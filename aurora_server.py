import os, requests, base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 TRAEMOS LA LLAVE (Verificá que en Render se llame GEMINI_API_KEY)
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        u_msg = request.json.get('msg', '').strip()
        
        # 🚀 CAMBIO DE RUTA: Usamos la versión estable 'v1' y el modelo a secas
        # Esta es la dirección que Google tiene abierta para todos ahora
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"Sos Aurora, una IA de Mendoza. Respondé de forma breve y amable. Usuario dice: {u_msg}"}]
            }]
        }
        
        res = requests.post(url, json=payload, timeout=15)
        
        if res.status_code != 200:
            # Si vuelve a fallar, el error nos dirá la verdad
            return jsonify({"respuesta": f"Google falló: {res.text}", "audio": None})
            
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"respuesta": txt, "audio": None})
        
    except Exception as e:
        return jsonify({"respuesta": f"Error del servidor: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
