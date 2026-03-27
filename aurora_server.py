from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Memoria de la charla (El secreto de la fluidez)
memoria_global = [] 

@app.route('/')
def index(): 
    # Aseguramos que cargue el archivo que renombraste
    return send_from_directory(os.getcwd(), 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    data = request.json
    texto_usuario = data.get('msg', '')
    
    API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # URL ACTUALIZADA: Usamos 'gemini-1.5-flash-latest' para evitar el Error 404
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        reloj = f"Sistema: Hora actual en Mendoza {datetime.datetime.now().strftime('%H:%M')}."
        contexto_sistema = f"{esencia}\n{reloj}"

        # Construimos la historia para que Aurora tenga memoria
        contenidos = []
        # Tomamos los últimos 6 mensajes para que no se pierda la fluidez
        for m in memoria_global[-6:]:
            rol = "user" if m["role"] == "user" else "model"
            contenidos.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        # Agregamos lo que el usuario acaba de decir ahora
        contenidos.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": contenidos,
            "systemInstruction": {"parts": [{"text": contexto_sistema}]},
            "generationConfig": {
                "temperature": 0.7, 
                "maxOutputTokens": 600,
                "topP": 0.95
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, json=payload, headers=headers, timeout=25)
        
        if res.status_code != 200:
            print(f"Error Google: {res.text}")
            return jsonify({"respuesta": "Perdón Gabriel, mi conexión con Google falló. ¿Podés intentar de nuevo?"})
            
        resultado = res.json()
        respuesta_ai = resultado['candidates'][0]['content']['parts'][0]['text']
        
        # GUARDAMOS EN MEMORIA (Para que la próxima vez se acuerde)
        memoria_global.append({"role": "user", "content": texto_usuario})
        memoria_global.append({"role": "assistant", "content": respuesta_ai})

    except Exception as e:
        print(f"Error crítico: {e}")
        respuesta_ai = "Se me cruzaron los cables un segundo. ¿Qué me decías?"

    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
