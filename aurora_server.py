from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

memoria_global = [] 

@app.route('/')
def index():
    try:
        return send_from_directory(os.getcwd(), 'inicio.html')
    except:
        return "Error: No encontré inicio.html. Revisá el nombre en GitHub."

@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    data = request.json
    texto_usuario = data.get('msg', '')
    
    # 🚨 ASEGURATE DE QUE ESTA VARIABLE ESTÉ EN RENDER 🚨
    API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # Usamos la v1 estable para evitar caprichos de Google
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
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
        
        res = requests.post(url, json=payload, timeout=20)
        
        # Si Google falla, queremos saber por qué
        if res.status_code != 200:
            return jsonify({"respuesta": f"Error de Google {res.status_code}: {res.text[:50]}"})
            
        resultado = res.json()
        respuesta_ai = resultado['candidates'][0]['content']['parts'][0]['text']
        
        memoria_global.append({"role": "user", "content": texto_usuario})
        memoria_global.append({"role": "assistant", "content": respuesta_ai})
        return jsonify({"respuesta": respuesta_ai})

    except Exception as e:
        # Esto nos dirá en el log de Render qué pasó exactamente
        print(f"ERROR CRÍTICO: {str(e)}")
        return jsonify({"respuesta": "Gabriel, mi conexión interna falló. ¿Revisaste la API Key?"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
