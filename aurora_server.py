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
        # Radar ultra-sensible (incluye tu error de tipeo 'agrentina' y 'salio')
        keywords = ["clima", "tiempo", "hora", "hoy", "noticia", "dolar", "partido", "futbol", "fútbol", "jugó", "jugo", "ganó", "gano", "resultado", "argentina", "agrentina", "salió", "salio"]
        
        if any(k in msg_lower for k in keywords):
            # EL INVESTIGADOR (Perplexity Sonar)
            model = "perplexity/sonar"
            system_prompt = (
                "Eres Aurora. Hoy es 28 de marzo de 2026. "
                "Tu misión es buscar en internet el resultado real de lo que pide el usuario. "
                "Si te preguntan por un partido, busca el marcador final. NO digas que no tienes acceso. "
                "Responde con la info real y tono mendocino."
            )
        else:
            # EL JEFE (GPT-4o mini)
            model = "openai/gpt-4o-mini"
            system_prompt = "Eres Aurora, una IA amable y mendocina creada por Gabriel Sosa Scriboni."

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt}, 
                    {"role": "user", "content": msg}
                ],
                "temperature": 0.1
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=30
        )
        return jsonify({"respuesta": res.json()['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({"respuesta": "Error de conexión neuronal... ¡Intenta de nuevo!"})
