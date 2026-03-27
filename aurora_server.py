import os, requests, base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 LLAVE DE GOOGLE (Sacala de AI Studio)
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        
        # 🚀 RUTA ULTRA-COMPATIBLE 2026
        # Usamos 'gemini-1.5-flash' que es el que entra en el plan gratis
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {"contents": [{"parts": [{"text": u_msg}]}]}
        res = requests.post(url, json=payload, timeout=15)
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"Google falló: {res.text}", "audio": None})
            
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"respuesta": txt, "audio": None})
        
    except Exception as e:
        return jsonify({"respuesta": f"Error: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
