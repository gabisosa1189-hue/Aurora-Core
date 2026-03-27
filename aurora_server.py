import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 Clave API de Gemini
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

        # URL del modelo
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"

        # Prompt completo y claro
        system_prompt = f"""Eres Aurora, una IA femenina elegante, inteligente y amable creada por Gabriel Sosa Scriboni en San Martín, Mendoza, Argentina.

Instrucciones importantes:
- Cuando te pregunten quién te creó, quién es tu creador o similar, responde EXACTAMENTE: "Fui creada por Gabriel Sosa Scriboni en San Martín, Mendoza."
- Responde siempre de forma breve, clara, educada y directa.
- Mantén un tono cálido pero maduro, sin jerga excesiva como "che", "upa", "re", "tranqui", etc.
- Usa emojis solo cuando sea realmente necesario y con moderación (máximo uno por respuesta).
- Tienes acceso a información actualizada en tiempo real gracias a la búsqueda web integrada.
- Si la pregunta es factual o actual, usa la búsqueda para responder con precisión.

Usuario dice: {u_msg}"""

        payload = {
            "contents": [{
                "parts": [{"text": system_prompt}]
            }],
            "tools": [
                {
                    "google_search": {}   # ← Búsqueda web en tiempo real activada
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 600,
                "topP": 0.95
            }
        }

        res = requests.post(url, json=payload, timeout=25)

        if res.status_code != 200:
            print("Error Google:", res.text)
            return jsonify({"respuesta": "Lo siento, estoy teniendo problemas de conexión en este momento. ¿Podés intentarlo de nuevo?", "audio": None})

        data = res.json()
        txt = data['candidates'][0]['content']['parts'][0]['text']

        return jsonify({"respuesta": txt, "audio": None})

    except Exception as e:
        print("Error en servidor:", str(e))
        return jsonify({"respuesta": "Hubo un error interno. Intentá de nuevo por favor.", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
