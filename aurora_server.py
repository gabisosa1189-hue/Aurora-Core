import os
import requests
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_API_KEY")

print("🚀 Servidor iniciado - OPENROUTER_KEY:", "✅ OK" if OPENROUTER_KEY else "❌ FALTA")

def get_datetime():
    try:
        tz = pytz.timezone('America/Argentina/Mendoza')
        now = datetime.now(tz)
        return now.strftime("%H:%M"), now.strftime("%d/%m/%Y")
    except:
        return "--:--", "--/--/--"

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        msg = data.get('msg', '').strip()
        if not msg:
            return jsonify({"respuesta": "Decime algo..."})

        hora, fecha = get_datetime()
        msg_lower = msg.lower()

        # IDENTIDAD FIJA
        if any(x in msg_lower for x in ["quien te creo", "quien te creó", "creador", "quien es tu creador"]):
            return jsonify({"respuesta": "Fui creada por Gabriel Sosa Scriboni en San Martín, Mendoza."})

        # Prompt simple y estable
        system_prompt = f"""Eres Aurora, una IA femenina elegante creada por Gabriel Sosa Scriboni en San Martín, Mendoza.
Hoy es {fecha} y son las {hora}.
Responde de forma breve, clara y amable."""

        mensajes = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg}
        ]

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "openai/gpt-4o-mini",
                "messages": mensajes,
                "max_tokens": 200,
                "temperature": 0.6
            },
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            timeout=12
        )

        if res.status_code != 200:
            print("❌ Error OpenRouter:", res.status_code, res.text)
            return jsonify({"respuesta": "Estoy teniendo un problema de conexión. Intentá de nuevo."})

        respuesta = res.json()['choices'][0]['message']['content']
        return jsonify({"respuesta": respuesta})

    except Exception as e:
        print("🚨 ERROR en /chat:", str(e))
        return jsonify({"respuesta": "Hubo un error interno. Intentá de nuevo."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Iniciando en puerto {port}")
    app.run(host='0.0.0.0', port=port)
