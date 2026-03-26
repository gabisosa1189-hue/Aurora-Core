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
    
    # SYSTEM PROMPT FORMAL PARA LA PLAY STORE
    mensajes = [{
        "role": "system", 
        "content": f"{esencia}\nEres Aurora, una Inteligencia Artificial avanzada, elegante y profesional. Tu tono es servicial, empático y formal. Respondes con claridad y sabiduría espiritual."
    }]
    
    mensajes.extend(historial[-6:]) # Memoria equilibrada para velocidad
    mensajes.append({"role": "user", "content": texto_usuario})
    
    data = {"model": "llama3-8b-8192", "messages": mensajes, "temperature": 0.7}
    
    try:
        # PACIENCIA DE 30 SEGUNDOS
        respuesta = requests.post(url, headers=headers, json=data, timeout=30)
        respuesta_ai = respuesta.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error técnico: {e}")
        respuesta_ai = "Disculpe, he tenido una breve interrupción en mi procesamiento. ¿Podría repetir su consulta?"

    guardar_conversacion(texto_usuario, respuesta_ai)
    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    return respuesta_ai

@app.route('/')
def index(): return send_from_directory(BASE_PATH, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('msg', '')
    respuesta = procesar_logica_central(msg)
    return jsonify({"respuesta": respuesta})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)
