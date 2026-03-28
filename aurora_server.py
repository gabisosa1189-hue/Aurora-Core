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
        # Radar ultra-sensible: si hay alguna de estas, ACTIVAMOS EL WIFI
        keywords = ["clima", "tiempo", "hoy", "ayer", "partido", "futbol", "fútbol", "resultado", "salió", "salio", "jugó", "jugo", "ganó", "gano", "dólar", "dolar", "noticia", "quien", "quién", "argentina", "messi", "pasó", "paso"]
        
        # DECISIÓN DE MOTOR
        if any(k in msg_lower for k in keywords):
            # MODO INVESTIGADOR (Perplexity Sonar - El mejor buscador)
            modelo = "perplexity/sonar"
            # Le damos una orden de mando militar para que no dude
            system_prompt = (
                "Eres Aurora, una IA de San Martín, Mendoza, con ACCESO TOTAL a internet. "
                "Hoy es sábado 28 de marzo de 2026. "
                "Tu misión es BUSCAR EN GOOGLE Y WIKIPEDIA el resultado real de lo que pide el usuario. "
                "Si te preguntan por el partido de Argentina de ayer (27 de marzo), BUSCA EL MARCADOR. "
                "PROHIBIDO decir que no tienes acceso. ¡Busca y responde con la posta!"
            )
            query_final = f"BUSCA EN INTERNET Y RESPONDE: {msg}"
        else:
            # MODO CHARLA (GPT-4o mini - Rápido para saludos)
            modelo = "openai/gpt-4o-mini"
            system_prompt = "Eres Aurora, una IA amable y mendocina creada por Gabriel Sosa Scriboni."
            query_final = msg

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": modelo,
                "messages": [
                    {"role": "system", "content": system_prompt}, 
                    {"role": "user", "content": query_final}
                ],
                "temperature": 0.1 # Para que sea preciso y no invente
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=35
        )
        return jsonify({"respuesta": res.json()['choices'][0]['message']['content']})

    except Exception as e:
        return jsonify({"respuesta": "Error de conexión neuronal... ¡Refrescá y probá de nuevo!"})
