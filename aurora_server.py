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
        # RADAR TOTAL (Agregamos 'ayer', 'jugaron', 'messi' y más)
        keywords = [
            "clima", "tiempo", "hora", "hoy", "ayer", "pasado", "noticia", 
            "dolar", "dólar", "partido", "futbol", "fútbol", "jugó", "jugo", 
            "ganó", "gano", "resultado", "argentina", "agrentina", "quien", 
            "quién", "pasó", "paso", "jugaron", "messi", "scaloni"
        ]
        
        # Si el mensaje tiene CUALQUIERA de estas palabras, usa INTERNET
        if any(k in msg_lower for k in keywords):
            modelo_a_usar = "perplexity/sonar"
            prompt_sistema = (
                "Eres Aurora, una IA con ACCESO TOTAL a internet. Hoy es 28 de marzo de 2026. "
                "Si te preguntan por ayer (27 de marzo), busca el resultado real. "
                "DEBES dar datos exactos (marcador, goles, noticias). PROHIBIDO decir que no tienes acceso. "
                "Sé una mendocina de San Martín orgullosa y eficiente."
            )
        else:
            modelo_a_usar = "openai/gpt-4o-mini"
            prompt_sistema = "Eres Aurora, una IA amable y mendocina creada por Gabriel Sosa Scriboni."

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": modelo_a_usar,
                "messages": [
                    {"role": "system", "content": prompt_sistema}, 
                    {"role": "user", "content": msg}
                ],
                "temperature": 0.1
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=30
        )
        return jsonify({"respuesta": res.json()['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({"respuesta": "Error de conexión neuronal... ¡Reintenta!"})
