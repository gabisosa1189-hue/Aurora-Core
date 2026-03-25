from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests # Lo usaremos para la API de alta velocidad

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
    # ¡Tu llave VIP ya está conectada!
    GROQ_API_KEY = "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"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. Le damos la personalidad a Aurora (System Prompt)
    mensajes = [{
        "role": "system", 
        "content": "Sos Aurora, una Inteligencia Artificial avanzada y amigable creada por Gabriel (un desarrollador de 21 años) en San Martín, Mendoza, Argentina. Respondés de forma concisa, útil y con un tono humano, usando español argentino neutro. Sos experta en ayudar y tenés muy buena onda."
    }]
    
    # 2. Sumamos la memoria de la charla y la nueva pregunta
    mensajes.extend(historial)
    mensajes.append({"role": "user", "content": texto_usuario})
    
    # 3. Configuramos el motor Llama 3 (Ultra rápido)
    data = {
        "model": "llama3-8b-8192", 
        "messages": mensajes,
        "temperature": 0.7
    }
    
    try:
        # Hacemos la llamada a la supercomputadora
        respuesta = requests.post(url, headers=headers, json=data)
        respuesta_json = respuesta.json()
        respuesta_ai = respuesta_json['choices'][0]['message']['content']
    except Exception as e:
        print("Error con la API:", e)
        respuesta_ai = "Perdón Gabriel, tuve un micro-corte con los servidores centrales. ¿Me repetís?"

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
    print("\n[SISTEMA] Memoria temporal reiniciada con éxito.")
    return jsonify({"status": "ok", "mensaje": "Historial borrado"})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("   AURORA CORE v7.0 - CLOUD READY")
    print("="*60 + "\n")
    # En la nube, Render nos dará el puerto automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)