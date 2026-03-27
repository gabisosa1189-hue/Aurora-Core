from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

# Esta ruta entrega el video fondo.mp4 y cualquier otro archivo
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        api_key = os.environ.get("GEMINI_API_KEY")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"Eres Aurora, una IA de Mendoza. Usuario dice: {u_msg}"}]}],
            "generationConfig": {"temperature": 0.7}
        }

        res = requests.post(url, json=payload, timeout=15)
        res_data = res.json()
        txt_ai = res_data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"respuesta": txt_ai})
    except Exception as e:
        return jsonify({"respuesta": "Aurora está conectando..."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
