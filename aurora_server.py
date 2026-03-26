from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import datetime
import alma

# Intentamos cargar el módulo de internet de forma segura
try:
    import internet
    INTERNET_ACTIVO = True
except Exception as e:
    print(f"Aviso: Módulo de internet no cargó correctamente - {e}")
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
    
    # --- 1. RELOJ INTERNO INFALIBLE (Hora de Argentina UTC-3) ---
    try:
        zona_ar = datetime.timezone(datetime.timedelta(hours=-3))
        ahora = datetime.datetime.now(zona_ar)
        reloj_interno = f"DATOS DE SISTEMA: Hoy es {ahora.strftime('%d/%m/%Y')} y la hora exacta en Argentina es {ahora.strftime('%H:%M')}."
    except:
        reloj_interno = "Hora no disponible."

    # --- 2. DATOS EXTRA SEGUROS (Clima, Noticias) ---
    datos_api = ""
    datos_red = ""
    if INTERNET_ACTIVO:
        try:
            datos_api = internet.obtener_datos_api(texto_usuario)
        except Exception as e:
            print(f"Error leve buscando APIs: {e}")
            
        palabras_clave = ["noticia", "clima", "quien", "paso", "mundo", "temperatura"]
        if len(texto_usuario.split()) >= 2 and any(p in msg_limpio for p in palabras_clave):
            try:
                datos_red = internet.buscar_en_red(texto_usuario)
            except Exception as e:
                print(f"Error leve en buscador profundo: {e}")
    
    # --- 3. ARMADO DEL CEREBRO ---
    esencia_aurora = alma.obtener_esencia()
    system_prompt = (
        f"{esencia_aurora}\n\n"
        f"{reloj_interno}\n"
        f"DATOS RECIENTES DE INTERNET (Úsalos solo si la pregunta lo requiere):\n{datos_api}\n{datos_red}"
    )
    
    mensajes = [{"role": "system", "content": system_prompt}]
    mensajes.extend(historial[-4:]) 
    mensajes.append({"role": "user", "content": texto_usuario})
    
    try:
        data_req = {
            "model": "llama-3.1-8b-instant", 
            "messages": mensajes, 
            "temperature": 0.4 # Lo bajamos a 0.4 para que responda directo al punto
        }
        res = requests.post(url, headers=headers, json=data_req, timeout=15)
        res.raise_for_status()
        respuesta_ai = res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Falla crítica de Groq: {e}")
        respuesta_ai = "Disculpe, mi red se congestionó un segundo. ¿Me lo repite?"

    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    
    return jsonify({"respuesta": respuesta_ai})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)
