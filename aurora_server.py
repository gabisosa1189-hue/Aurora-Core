from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

try:
    import internet
    INTERNET_ACTIVO = True
except:
    INTERNET_ACTIVO = False

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

BASE_PATH = os.getcwd() 
historial = [] 

@app.route('/')
def index(): 
    return send_from_directory(BASE_PATH, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historial
    data = request.json
    texto_usuario = data.get('msg', '')
    
    # BUSCAMOS LA LLAVE NUEVA
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        return jsonify({"respuesta": "ERROR: No configuraste GEMINI_API_KEY en Render."})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    try:
        reloj = f"Sistema: Hora actual {datetime.datetime.now().strftime('%H:%M')}."
        esencia = alma.obtener_esencia()
        system_prompt = f"{esencia}\n{reloj}\n"
        
        if INTERNET_ACTIVO:
            datos_api = internet.obtener_datos_api(texto_usuario)
            system_prompt += f"\nDATOS TIEMPO REAL: {datos_api}"

        # Formato de Google
        contenidos = []
        for m in historial[-6:]:
            rol = "user" if m["role"] == "user" else "model"
            contenidos.append({"role": rol, "parts": [{"text": m["content"]}]})
        contenidos.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": contenidos,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 450}
        }
        
        res = requests.post(url, json=payload, timeout=15)
        
        # Si Google nos da error, lo mostramos para arreglarlo
        if res.status_code != 200:
            return jsonify({"respuesta": f"Error de Google: {res.status_code}. Revisa tu API Key."})
            
        respuesta_ai = res.json()['candidates'][0]['content']['parts'][0]['text']
        
    except Exception as e:
        respuesta_ai = "Disculpe, mi red se saturó un segundo. ¿Podemos retomar?"

    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
