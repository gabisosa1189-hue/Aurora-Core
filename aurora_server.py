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
    
    # 🚨 ASEGURATE DE TENER "OPENAI_API_KEY" EN RENDER
    API_KEY = os.environ.get("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/chat/completions"
    
    try:
        esencia = alma.obtener_esencia()
        contexto = f"{esencia}\nHora en Mendoza: {datetime.datetime.now().strftime('%H:%M')}"

        mensajes = [{"role": "system", "content": contexto}]
        for m in memoria_global[-6:]:
            mensajes.append({"role": m["role"], "content": m["content"]})
        mensajes.append({"role": "user", "content": u_msg})

        payload = {
            "model": "gpt-4o-mini", 
            "messages": mensajes,
            "temperature": 0.7
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        res = requests.post(url, json=payload, headers=headers, timeout=20)
        res_json = res.json()
        
        respuesta_texto = res_json['choices'][0]['message']['content']
        
        memoria_global.append({"role": "user", "content": u_msg})
        memoria_global.append({"role": "assistant", "content": respuesta_texto})
        
        return jsonify({"respuesta": respuesta_texto})

    except Exception as e:
        return jsonify({"respuesta": "Gabriel, revisá si la llave de OpenAI está bien puesta en Render."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
