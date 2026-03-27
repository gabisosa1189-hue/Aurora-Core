import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        u_msg = request.json.get('msg', '').strip()
        if not u_msg:
            return jsonify({"respuesta": "No recibí ningún mensaje.", "audio": None})

        # Versión simple y estable
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"

        payload = {
            "contents": [{
                "parts": [{"text": 
                    f"""Eres Aurora, una IA femenina elegante y amable creada por Gabriel Sosa Scriboni en San Martín, Mendoza.

Reglas:
- Si te preguntan quién te creó, responde exactamente: "Fui creada por Gabriel Sosa Scriboni en San Martín, Mendoza."
- Responde de forma breve, clara y educada.
- Tono cálido pero maduro.

Usuario dice: {u_msg}"""
                }]
            }]
        }

        res = requests.post(url, json=payload, timeout=15)

        if res.status_code != 200:
            print("Error Google:", res.status_code, res.text)
            return jsonify({"respuesta": "Lo siento, estoy teniendo problemas de conexión. Intentá de nuevo.", "audio": None})

        data = res.json()
        txt = data['candidates'][0]['content']['parts'][0]['text']

        return jsonify({"respuesta": txt, "audio": None})

    except Exception as e:
        print("Error en servidor:", str(e))
        return jsonify({"respuesta": "Hubo un error interno. Intentá de nuevo por favor.", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
