import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

# 1. Esto muestra tu página principal
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# 2. Esto permite que se cargue el fondo.mp4 y las fotos
@app.route('/<path:filename>')
def serve_files(filename):
    return send_from_directory('.', filename)

# 3. El cerebro de Aurora (AHORA CON DOS MOTORES)
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        msg = data.get('msg', '').strip()
        if not msg: return jsonify({"respuesta": "Dime..."})
        
        # --- EL RUTEADOR NEURONAL DE GABRIEL ---
        msg_minusculas = msg.lower()
        # Si el mensaje tiene alguna de estas palabras, usamos internet
        palabras_clave = ["clima", "tiempo", "hora", "noticia", "hoy", "precio", "dólar", "dolar", "internet", "actual", "busca"]
        
        necesita_internet = any(palabra in msg_minusculas for palabra in palabras_clave)
        
        if necesita_internet:
            # EL INVESTIGADOR (Lento pero con Google)
            modelo_a_usar = "perplexity/llama-3.1-sonar-small-128k-online"
            prompt_sistema = "Eres Aurora, una IA mendocina. Responde con los datos actuales de internet de forma amable y directa."
        else:
            # EL JEFE (Rápido y conversacional)
            modelo_a_usar = "openai/gpt-4o-mini"
            prompt_sistema = "IA amable y mendocina creada por Gabriel Sosa Scriboni."
        # ----------------------------------------
        
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": modelo_a_usar,
                "messages": [
                    {"role": "system", "content": prompt_sistema}, 
                    {"role": "user", "content": msg}
                ]
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=20 # Le damos un poquito más de tiempo por si busca en internet
        )
        return jsonify({"respuesta": res.json()['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({"respuesta": "Error de conexión neuronal..."})
