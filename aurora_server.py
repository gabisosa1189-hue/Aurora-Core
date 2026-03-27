from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

# ESTA RUTA ES LA QUE SIRVE EL VIDEO SÍ O SÍ
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        api_key = os.environ.get("GEMINI_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        payload = {"contents": [{"role": "user", "parts": [{"text": u_msg}]}]}
        res = requests.post(url, json=payload, timeout=10)
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"respuesta": txt})
    except:
        return jsonify({"respuesta": "Aurora reconectando..."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
