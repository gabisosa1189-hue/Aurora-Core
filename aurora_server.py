from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime

# Intentamos importar tus archivos, si fallan, la app arranca igual
try:
    import alma, internet
except ImportError:
    alma = None
    internet = None

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

memoria_global = [] 

# RUTA DE SALUDO (Health Check)
# Esto es lo que Render necesita ver para saber que la app vive
@app.route('/health')
def health():
    return "OK", 200

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        API_KEY = os.environ.get("GEMINI_API_KEY") # 🚨 ASEGURATE DE PONERLA EN RENDER (Environment Variables)
        
        if not API_KEY:
            return jsonify({"respuesta": "Falta la API KEY en la configuración de Render."})

        # Buscador de internet (solo si el archivo existe)
        busqueda_info = ""
        if internet and any(p in u_msg.lower() for p in ["busca", "internet", "clima", "quien es"]):
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
        return jsonify({"respuesta": "Aurora está reconectando sus neuronas..."})

if __name__ == '__main__':
    # Esto es solo para tu compu local
    app.run(host='0.0.0.0', port=10000)
