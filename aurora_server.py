from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

try:
    import internet
    INTERNET_ACTIVO = True
except:
    INTERNET_ACTIVO = False

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Memoria de la charla (Para que sea fluida y se acuerde de lo que dijeron)
historial_memoria = [] 

@app.route('/')
def index(): 
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historial_memoria
    data = request.json
    texto_usuario = data.get('msg', '')
    
    # 1. VERIFICAR LLAVE
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        return jsonify({"respuesta": "Falta la GEMINI_API_KEY en las variables de Render."})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    try:
        esencia = alma.obtener_esencia()
        # Le pasamos la fecha y hora de Mendoza para que esté ubicada
        reloj = f"Sistema: Hoy es {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}."
        
        system_prompt = f"{esencia}\n{reloj}\n"
        
        if INTERNET_ACTIVO:
            try:
                datos_api = internet.obtener_datos_api(texto_usuario)
                system_prompt += f"\nDATOS TIEMPO REAL: {datos_api}"
            except: pass

        # 2. CONSTRUIR LA MEMORIA (Esto es lo que hace la charla fluida)
        # Tomamos los últimos 10 mensajes para que no se olvide de nada
        contenidos = []
        for m in historial_memoria[-10:]:
            rol = "user" if m["role"] == "user" else "model"
            contenidos.append({"role": rol, "parts": [{"text": m["content"]}]})
        
        # Agregamos lo que el usuario acaba de decir ahora
        contenidos.append({"role": "user", "parts": [{"text": texto_usuario}]})

        payload = {
            "contents": contenidos,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
        }
        
        # 3. LLAMADA A GOOGLE
        res = requests.post(url, json=payload, timeout=20)
        
        if res.status_code != 200:
            print(f"ERROR GOOGLE: {res.text}") # Esto lo vemos en Render
            return jsonify({"respuesta": "Aurora está descansando un minuto. Probá de nuevo en un instante."})
            
        respuesta_ai = res.json()['candidates'][0]['content']['parts'][0]['text']
        
        # Guardamos en la memoria para que la charla siga
        historial_memoria.append({"role": "user", "content": texto_usuario})
        historial_memoria.append({"role": "assistant", "content": respuesta_ai})

    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        respuesta_ai = "Perdón, se me cruzaron los cables. ¿Me repetís eso?"

    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
