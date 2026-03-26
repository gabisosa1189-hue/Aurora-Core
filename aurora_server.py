from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, datetime, alma, internet

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Memoria ultra-corta para evitar que Render se trabe (Solo 2 vueltas)
historial = [] 

@app.route('/')
def index(): 
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historial
    data = request.json
    user_msg = data.get('msg', '')
    
    # 1. Datos de Realidad (Presidente, Dólar, Clima)
    # Forzamos a que internet.py busque la verdad actual
    datos_actuales = internet.obtener_datos_api(user_msg)
    
    # 2. Reloj del Servidor
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
    fecha_hoy = f"FECHA Y HORA REAL: {now.strftime('%d/%m/%Y %H:%M')}"

    # 3. Limpieza de Memoria (Si hay más de 4 mensajes, borramos)
    if len(historial) > 4:
        historial = historial[-4:]

    # 4. Prompt de Hierro (Ordenamos que no mienta con el presidente)
    prompt_seguro = (
        f"{alma.obtener_esencia()}\n"
        f"{fecha_hoy}\n"
        f"INFORMACIÓN DE INTERNET (OBLIGATORIA): {datos_actuales}\n"
        "REGLA CRÍTICA: El presidente de Argentina es Javier Milei. No menciones a presidentes anteriores."
    )
    
    headers = {
        "Authorization": f"Bearer {os.environ.get('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": prompt_seguro}] + historial + [{"role": "user", "content": user_msg}],
        "temperature": 0.3, # Bajamos la temperatura para que sea más precisa
        "max_tokens": 200
    }

    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15)
        res.raise_for_status()
        ai_res = res.json()['choices'][0]['message']['content']
    except:
        ai_res = "Mi conexión se saturó un segundo. ¿Podrías repetir?"

    historial.append({"role": "user", "content": user_msg})
    historial.append({"role": "assistant", "content": ai_res})
    
    return jsonify({"respuesta": ai_res})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0')
