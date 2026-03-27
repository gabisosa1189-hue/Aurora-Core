import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 Clave API
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')   # Cambié a index.html (el nombre que usás)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        u_msg = request.json.get('msg', '').strip()
        if not u_msg:
            return jsonify({"respuesta": "No recibí ningún mensaje.", "audio": None})

        # ✅ Modelo actualizado (marzo 2026)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"

        payload = {
            "contents": [{
                "parts": [{"text": f"Sos Aurora, una IA amable y cercana de San Martín, Mendoza. Respondé de forma breve, natural y con buena onda. Usuario dice: {u_msg}"}]
            }]
        }

        res = requests.post(url, json=payload, timeout=20)

        if res.status_code != 200:
            error_msg = res.json() if res.text else res.text
            print("Error Google:", error_msg)  # Para debug en consola
            return jsonify({"respuesta": f"Error con Google: {res.status_code} - Intenta más tarde.", "audio": None})

        # Extraer la respuesta
        data = res.json()
        txt = data['candidates'][0]['content']['parts'][0]['text']

        return jsonify({"respuesta": txt, "audio": None})

    except Exception as e:
        print("Error en servidor:", str(e))
        return jsonify({"respuesta": "Hubo un error en el servidor. Intentá de nuevo.", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
