from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

memoria_global = [] 

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    data = request.json
    texto_usuario = data.get('msg', '').strip()
    
    API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # URL V1 ESTABLE: La dirección oficial que no falla en 2026
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        contexto = f"{esencia}\nHora en Mendoza: {datetime.datetime.now().strftime('%H:%M')}"

        # Formateo estricto para evitar el Error 400
        historial = []
        for m in memoria_global[-6:]:
            # Cambiamos 'assistant' por 'model' para que Google no se queje
            rol_gemini = "user" if m["role"] == "user" else "model"
            historial.append({"role": rol_gemini, "parts": [{"text": m["content"]}]})
        
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
        
        if res.status_code != 200:
            # Si hay error, lo mostramos para saber qué pasa
            return jsonify({"respuesta": f"Error {res.status_code}: Google no aceptó el formato."})
            
        resultado = res.json()
        respuesta_ai = resultado['candidates'][0]['content']['parts'][0]['text']
        
        # Guardamos en memoria con roles limpios
        memoria_global.append({"role": "user", "content": texto_usuario})
        memoria_global.append({"role": "model", "content": respuesta_ai})
        
        return jsonify({"respuesta": respuesta_ai})

    except Exception as e:
        return jsonify({"respuesta": f"Error de conexión: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
