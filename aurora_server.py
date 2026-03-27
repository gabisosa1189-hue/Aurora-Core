from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

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
    if not API_KEY:
        return jsonify({"respuesta": "ERROR: No configuraste GEMINI_API_KEY en Render."})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    try:
        # 1. Armamos el contexto
        esencia = alma.obtener_esencia()
        contexto = f"{esencia}\nHora actual: {datetime.datetime.now().strftime('%H:%M')}"

        # 2. Formato de memoria Gemini
        contenidos = []
        for m in memoria_global[-6:]:
            rol = "user" if m["role"] == "user" else "model"
            contenidos.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        contenidos.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": contenidos,
            "systemInstruction": {"parts": [{"text": contexto}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
        }
        
        # 3. La llamada (Aquí es donde está fallando)
        res = requests.post(url, json=payload, timeout=20)
        
        # SI GOOGLE RECHAZA LA PETICIÓN, ESTO NOS DIRÁ POR QUÉ
        if res.status_code != 200:
            print(f"--- ERROR DE GOOGLE ---")
            print(f"Status: {res.status_code}")
            print(f"Respuesta: {res.text}")
            return jsonify({"respuesta": f"Google respondió con error {res.status_code}. Revisá los logs."})
            
        respuesta_ai = res.json()['candidates'][0]['content']['parts'][0]['text']
        
        memoria_global.append({"role": "user", "content": texto_usuario})
        memoria_global.append({"role": "assistant", "content": respuesta_ai})

    except Exception as e:
        # ESTO ES LO QUE NECESITO QUE ME PASES
        print(f"--- ERROR CRÍTICO DE PYTHON ---")
        print(str(e))
        respuesta_ai = f"Error técnico: {str(e)}"

    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
