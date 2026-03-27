from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Memoria de la charla (Para que Aurora se acuerde de todo)
memoria_global = [] 

@app.route('/')
def index(): 
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    data = request.json
    texto_usuario = data.get('msg', '')
    
    API_KEY = os.environ.get("GEMINI_API_KEY")
    # DIRECCIÓN ACTUALIZADA (v1 en lugar de v1beta y modelo flash-latest)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        contexto = f"{esencia}\nHora en Mendoza: {datetime.datetime.now().strftime('%H:%M')}"

        # Formato de memoria para que la charla sea fluida
        contenidos = []
        for m in memoria_global[-8:]: # Recordamos los últimos 8 mensajes
            rol = "user" if m["role"] == "user" else "model"
            contenidos.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        contenidos.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": contenidos,
            "systemInstruction": {"parts": [{"text": contexto}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600}
        }
        
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, json=payload, headers=headers, timeout=20)
        
        # Si falla, lanzamos el error para verlo en el log
        res.raise_for_status()
        
        resultado = res.json()
        respuesta_ai = resultado['candidates'][0]['content']['parts'][0]['text']
        
        # GUARDAMOS EN MEMORIA (El secreto de la fluidez)
        memoria_global.append({"role": "user", "content": texto_usuario})
        memoria_global.append({"role": "assistant", "content": respuesta_ai})

    except Exception as e:
        print(f"--- ERROR DETECTADO ---")
        print(f"Detalle: {str(e)}")
        # Si hay error 404, Aurora te lo dirá para que sepamos
        respuesta_ai = "Perdón, Gabriel. Todavía tengo un problemita en mi conexión con Google. ¿Revisaste que la API Key esté activa?"

    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
