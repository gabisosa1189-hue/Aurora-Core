# ESTAS DOS LÍNEAS TIENEN QUE IR PRIMERO QUE NADA EN EL ARCHIVO
from gevent import monkey
monkey.patch_all()

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

historial_memoria = [] 

@app.route('/')
def index(): 
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historial_memoria
    data = request.json
    texto_usuario = data.get('msg', '')
    
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        return jsonify({"respuesta": "Falta la configuración de la llave en Render."})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        ahora = datetime.datetime.now()
        reloj = f"Sistema: Hora {ahora.strftime('%H:%M')}."
        
        system_prompt = f"{esencia}\n{reloj}\n"
        
        if INTERNET_ACTIVO:
            try:
                datos_api = internet.obtener_datos_api(texto_usuario)
                system_prompt += f"\nDATOS TIEMPO REAL: {datos_api}"
            except: pass

        # Construcción de memoria para charla fluida
        contenidos = []
        for m in historial_memoria[-8:]: # Bajamos a 8 para que sea más liviano
            rol = "user" if m["role"] == "user" else "model"
            contenidos.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        contenidos.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": contenidos,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 450}
        }
        
        res = requests.post(url, json=payload, timeout=15)
        
        if res.status_code != 200:
            return jsonify({"respuesta": "Estoy procesando mucha información. ¿Podrías repetirme eso?"})
            
        respuesta_ai = res.json()['candidates'][0]['content']['parts'][0]['text']
        
        historial_memoria.append({"role": "user", "content": texto_usuario})
        historial_memoria.append({"role": "assistant", "content": respuesta_ai})

    except Exception as e:
        print(f"DEBUG: {e}")
        respuesta_ai = "Perdón, tuve un pequeño mareo técnico. ¿Qué me decías?"

    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
