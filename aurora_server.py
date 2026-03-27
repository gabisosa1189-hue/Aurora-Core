from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, base64

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        
        # 🔎 REVISIÓN MÉDICA DE LA LLAVE
        # Buscamos la llave y le sacamos cualquier espacio o comilla rara
        raw_key = os.environ.get("GEMINI_API_KEY", "")
        gemini_key = raw_key.strip().replace('"', '').replace("'", "")

        # 🚨 SI ESTÁ VACÍA, TE AVISO ANTES DE IR A GOOGLE
        if not gemini_key:
            return jsonify({
                "respuesta": "❌ ERROR CRÍTICO: El servidor no ve la llave. Render no la está pasando. Revisá el nombre en la pestaña Environment.",
                "audio": None
            })

        # 🚀 LLAMADA A GOOGLE (Versión estable)
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        params = {'key': gemini_key}
        payload = {"contents": [{"parts": [{"text": u_msg}]}]}
        
        res = requests.post(url, json=payload, params=params, timeout=15)
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"⚠️ Google dice: {res.text}", "audio": None})
            
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"respuesta": txt, "audio": None}) # Probemos primero el texto
        
    except Exception as e:
        return jsonify({"respuesta": f"Error del servidor: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
