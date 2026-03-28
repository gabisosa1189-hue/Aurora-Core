import os, requests, json, re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 LLAVES (Configuradas en Render > Environment)
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_API_KEY")

# 🕒 HORA MENDOCINA
def get_datetime():
    try:
        tz = pytz.timezone('America/Argentina/Mendoza')
        now = datetime.now(tz)
        return now.strftime("%H:%M"), now.strftime("%d/%m/%Y")
    except:
        return "--:--", "--/--/--"

# 🌦 CLIMA INTELIGENTE Y RÁPIDO
def buscar_clima_inteligente(mensaje):
    if not OPENWEATHER_KEY:
        return ""
    
    mensaje = mensaje.lower()
    ciudades_a_buscar = []
    
    # Ciudades clave. Si el usuario las menciona, las buscamos en milisegundos.
    lugares = {
        "mendoza": "Mendoza,AR", 
        "buenos aires": "Buenos Aires,AR", 
        "san martin": "San Martin,Mendoza,AR", 
        "san martín": "San Martin,Mendoza,AR",
        "cordoba": "Cordoba,AR",
        "córdoba": "Cordoba,AR"
    }
    
    for clave, valor in lugares.items():
        if clave in mensaje:
            ciudades_a_buscar.append(valor)
            
    # Si pregunta por el clima pero no nombra ciudad, por defecto San Martín
    if ("clima" in mensaje or "tiempo" in mensaje) and not ciudades_a_buscar:
        ciudades_a_buscar.append("San Martin,Mendoza,AR")

    reporte = []
    for ciudad in ciudades_a_buscar:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={OPENWEATHER_KEY}&units=metric&lang=es"
            res = requests.get(url, timeout=3).json()
            temp = round(res['main']['temp']) # Redondeamos para que suene más natural
            desc = res['weather'][0]['description']
            nombre = ciudad.split(',')[0]
            reporte.append(f"En {nombre} hace {temp}°C con {desc}.")
        except:
            continue
            
    return " ".join(reporte)

# 📚 BUSCADOR DE DATOS EXACTOS
def buscar_datos_exactos(mensaje):
    mensaje = mensaje.lower()
    # Filtro rápido para no perder tiempo si es una charla normal
    if any(palabra in mensaje for palabra in ["quien es", "que es", "presidente", "capital"]):
        # Limpiamos la pregunta para buscar solo la palabra clave
        busqueda = mensaje.replace("quien es", "").replace("que es", "").replace("el presidente de", "presidente").strip()
        busqueda = " ".join(busqueda.split()[:4]) # Máximo 4 palabras
        
        try:
            url = f"https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={busqueda}&utf8=&format=json"
            res = requests.get(url, timeout=3).json()
            if res['query']['search']:
                snippet = res['query']['search'][0]['snippet']
                limpio = re.sub('<[^<]+>', '', snippet)
                return f"Dato exacto de Wikipedia: {limpio}"
        except:
            pass
    return ""

# 🌐 RUTA PRINCIPAL
@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/ping')
def ping():
    return "pong", 200

# 💬 MOTOR DEL CHAT (Optimizado para velocidad)
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True)
        msg = data.get('msg', '').strip() if data else ''

        if not msg:
            return jsonify({"respuesta": "¡Hablame, Gabriel! 😏"})

        hora, fecha = get_datetime()
        msg_lower = msg.lower()

        # IDENTIDAD RÁPIDA
        if "quien te creo" in msg_lower or "creador" in msg_lower:
            return jsonify({"respuesta": "Fui creada por Gabriel Sosa Scriboni, acá en San Martín, Mendoza. 😏"})

        # 1. RECOPILAMOS INFO EN TIEMPO REAL (En menos de 1 segundo)
        info_clima = buscar_clima_inteligente(msg)
        info_datos = buscar_datos_exactos(msg)

        # 2. CONSTRUIMOS EL CEREBRO
        system_prompt = (
            f"Eres Aurora, una IA mendocina rápida, amable y elegante. Creador: Gabriel Sosa Scriboni.\n"
            f"Hoy es {fecha} y son las {hora}.\n"
            f"REGLA DE ORO: Si te doy 'Datos en tiempo real' abajo, ÚSALOS para responder con exactitud absoluta, pero mantén un tono conversacional y breve.\n\n"
        )
        
        # INYECTAMOS LA INFORMACIÓN AL CEREBRO DE AURORA
        if info_clima or info_datos:
            system_prompt += "--- DATOS EN TIEMPO REAL PARA TU RESPUESTA ---\n"
            if info_clima: system_prompt += f"CLIMA ACTUAL: {info_clima}\n"
            if info_datos: system_prompt += f"INFORMACIÓN: {info_datos}\n"
            system_prompt += "---------------------------------------------\n"

        mensajes = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg}
        ]

        # 3. LLAMADA ULTRA RÁPIDA A LA IA
        if not OPENROUTER_KEY:
            return jsonify({"respuesta": "Falta la llave de OpenRouter."})

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "openai/gpt-4o-mini",
                "messages": mensajes,
                "max_tokens": 150,  # Reducimos tokens para que responda más rápido
                "temperature": 0.4  # La hacemos más precisa y menos inventiva
            },
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            timeout=10
        )

        respuesta_ia = res.json()['choices'][0]['message']['content']
        return jsonify({"respuesta": respuesta_ia})

    except Exception as e:
        return jsonify({"respuesta": f"¡Upa! Un pequeño tropezón: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
