import os
import requests
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route('/')
def index():
    # 🛡️ Esto obliga a limpiar la memoria vieja del navegador
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
        if not msg: return jsonify({"respuesta": "Dime..."})
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "system", "content": "IA amable creada por Gabriel Sosa Scriboni."}, {"role": "user", "content": msg}]
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=10
        )
        return jsonify({"respuesta": res.json()['choices'][0]['message']['content']})
    except:
        return jsonify({"respuesta": "Error de conexión."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
