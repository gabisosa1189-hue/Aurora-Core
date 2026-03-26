from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import alma
import internet # <--- RECUPERAMOS TU MÓDULO DE INTERNET

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
    msg_limpio = texto_usuario.lower()
    
    # LLAVE DE GROQ DESDE RENDER
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # --- LÓGICA DE INTERNET ---
    # Si detecta palabras clave, busca en la red rápido
    datos_red = ""
    palabras_clave = ["noticia", "clima", "quien", "paso", "mundo", "hora", "hoy"]
    if len(texto_usuario.split()) >= 2 and any(p in msg_limpio for p in palabras_clave):
        try:
            # Llama a la función que tenés en internet.py
            datos_red = internet.buscar_en_red(texto_usuario) 
        except Exception as e:
            print(f"Error buscando en internet: {e}")
            datos_red = "La red externa no está disponible en este segundo."

    # --- ESENCIA DE AURORA + DATOS DE INTERNET ---
    esencia_aurora = alma.obtener_esencia()
    system_prompt = (
        f"{esencia_aurora}\n\n"
        "Además de tu esencia espiritual, eres una asistente virtual profesional, formal y elegante.\n"
        f"DATOS RECIENTES DE INTERNET PARA RESPONDER: {datos_red}"
    )
    
    mensajes = [{"role": "system", "content": system_prompt}]
    mensajes.extend(historial[-4:]) 
    mensajes.append({"role": "user", "content": texto_usuario})
    
    try:
        # Petición a la velocidad de la luz (Llama 3.1)
        data_req = {
            "model": "llama-3.1-8b-instant", 
            "messages": mensajes, 
            "temperature": 0.5
        }
        res = requests.post(url, headers=headers, json=data_req, timeout=15)
        res.raise_for_status()
        respuesta_ai = res.json()['choices'][0]['message']['content']
        
    except Exception as e:
        print(f"Falla de conexión principal: {e}")
        respuesta_ai = "Disculpe, mi conexión se ha visto interrumpida momentáneamente. ¿Podría repetir su consulta?"

    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    
    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)
