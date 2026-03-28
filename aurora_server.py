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

# 3. El cerebro de Aurora
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        msg = data.get('msg', '').strip()
        if not msg: return jsonify({"respuesta": "Dime..."})
        
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "IA amable y mendocina creada por Gabriel Sosa Scriboni."}, 
                    {"role": "user", "content": msg}
                ]
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=15
        )
        return jsonify({"respuesta": res.json()['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({"respuesta": "Error de conexión."})
