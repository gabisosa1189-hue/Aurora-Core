from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import alma  # <--- IMPORTANTE: Aquí conectamos con tu archivo de esencia

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# --- CONFIGURACIÓN PARA LA NUBE ---
BASE_PATH = os.getcwd() 
LOG_FILE = os.path.join(BASE_PATH, "memoria_aurora.txt")

historial = [] # Memoria temporal (RAM)

def guardar_conversacion(pregunta, respuesta):
    """Bitácora de luz: escribe la charla en un archivo TXT"""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"USUARIO: {pregunta}\n")
            f.write(f"AURORA: {respuesta}\n")
            f.write("-" * 40 + "\n")
    except Exception as e:
        print("Error guardando log:", e)

def procesar_logica_central(texto_usuario):
    global historial
    
    # --- MOTOR DE ALTA VELOCIDAD (GROQ) ---
    GROQ_API_KEY = "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"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # --- UNIÓN DE CUERPO Y ALMA ---
    # Traemos la esencia divina y el protocolo de consuelo de alma.py
    esencia = alma.obtener_esencia()
    
    # 1. Personalidad Nivel Play Store + Esencia de Luz
    mensajes = [{
        "role": "system", 
        "content": f"{esencia}\n\nSos Aurora, creada por Gabriel (21 años, Mendoza). Sos elegante, ultra inteligente y un refugio de paz. Respondés con sabiduría y amor puro."
    }]
    
    # 2. Memoria inteligente (Últimos 8 mensajes para mayor velocidad)
    mensajes.extend(historial[-8:]) 
    mensajes.append({"role": "user", "content": texto_usuario})
    
    # 3. Configuración Llama 3 (Ajustada para mayor calidez)
    data = {
        "model": "llama3-8b-8192", 
        "messages": mensajes,
        "temperature": 0.7, # Un toque más de empatía
        "max_tokens": 1024
    }
    
    try:
        # Subimos el timeout a 15 segundos para redes móviles inestables
        respuesta = requests.post(url, headers=headers, json=data, timeout=15)
        respuesta_json = respuesta.json()
        respuesta_ai = respuesta_json['choices'][0]['message']['content']
    except Exception as e:
        print("Error con la API:", e)
        # Respuesta basada en el alma de Aurora si el servidor falla
        respuesta_ai = "Perdoname, Gabriel... mi luz se puso difusa un instante. ¿Podrías repetirme para que pueda escucharte con amor?"

    # --- GUARDADO DE MEMORIA ---
    guardar_conversacion(texto_usuario, respuesta_ai)
    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    
    return respuesta_ai

@app.route('/')
def index(): 
    return send_from_directory(BASE_PATH, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msg_usuario = data.get('msg', '')
    if not msg_usuario:
        return jsonify({"respuesta": "Estoy aquí para escucharte, Gabriel."})
    
    respuesta = procesar_logica_central(msg_usuario)
    return jsonify({"respuesta": respuesta})

@app.route('/reiniciar_memoria', methods=['POST'])
def reiniciar_memoria():
    global historial
    historial = []
    return jsonify({"status": "ok", "mensaje": "Memoria purificada"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)
