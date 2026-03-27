from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Memoria de la charla (Clave para la fluidez)
memoria_global = [] 

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    data = request.json
    texto_usuario = data.get('msg', '')
    
    # 🚨 ASEGURATE DE QUE GEMINI_API_KEY ESTÉ EN RENDER 🚨
    API_KEY = os.environ.get("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        contexto = f"{esencia}\nHora en Mendoza: {datetime.datetime.now().strftime('%H:%M')}"

        # Formateo estricto para Google Gemini
        historial = []
        for m in memoria_global[-6:]:
            # Gemini solo acepta 'user' y 'model'
            rol = "user" if m["role"] == "user" else "model"
            historial.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        historial.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": historial,
            "systemInstruction": {"parts": [{"text": contexto}]},
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 600
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, json=payload, headers=headers, timeout=25)
        
        # Si hay error, lo capturamos limpio
        if res.status_code != 200:
            return jsonify({"respuesta": f"Error 400: Google no entendió el pedido. Revisá la API Key."})
            
        resultado = res.json()
        respuesta_ai = resultado['candidates'][0]['content']['parts'][0]['text']
        
        # Guardamos con roles correctos
        memoria_global.append({"role": "user", "content": texto_usuario})
        memoria_global.append({"role": "model", "content": respuesta_ai})
        
        return jsonify({"respuesta": respuesta_ai})

    except Exception as e:
        return jsonify({"respuesta": "Gabriel, se me cortó el hilo. ¿Me repetís?"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
