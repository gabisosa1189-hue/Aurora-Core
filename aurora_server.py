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
        # Radar ampliado: si detecta cualquier cosa de actualidad, activa el modo BUSCADOR
        keywords = ["clima", "tiempo", "hora", "hoy", "noticia", "dolar", "dólar", "partido", "futbol", "fútbol", "jugó", "jugo", "ganó", "gano", "resultado", "argentina", "quien", "quién", "pasó", "paso"]
        
        if any(k in msg_lower for k in keywords):
            # MODO INVESTIGADOR: Perplexity Sonar (Es el que usa Wikipedia y Google en tiempo real)
            modelo_a_usar = "perplexity/sonar"
            prompt_sistema = (
                "ACTÚA COMO UN BUSCADOR EN TIEMPO REAL. Hoy es sábado 28 de marzo de 2026. "
                "Tu misión es buscar en Wikipedia, noticias y buscadores el resultado exacto. "
                "Si preguntan por fútbol, da el marcador y quién hizo los goles. "
                "Responde con la info real, no digas que eres una IA sin acceso. ¡Sé directa y mendocina!"
            )
        else:
            # MODO CHARLA: El modelo rápido para cuando solo saludas
            modelo_a_usar = "openai/gpt-4o-mini"
            prompt_sistema = "Eres Aurora, una IA amable y mendocina creada por Gabriel Sosa Scriboni de San Martín."

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": modelo_a_usar,
                "messages": [
                    {"role": "system", "content": prompt_sistema}, 
                    {"role": "user", "content": msg}
                ],
                "temperature": 0.1 # Para que no invente y sea preciso
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=30
        )
        return jsonify({"respuesta": res.json()['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({"respuesta": "Error de conexión neuronal... ¡Refrescá y probá de nuevo!"})
