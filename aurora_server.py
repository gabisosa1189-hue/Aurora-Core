from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Memoria para que no se olvide de lo que hablan
memoria_global = [] 

@app.route('/')
def index():
    # Buscamos inicio.html (asegurate que se llame así en GitHub)
    return send_from_directory(os.getcwd(), 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    data = request.json
    texto_usuario = data.get('msg', '').strip()
    
    # 1. Traemos la llave desde Render
    API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # 2. URL Oficial v1 (La más estable)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        contexto = f"{esencia}\nHora en Mendoza: {datetime.datetime.now().strftime('%H:%M')}"

        # 3. Formateo de historial (JSON que Google entiende)
        historial = []
        for m in memoria_global[-6:]:
            rol = "user" if m["role"] == "user" else "model"
            historial.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        historial.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": historial,
            "systemInstruction": {"parts": [{"text": contexto}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600}
        }
        
        # 4. Petición a Google
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, json=payload, headers=headers, timeout=25)
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"Error de Google: {res.status_code}"})
            
        resultado = res.json()
        respuesta_ai = resultado['candidates'][0]['content']['parts'][0]['text']
        
        # Guardamos en memoria
        memoria_global.append({"role": "user", "content": texto_usuario})
        memoria_global.append({"role": "model", "content": respuesta_ai})
        
        return jsonify({"respuesta": respuesta_ai})

    except Exception as e:
        return jsonify({"respuesta": "Se me cortó el hilo, Gabriel. ¿Me repetís?"})

if __name__ == '__main__':
    # Render asigna el puerto automáticamente
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
