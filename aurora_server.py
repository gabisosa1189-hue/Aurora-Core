from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

memoria_global = [] 

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'inicio.html')

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory(os.getcwd(), path)

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    data = request.json
    u_msg = data.get('msg', '').strip()
    API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # 🚨 URL BLINDADA: v1beta con gemini-1.5-flash-latest
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        contexto = f"{esencia}\nHora en Mendoza: {datetime.datetime.now().strftime('%H:%M')}"
        historial = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in memoria_global[-6:]]
        historial.append({"role": "user", "parts": [{"text": u_msg}]})

        payload = {"contents": historial, "systemInstruction": {"parts": [{"text": contexto}]}, "generationConfig": {"temperature": 0.7}}
        res = requests.post(url, json=payload, timeout=20)
        res_json = res.json()
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"Error de Google: {res_json.get('error', {}).get('message')}"})

        txt_ai = res_json['candidates'][0]['content']['parts'][0]['text']
        memoria_global.append({"role": "user", "content": u_msg})
        memoria_global.append({"role": "model", "content": txt_ai})
        return jsonify({"respuesta": txt_ai})
    except Exception as e:
        return jsonify({"respuesta": "Cortocircuito de red. ¿Render se durmió?"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
