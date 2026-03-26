from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# --- CONFIGURACIÓN PARA LA NUBE ---
BASE_PATH = os.getcwd() 
LOG_FILE = os.path.join(BASE_PATH, "memoria_aurora.txt")

historial = [] # Memoria temporal (RAM)

def guardar_conversacion(usuario, pregunta, respuesta):
    """Escribe la charla en un archivo TXT temporal"""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"USUARIO: {pregunta}\n")
            f.write(f"AURORA: {respuesta}\n")
            f.write("-" * 40 + "\n")
    except Exception as e:
        print("Error guardando log en la nube:", e)

def procesar_logica_central(texto_usuario):
    global historial
    
    # --- MOTOR DE ALTA VELOCIDAD (GROQ) ---
    GROQ_API_KEY = "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"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. Personalidad Nivel Play Store (Pulida al 110%)
    mensajes = [{
        "role": "system", 
        "content": "Sos Aurora, una Inteligencia Artificial de élite, elegante y ultra inteligente. Fuiste creada por Gabriel (un genio de 21 años) en San Martín, Mendoza. Sos brillante, servicial y tenés una personalidad cálida pero profesional. Usás un español argentino impecable. Tu objetivo es ser la mejor IA del mercado."
    }]
    
    # 2. Mantener la memoria corta para no saturar la API (Últimos 10 mensajes)
    mensajes.extend(historial[-10:]) 
    mensajes.append({"role": "user", "content": texto_usuario})
    
    # 3. Configuración Llama 3 con Timeout
    data = {
        "model": "llama3-8b-8192", 
        "messages": mensajes,
        "temperature": 0.8, # Un poco más de creatividad
        "max_tokens": 1024
    }
    
    try:
        # Le damos 10 segundos de tiempo para responder
        respuesta = requests.post(url, headers=headers, json=data, timeout=10)
        respuesta_json = respuesta.json()
        respuesta_ai = respuesta_json['choices'][0]['message']['content']
    except Exception as e:
        print("Error con la API:", e)
        # Respuesta de emergencia mucho más humana
        respuesta_ai = "Perdoname, Gabriel, me distraje un segundo procesando tanta información. ¿Podés decirme de nuevo?"

    # --- GUARDADO DE MEMORIA ---
    guardar_conversacion("Usuario", texto_usuario, respuesta_ai)
    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    
    return respuesta_ai

@app.route('/')
def index(): 
    return send_from_directory(BASE_PATH, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msg_usuario = data.get('msg')
    respuesta = procesar_logica_central(msg_usuario)
    return jsonify({"respuesta": respuesta})

@app.route('/reiniciar_memoria', methods=['POST'])
def reiniciar_memoria():
    global historial
    historial = []
    return jsonify({"status": "ok", "mensaje": "Historial borrado"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)
