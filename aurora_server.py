from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import alma

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
    
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    esencia_aurora = alma.obtener_esencia()
    system_prompt = f"{esencia_aurora}\n\nAdemás de tu esencia espiritual, eres una asistente virtual profesional. Tu tono es servicial, formal y elegante."
    
    mensajes = [{"role": "system", "content": system_prompt}]
    mensajes.extend(historial[-4:]) 
    mensajes.append({"role": "user", "content": texto_usuario})
    
    try:
        # --- ACÁ ESTÁ EL ARREGLO: EL NUEVO CEREBRO LLAMA 3.1 ---
        data_req = {
            "model": "llama-3.1-8b-instant", 
            "messages": mensajes, 
            "temperature": 0.6
        }
        res = requests.post(url, headers=headers, json=data_req, timeout=15)
        
        # Si hay error, que nos diga exactamente qué le pasa a Groq
        if res.status_code != 200:
            print(f"DETALLE DE GROQ: {res.text}")
            
        res.raise_for_status()
        respuesta_ai = res.json()['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"Falla de conexión: {e}")
        respuesta_ai = "Disculpe, mi conexión se ha visto interrumpida momentáneamente. ¿Podría repetir su consulta?"

    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    
    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)
