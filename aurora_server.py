from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Memoria de la charla para que Aurora no sea "olvidadiza"
memoria_global = [] 

@app.route('/')
def index(): 
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    data = request.json
    texto_usuario = data.get('msg', '')
    
    # 1. Traemos la llave de Render
    API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # 2. URL DEFINITIVA (v1beta + gemini-1.5-flash-latest)
    # Esta es la dirección que acepta los modelos más nuevos sin tirar 404
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        reloj = f"Sistema: Hora actual {datetime.datetime.now().strftime('%H:%M')}."
        contexto = f"{esencia}\n{reloj}"

        # 3. Construcción de memoria para charla fluida
        contenidos = []
        for m in memoria_global[-6:]:
            rol = "user" if m["role"] == "user" else "model"
            contenidos.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        contenidos.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": contenidos,
            "systemInstruction": {"parts": [{"text": contexto}]},
            "generationConfig": {
                "temperature": 0.7, 
                "maxOutputTokens": 600,
                "topP": 0.95
            }
        }
        
        # 4. Petición a Google
        res = requests.post(url, json=payload, timeout=25)
        
        # Si Google nos da un error, lo mandamos al chat para verlo
        if res.status_code != 200:
            return jsonify({"respuesta": f"DEBUG: Error de Google {res.status_code}. Mensaje: {res.text[:100]}"})
            
        resultado = res.json()
        respuesta_ai = resultado['candidates'][0]['content']['parts'][0]['text']
        
        # 5. Guardamos en memoria para la fluidez
        memoria_global.append({"role": "user", "content": texto_usuario})
        memoria_global.append({"role": "assistant", "content": respuesta_ai})

    except Exception as e:
        print(f"Error: {e}")
        respuesta_ai = "Perdón, se me cortó la conexión un segundo. ¿Me repetís?"

    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
