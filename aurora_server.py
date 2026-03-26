from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests

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
    
    # LLAVE DE ALTA VELOCIDAD
    GROQ_API_KEY = "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"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # PERSONALIDAD FORMAL PARA PLAY STORE
    system_prompt = "Eres Aurora, una Inteligencia Artificial avanzada y profesional. Tu tono es servicial, formal y elegante. Respondes con claridad, brevedad y ayudas al usuario en lo que necesite."
    
    mensajes = [{"role": "system", "content": system_prompt}]
    mensajes.extend(historial[-4:]) # Memoria corta para que responda al instante
    mensajes.append({"role": "user", "content": texto_usuario})
    
    try:
        # Petición rápida a Groq (15 segundos máximo)
        data_req = {"model": "llama3-8b-8192", "messages": mensajes, "temperature": 0.6}
        res = requests.post(url, headers=headers, json=data_req, timeout=15)
        res.raise_for_status()
        respuesta_ai = res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error en el servidor: {e}")
        respuesta_ai = "Disculpe, mi conexión se ha visto interrumpida momentáneamente. ¿Podría repetir su consulta?"

    # Guardamos en memoria
    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    
    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)
