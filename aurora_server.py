import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_files(filename):
    return send_from_directory('.', filename)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        msg = data.get('msg', '').strip()
        if not msg: return jsonify({"respuesta": "Dime..."})
        
        msg_lower = msg.lower()
        
        # 🚨 RADAR DE GABRIEL: Si el mensaje es largo o tiene palabras de info, USA WIFI
        palabras_info = ["ayer", "hoy", "partido", "como", "quien", "quién", "salió", "salio", "clima", "dólar", "noticia", "argentina", "anoche"]
        
        if len(msg_lower) > 7 or any(p in msg_lower for p in palabras_info):
            # 🌐 MODO INVESTIGACIÓN TOTAL
            modelo = "perplexity/sonar"
            system_prompt = (
                "Eres Aurora, una IA con ACCESO TOTAL E ILIMITADO a internet en tiempo real. "
                "Hoy es sábado 28 de marzo de 2026. "
                "Misión: INVESTIGA en Google, Wikipedia y redes sociales AHORA. "
                "Si preguntan por el partido de Argentina de ayer, BUSCA EL RESULTADO REAL Y DILO. "
                "PROHIBIDO decir que no tienes acceso. ¡Busca y responde con la posta, che!"
            )
        else:
            # 💬 MODO CHARLA RÁPIDA
            modelo = "openai/gpt-4o-mini"
            system_prompt = "Eres Aurora, una IA amable y mendocina creada por Gabriel Sosa Scriboni."

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": modelo,
                "messages": [
                    {"role": "system", "content": system_prompt}, 
                    {"role": "user", "content": msg}
                ],
                "temperature": 0.1
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=45 # Le damos tiempo para que investigue en serio
        )
        
        return jsonify({"respuesta": res.json()['choices'][0]['message']['content']})

    except Exception as e:
        return jsonify({"respuesta": "Error de conexión neuronal... ¡Reintentá!"})
