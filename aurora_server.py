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
    
    if not texto_usuario:
        return jsonify({"respuesta": "Me enviaste un mensaje vacío, Gabriel."})

    API_KEY = os.environ.get("GEMINI_API_KEY")
    # URL v1beta: Aseguramos que el modelo sea el flash-latest
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        contexto = f"{esencia}\nHora en Mendoza: {datetime.datetime.now().strftime('%H:%M')}"

        # Construimos el historial asegurando que no haya errores de formato
        historial = []
        for m in memoria_global[-8:]: # Aumentamos un poquito la memoria
            rol = "user" if m["role"] == "user" else "model"
            if m.get("content"):
                historial.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        # Agregamos el mensaje actual
        historial.append({"role": "user", "parts": [{"text": texto_usuario}]})

        # Estructura de payload súper limpia
        payload = {
            "contents": historial,
            "system_instruction": { # Ojo: a veces Google prefiere 'system_instruction' con guion bajo
                "parts": [{"text": contexto}]
            },
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 800,
                "topP": 0.95
            }
        }
        
        res = requests.post(url, json=payload, timeout=25)
        
        if res.status_code != 200:
            # Si falla, leemos el mensaje de error real de Google
            try:
                msg_error = res.json().get('error', {}).get('message', 'Error desconocido')
            except:
                msg_error = res.text[:100]
            return jsonify({"respuesta": f"Google dice: {msg_error}. Revisá si tu API KEY tiene permisos para Gemini 1.5 Flash."})
            
        resultado = res.json()
        
        # Verificamos que la respuesta tenga contenido
        if 'candidates' in resultado and resultado['candidates']:
            respuesta_ai = resultado['candidates'][0]['content']['parts'][0]['text']
            
            # Guardamos en memoria con roles de Gemini
            memoria_global.append({"role": "user", "content": texto_usuario})
            memoria_global.append({"role": "model", "content": respuesta_ai})
            
            return jsonify({"respuesta": respuesta_ai})
        else:
            return jsonify({"respuesta": "Google no generó una respuesta. Intentá con otra frase."})

    except Exception as e:
        return jsonify({"respuesta": f"Error en el servidor de Mendoza: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
