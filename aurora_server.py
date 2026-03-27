from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime

# Intentamos importar tus archivos de lógica
try:
    import alma, internet
except ImportError:
    alma = None
    internet = None

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

memoria_global = [] 

# 🚨 ESTA ES LA RUTA QUE FALTABA: Entrega el video y cualquier archivo de la carpeta
@app.route('/<path:path>')
def send_static(path):
    return send_from_directory(os.getcwd(), path)

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        API_KEY = os.environ.get("GEMINI_API_KEY") 
        
        if not API_KEY:
            return jsonify({"respuesta": "Falta la API KEY en Render (Environment Variables)."})

        busqueda_info = ""
        if internet and any(p in u_msg.lower() for p in ["busca", "internet", "noticias", "clima"]):
            busqueda_info = internet.buscar(u_msg)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
        
        esencia = alma.obtener_esencia() if alma else "Eres Aurora, una IA de Mendoza."
        contexto = f"{esencia}\nHora: {datetime.datetime.now().strftime('%H:%M')}\nInfo: {busqueda_info}"
        
        historial = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in memoria_global[-6:]]
        historial.append({"role": "user", "parts": [{"text": u_msg}]})

        payload = {"contents": historial, "systemInstruction": {"parts": [{"text": contexto}]}, "generationConfig": {"temperature": 0.7}}
        res = requests.post(url, json=payload, timeout=15)
        res_json = res.json()
        
        txt_ai = res_json['candidates'][0]['content']['parts'][0]['text']
        memoria_global.append({"role": "user", "content": u_msg})
        memoria_global.append({"role": "model", "content": txt_ai})
        
        return jsonify({"respuesta": txt_ai})
    except Exception as e:
        return jsonify({"respuesta": "Aurora está reconectando... reintentá en un segundo."})

if __name__ == '__main__':
    # Puerto 10000 fijo para Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
