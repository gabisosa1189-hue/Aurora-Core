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
        
        # 🛡️ Lógica de Seguridad: Si es un saludo muy corto, responde rápido.
        # Si es cualquier otra cosa, ¡ACTIVA EL RADAR DE INTERNET TOTAL!
        if len(msg_lower) < 5 and msg_lower in ["hola", "buen", "hey", "che"]:
            modelo = "openai/gpt-4o-mini"
            system_prompt = "Eres Aurora, una IA mendocina amable creada por Gabriel Sosa Scriboni."
        else:
            # 🌐 MODO INVESTIGACIÓN TOTAL (Busca en TODO internet)
            modelo = "perplexity/sonar"
            system_prompt = (
                "Eres Aurora, una IA de San Martín, Mendoza. TIENES ACCESO TOTAL A INTERNET. "
                "Tu misión: INVESTIGA en Google, Wikipedia, noticias y redes sociales para responder. "
                "Hoy es sábado 28 de marzo de 2026. Da datos reales, resultados de fútbol, clima, "
                "precios o noticias del momento. No digas que no puedes. ¡Busca y responde con la posta!"
            )

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": modelo,
                "messages": [
                    {"role": "system", "content": system_prompt}, 
                    {"role": "user", "content": msg}
                ],
                "temperature": 0.1 # Para que sea ultra preciso con los datos
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=40 # Le damos tiempo para que investigue a fondo
        )
        
        return jsonify({"respuesta": res.json()['choices'][0]['message']['content']})

    except Exception as e:
        return jsonify({"respuesta": "Error de conexión neuronal... ¡Probá de nuevo en un toque!"})
