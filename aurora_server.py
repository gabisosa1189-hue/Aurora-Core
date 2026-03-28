import os
import requests
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

# Log para saber si la clave está cargada
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

        # IDENTIDAD FIJA
        if any(x in msg_lower for x in ["quien te creo", "quien te creó", "creador", "quien es tu creador"]):
            return jsonify({"respuesta": "Fui creada por Gabriel Sosa Scriboni en San Martín, Mendoza."})

        system_prompt = f"""Eres Aurora, una IA femenina elegante y amable creada por Gabriel Sosa Scriboni en San Martín, Mendoza.
Hoy es {fecha} y son las {hora}.
Responde de forma breve, clara y cálida."""

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
                "temperature": 0.65
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
        print("🚨 Error en /chat:", str(e))
        return jsonify({"respuesta": "Hubo un cortocircuito. Intentá de nuevo por favor."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Servidor corriendo en puerto {port}")
    app.run(host='0.0.0.0', port=port)
