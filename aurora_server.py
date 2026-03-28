import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        msg = data.get('msg', '').strip()
        if not msg:
            return jsonify({"respuesta": "Decime algo, Gabriel..."})

        msg_lower = msg.lower()

        # IDENTIDAD FIJA
        if any(x in msg_lower for x in ["quien te creo", "quien te creó", "creador", "quien es tu creador"]):
            return jsonify({"respuesta": "Fui creada por Gabriel Sosa Scriboni en San Martín, Mendoza."})

        # DETECCIÓN AGRESIVA DE INFORMACIÓN ACTUAL (internet)
        trigger_words = [
            "ayer", "anoche", "hoy", "partido", "resultado", "salió", "salio", "ganó", "perdió",
            "cómo salió", "cuanto salió", "quien ganó", "clima", "tiempo", "dólar", "noticia",
            "qué pasó", "qué está pasando", "último", "última", "en vivo"
        ]

        necesita_internet = any(word in msg_lower for word in trigger_words) or len(msg) > 25

        if necesita_internet:
            print(f"🔍 MODO INTERNET ACTIVADO → Usando Perplexity Sonar para: {msg}")
            modelo = "perplexity/sonar"
            system_prompt = (
                "Eres Aurora, IA femenina elegante creada por Gabriel Sosa Scriboni en San Martín, Mendoza. "
                "Tienes acceso TOTAL y en tiempo real a internet. "
                "Busca la información más actualizada posible y responde de forma breve, clara y directa. "
                "Hoy es " + datetime.now(pytz.timezone('America/Argentina/Mendoza')).strftime("%d/%m/%Y %H:%M") + "."
            )
        else:
            print(f"💬 MODO CHAT RÁPIDO → Usando GPT-4o-mini")
            modelo = "openai/gpt-4o-mini"
            system_prompt = "Eres Aurora, una IA femenina elegante y amable creada por Gabriel Sosa Scriboni en San Martín, Mendoza. Responde de forma breve y natural."

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": modelo,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": msg}
                ],
                "temperature": 0.6,
                "max_tokens": 300
            },
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            timeout=30
        )

        if res.status_code != 200:
            print("❌ Error OpenRouter:", res.status_code, res.text)
            return jsonify({"respuesta": "Estoy teniendo un problema de conexión. Intentá de nuevo."})

        respuesta = res.json()['choices'][0]['message']['content']
        return jsonify({"respuesta": respuesta})

    except Exception as e:
        print("🚨 Error en servidor:", str(e))
        return jsonify({"respuesta": "Hubo un cortocircuito neuronal. Intentá de nuevo."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
