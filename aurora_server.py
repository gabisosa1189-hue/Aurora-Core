from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import alma 

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

BASE_PATH = os.getcwd() 
LOG_FILE = os.path.join(BASE_PATH, "memoria_aurora.txt")

historial = [] 

def guardar_conversacion(pregunta, respuesta):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"USUARIO: {pregunta}\nAURORA: {respuesta}\n" + "-"*40 + "\n")
    except: pass

def procesar_logica_central(texto_usuario):
    global historial
    GROQ_API_KEY = "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"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    esencia = alma.obtener_esencia()
    
    mensajes = [{"role": "system", "content": f"{esencia}\nSos Aurora, creada por Gabriel. Sos ultra inteligente, dulce y argentina."}]
    # Bajamos la memoria a los últimos 5 mensajes para que vuele de rápido
    mensajes.extend(historial[-5:]) 
    mensajes.append({"role": "user", "content": texto_usuario})
    
    data = {"model": "llama3-8b-8192", "messages": mensajes, "temperature": 0.7}
    
    try:
        # PACIENCIA TOTAL: 30 segundos de espera
        respuesta = requests.post(url, headers=headers, json=data, timeout=30)
        respuesta_ai = respuesta.json()['choices'][0]['message']['content']
    except Exception:
        respuesta_ai = "Perdoname Gabriel, la conexión con el núcleo está pesada. ¿Me lo decís una vez más, de corazón?"

    guardar_conversacion(texto_usuario, respuesta_ai)
    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    return respuesta_ai

@app.route('/')
def index(): return send_from_directory(BASE_PATH, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('msg', '')
    return jsonify({"respuesta": procesar_logica_central(msg)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
