from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import datetime
import alma

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
    
    # BUSCAMOS LA LLAVE
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        return jsonify({"respuesta": "Error: No encontré la llave GEMINI_API_KEY en Render."})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    try:
        zona_ar = datetime.timezone(datetime.timedelta(hours=-3))
        ahora = datetime.datetime.now(zona_ar)
        reloj = f"Sistema: Hoy es {ahora.strftime('%d/%m/%Y')} y la hora es {ahora.strftime('%H:%M')}."
    except:
        reloj = ""

    esencia = alma.obtener_esencia()
    system_prompt = f"{esencia}\n{reloj}\n"
    
    if INTERNET_ACTIVO:
        try:
            datos_api = internet.obtener_datos_api(texto_usuario)
            system_prompt += f"\n--- DATOS EN TIEMPO REAL ---\n{datos_api}\n"
        except: pass

    # Formato obligatorio para Google Gemini
    contenidos = []
    for msg in historial[-6:]:
        rol = "user" if msg["role"] == "user" else "model"
        contenidos.append({"role": rol, "parts": [{"text": msg["content"]}]})
    
    contenidos.append({"role": "user", "parts": [{"text": texto_usuario}]})

    payload = {
        "contents": contenidos,
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 400}
    }
    
    try:
        res = requests.post(url, json=payload, timeout=20)
        res.raise_for_status()
        respuesta_ai = res.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        respuesta_ai = "Disculpe, mi red se saturó un segundo. ¿Podemos retomar?"

    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    
    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)
