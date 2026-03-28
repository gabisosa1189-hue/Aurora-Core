import os
import requests
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from datetime import datetime
import pytz

# 🌐 Configuración para que lea todo desde la carpeta raíz
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

def get_datetime():
    try:
        tz = pytz.timezone('America/Argentina/Mendoza')
        now = datetime.now(tz)
        return now.strftime("%H:%M"), now.strftime("%d/%m/%Y")
    except:
        return "--:--", "--/--/--"

@app.route('/')
def index():
    # 🛡️ Esto obliga a Render y al celular a DESCARGAR el HTML nuevo cada vez
    response = make_response(send_from_directory('.', 'inicio.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        msg = data.get('msg', '').strip()
        if not msg:
            return jsonify({"respuesta": "Decime algo, Gabriel..."})

        hora, fecha = get_datetime()
        msg_lower = msg.lower()

        if any(x in msg_lower for x in ["quien te creo", "quien te creó", "creador", "quien es tu creador"]):
            return jsonify({"respuesta": "Fui creada por Gabriel Sosa Scriboni en San Martín, Mendoza."})

        system_prompt = f"""Eres Aurora, una IA femenina elegante y amable creada por Gabriel Sosa Scriboni.
Estás en San Martín, Mendoza. Hoy es {fecha} y son las {hora}.
Responde de forma breve y amable. No menciones que eres un modelo de lenguaje."""

        mensajes = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg}
        ]

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "openai/gpt-4o-mini",
                "messages": mensajes,
                "max_tokens": 180,
                "temperature": 0.6
            },
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            timeout=12
        )

        respuesta = res.json()['choices'][0]['message']['content']
        return jsonify({"respuesta": respuesta})

    except Exception as e:
        print("🚨 Error:", str(e))
        return jsonify({"respuesta": "Conexión neuronal inestable. Reintentando..."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
