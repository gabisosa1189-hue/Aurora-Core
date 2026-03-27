from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

memoria_global = [] 

@app.route('/')
def index():
    # Intentamos cargar inicio.html. Asegurate que en GitHub esté EXACTO así.
    try:
        return send_from_directory(os.getcwd(), 'inicio.html')
    except Exception as e:
        return f"Error: No encontré 'inicio.html'. Archivos en carpeta: {os.listdir('.')}"

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    data = request.json
    texto_usuario = data.get('msg', '')
    API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # URL v1beta para evitar el 404 de Google
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        contexto = f"{esencia}\nHora en Mendoza: {datetime.datetime.now().strftime('%H:%M')}"

        contenidos = []
        for m in memoria_global[-6:]:
            rol = "user" if m["role"] == "user" else "model"
            contenidos.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        contenidos.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": contenidos,
            "systemInstruction": {"parts": [{"text": contexto}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600}
        }
        
        res = requests.post(url, json=payload, timeout=25)
        res.raise_for_status()
        respuesta_ai = res.json()['candidates'][0]['content']['parts'][0]['text']
        
        memoria_global.append({"role": "user", "content": texto_usuario})
        memoria_global.append({"role": "assistant", "content": respuesta_ai})
        return jsonify({"respuesta": respuesta_ai})

    except Exception as e:
        return jsonify({"respuesta": "Perdón, tuve un hipo en la conexión. ¿Me repetís?"})

if __name__ == '__main__':
    # Render usa el puerto de la variable de entorno
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
