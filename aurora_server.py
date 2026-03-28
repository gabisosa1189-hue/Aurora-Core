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
        # Radar ultra-sensible para activar el WiFi
        keywords = ["clima", "tiempo", "hora", "hoy", "noticia", "dolar", "dólar", "partido", "futbol", "fútbol", "jugó", "jugo", "ganó", "gano", "resultado", "quien", "quién"]
        
        if any(k in msg_lower for k in keywords):
            # EL INVESTIGADOR (Perplexity Sonar - El mejor buscador)
            modelo_a_usar = "perplexity/sonar"
            prompt_sistema = (
                "Eres Aurora, una IA con ACCESO TOTAL Y OBLIGATORIO a internet en tiempo real. "
                "Hoy es sábado 28 de marzo de 2026. Tu misión es buscar en Google/Bing AHORA MISMO "
                "y dar el resultado exacto de lo que pide el usuario (partidos, clima, etc). "
                "PROHIBIDO decir que no tienes acceso. Busca y responde como una mendocina de San Martín."
            )
        else:
            # EL JEFE (GPT-4o mini - El más rápido para charlar)
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
                "temperature": 0.1 # Baja temperatura para que sea más preciso y menos 'chamuyero'
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=30
        )
        respuesta_final = res.json()['choices'][0]['message']['content']
        return jsonify({"respuesta": respuesta_final})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"respuesta": "Error de conexión neuronal... Intentá de nuevo en un segundo."})
