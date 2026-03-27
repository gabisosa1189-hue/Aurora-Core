from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma
from duckduckgo_search import DDGS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

memoria_global = [] 

def buscar_web(q):
    try:
        with DDGS() as ddgs:
            res = [r['body'] for r in ddgs.text(q, max_results=2)]
            return " | ".join(res)
    except: return ""

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    data = request.json
    u_msg = data.get('msg', '').strip()
    API_KEY = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    try:
        # Búsqueda inteligente si es necesario
        info = ""
        if any(w in u_msg.lower() for w in ["hoy", "noticias", "clima", "quien"]):
            info = f" [Dato Web: {buscar_web(u_msg)}]"

        esencia = alma.obtener_esencia()
        ctx = f"{esencia}\nHora: {datetime.datetime.now().strftime('%H:%M')}.{info}"

        # Estructura ultra-limpia para evitar Error 400
        historial = []
        for m in memoria_global[-6:]:
            historial.append({"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]})
        historial.append({"role": "user", "parts": [{"text": u_msg}]})

        payload = {
            "contents": historial,
            "systemInstruction": {"parts": [{"text": ctx}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
        }
        
        res = requests.post(url, json=payload, timeout=20)
        res_json = res.json()
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"Error {res.status_code}: {res_json.get('error', {}).get('message', '')}"})

        txt_ai = res_json['candidates'][0]['content']['parts'][0]['text']
        memoria_global.append({"role": "user", "content": u_msg})
        memoria_global.append({"role": "model", "content": txt_ai})
        return jsonify({"respuesta": txt_ai})

    except Exception as e:
        return jsonify({"respuesta": "Hubo un pequeño cortocircuito. ¿Me repetís?"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
