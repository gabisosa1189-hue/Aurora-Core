from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma

# Intentamos cargar internet, si falla, el servidor sigue vivo
try:
    import internet
    INTERNET_OK = True
except:
    INTERNET_OK = False

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Memoria ultra-liviana (Solo guarda las últimas 2 vueltas)
historial = [] 

@app.route('/')
def index(): 
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historial
    data = request.json
    user_msg = data.get('msg', '')
    
    # 1. Reloj Rápido
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
    info_sistema = f"Hoy: {now.strftime('%d/%m/%Y %H:%M')}. "

    # 2. Datos de Internet (Solo si es necesario para no pesar)
    contexto_extra = ""
    if INTERNET_OK and any(p in user_msg.lower() for p in ["quien", "noticia", "dolar", "clima", "hoy"]):
        try:
            contexto_extra = internet.obtener_datos_api(user_msg)
        except: pass

    # 3. Limpieza radical de historial (Solo 4 mensajes max)
    if len(historial) > 4:
        historial = historial[-4:]

    # 4. Prompt optimizado para velocidad
    prompt = f"{alma.obtener_esencia()}\n{info_sistema}\nContexto: {contexto_extra}"
    
    headers = {
        "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": prompt}] + historial + [{"role": "user", "content": user_msg}],
        "temperature": 0.5,
        "max_tokens": 250 # Respuestas cortas = más rápidas
    }

    try:
        # Timeout corto para que no se quede colgado
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=10)
        res.raise_for_status()
        ai_res = res.json()['choices'][0]['message']['content']
    except:
        ai_res = "Perdí la conexión un segundo. ¿Me repite su consulta?"

    historial.append({"role": "user", "content": user_msg})
    historial.append({"role": "assistant", "content": ai_res})
    
    return jsonify({"respuesta": ai_res})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
