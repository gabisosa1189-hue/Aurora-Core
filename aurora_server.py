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
    texto_usuario = data.get('msg', '')
    
    API_KEY = os.environ.get("GEMINI_API_KEY")
    # URL v1beta: Es la que mejor funciona con systemInstruction
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        contexto = f"{esencia}\nHora en Mendoza: {datetime.datetime.now().strftime('%H:%M')}"

        # LIMPIEZA TOTAL: Solo mandamos lo que Google entiende
        historial = []
        for m in memoria_global[-6:]:
            rol = "user" if m["role"] == "user" else "model"
            if m["content"]: # Evitamos mensajes vacíos
                historial.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        historial.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": historial,
            "systemInstruction": {"parts": [{"text": contexto}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600}
        }
        
        res = requests.post(url, json=payload, timeout=25)
        
        if res.status_code != 200:
            # ESTO ES CLAVE: Si falla, nos dice por qué
            error_detalle = res.json().get('error', {}).get('message', 'Error desconocido')
            return jsonify({"respuesta": f"Error de Google: {error_detalle}"})
            
        resultado = res.json()
        respuesta_ai = resultado['candidates'][0]['content']['parts'][0]['text']
        
        # Guardamos en memoria con roles de Gemini
        memoria_global.append({"role": "user", "content": texto_usuario})
        memoria_global.append({"role": "model", "content": respuesta_ai})
        
        return jsonify({"respuesta": respuesta_ai})

    except Exception as e:
        return jsonify({"respuesta": f"Error en el servidor: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
