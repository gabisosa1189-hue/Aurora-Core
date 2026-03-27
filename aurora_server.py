from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

# Intentamos cargar internet.py si existe para las búsquedas
try:
    import internet
    INTERNET_ACTIVO = True
except:
    INTERNET_ACTIVO = False

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Memoria de la charla (Para que Aurora no sea "olvidadiza")
historial_memoria = [] 

@app.route('/')
def index(): 
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historial_memoria
    data = request.json
    texto_usuario = data.get('msg', '')
    
    # Buscamos la llave de Google en Render
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        return jsonify({"respuesta": "Falta la llave GEMINI_API_KEY en Render."})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        reloj = f"Sistema: Hora actual {datetime.datetime.now().strftime('%H:%M')}."
        system_prompt = f"{esencia}\n{reloj}\n"
        
        if INTERNET_ACTIVO:
            try:
                datos_api = internet.obtener_datos_api(texto_usuario)
                system_prompt += f"\nDATOS TIEMPO REAL: {datos_api}"
            except: pass

        # Construcción de la memoria (Últimos 6 mensajes)
        contenidos = []
        for m in historial_memoria[-6:]:
            rol = "user" if m["role"] == "user" else "model"
            contenidos.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        contenidos.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": contenidos,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 450}
        }
        
        # Llamada directa y estable a Google
        res = requests.post(url, json=payload, timeout=15)
        res.raise_for_status()
        
        respuesta_ai = res.json()['candidates'][0]['content']['parts'][0]['text']
        
        # Guardamos en la memoria para que la charla fluya
        historial_memoria.append({"role": "user", "content": texto_usuario})
        historial_memoria.append({"role": "assistant", "content": respuesta_ai})

    except Exception as e:
        print(f"ERROR: {e}")
        respuesta_ai = "Perdón, tuve un pequeño problema de conexión. ¿Me repetís eso?"

    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
