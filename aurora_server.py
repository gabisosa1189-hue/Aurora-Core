from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import datetime
import alma

try:
    import internet
    INTERNET_ACTIVO = True
except:
    INTERNET_ACTIVO = False

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

BASE_PATH = os.getcwd() 
historial = [] 

@app.route('/')
def index(): 
    return send_from_directory(BASE_PATH, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historial
    data = request.json
    texto_usuario = data.get('msg', '')
    msg_limpio = texto_usuario.lower()
    
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    try:
        zona_ar = datetime.timezone(datetime.timedelta(hours=-3))
        ahora = datetime.datetime.now(zona_ar)
        reloj = f"Sistema: Hoy es {ahora.strftime('%d/%m/%Y')} y la hora es {ahora.strftime('%H:%M')}."
    except:
        reloj = ""

    # Limpiador de memoria: Solo recuerda los últimos 6 mensajes para no trabarse
    if len(historial) > 6:
        historial = historial[-6:]

    esencia = alma.obtener_esencia()
    system_prompt = f"{esencia}\n{reloj}"
    
    if INTERNET_ACTIVO:
        try:
            datos_api = internet.obtener_datos_api(texto_usuario)
            system_prompt += f"\nDATOS ACTUALES:\n{datos_api}"
        except: pass
        
        palabras_clave = ["noticia", "clima", "quien", "paso", "mundo", "temperatura"]
        if len(texto_usuario.split()) >= 2 and any(p in msg_limpio for p in palabras_clave):
            try:
                datos_red = internet.buscar_en_red(texto_usuario)
                if datos_red != "Sin datos extra de internet.":
                    system_prompt += f"\nBÚSQUEDA PROFUNDA:\n{datos_red}"
            except: pass

    mensajes = [{"role": "system", "content": system_prompt}]
    mensajes.extend(historial) 
    mensajes.append({"role": "user", "content": texto_usuario})
    
    try:
        data_req = {
            "model": "llama-3.1-8b-instant", 
            "messages": mensajes, 
            "temperature": 0.4,
            "max_tokens": 400
        }
        res = requests.post(url, headers=headers, json=data_req, timeout=25)
        res.raise_for_status()
        respuesta_ai = res.json()['choices'][0]['message']['content']
    except:
        respuesta_ai = "Disculpe, mi red se saturó un segundo. ¿Podemos retomar?"

    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    
    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)
