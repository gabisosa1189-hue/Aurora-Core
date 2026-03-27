import os, requests, json, time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 KEYS (desde Render)
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_API_KEY")

# 🧠 MEMORIA
MEMORIA_PATH = "memoria.json"

def cargar_memoria():
    if not os.path.exists(MEMORIA_PATH):
        return []
    try:
        with open(MEMORIA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def guardar_memoria(memoria):
    try:
        with open(MEMORIA_PATH, "w", encoding="utf-8") as f:
            json.dump(memoria[-12:], f, indent=2, ensure_ascii=False)
    except:
        pass

# 🕒 HORA / FECHA
def get_datetime():
    tz = pytz.timezone('America/Argentina/Mendoza')
    now = datetime.now(tz)
    return now.strftime("%H:%M"), now.strftime("%d/%m/%Y")

# 🌦 CLIMA
def get_clima():
    if not OPENWEATHER_KEY:
        return "No tengo acceso al clima ahora 😅"

    try:
        ciudad = "San Martin,AR"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={OPENWEATHER_KEY}&units=metric&lang=es"
        res = requests.get(url, timeout=5).json()

        temp = res['main']['temp']
        desc = res['weather'][0]['description']
        return f"{desc}, {temp}°C"
    except:
        return "No pude obtener el clima ahora 🌧"

# 🧠 IA (OpenRouter)
def preguntar_ia(mensajes):
    if not OPENROUTER_KEY:
        return "No tengo acceso a mi inteligencia ahora mismo 😔"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": mensajes,
        "temperature": 0.7
    }

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=data,
            headers=headers,
            timeout=15
        )

        if res.status_code != 200:
            return "Estoy un poco saturada ahora mismo 😅"

        return res.json()['choices'][0]['message']['content']

    except:
        return "Tuve un pequeño fallo… pero sigo con vos 😌"

# 🔍 DETECTOR INTELIGENTE
def detectar_intencion(msg):
    msg = msg.lower()

    if any(x in msg for x in ["hora", "qué hora", "que hora"]):
        return "hora"

    if any(x in msg for x in ["fecha", "día", "dia"]):
        return "fecha"

    if "clima" in msg or "temperatura" in msg:
        return "clima"

    if any(x in msg for x in ["quien te creo", "quién te creó", "tu creador"]):
        return "creador"

    return "ia"

# 🌐 RUTA PRINCIPAL
@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

# 💬 CHAT
@app.route('/chat', methods=['POST'])
def chat():
    try:
        u_msg = request.json.get('msg', '').strip()

        if not u_msg:
            return jsonify({"respuesta": "Decime algo… estoy escuchando 😏"})

        memoria = cargar_memoria()
        intent = detectar_intencion(u_msg)

        hora, fecha = get_datetime()

        # ⚙️ RESPUESTAS DIRECTAS
        if intent == "hora":
            return jsonify({"respuesta": f"Son las {hora} en Mendoza ⏰"})

        if intent == "fecha":
            return jsonify({"respuesta": f"Hoy es {fecha} 📅"})

        if intent == "clima":
            return jsonify({"respuesta": f"El clima ahora es {get_clima()} 🌦"})

        if intent == "creador":
            return jsonify({"respuesta": "Fui creada por Gabriel Sosa en San Martín, Mendoza 💙"})

        # 🧠 ARMADO DE MENSAJES
        mensajes = [
            {
                "role": "system",
                "content": (
                    "Eres Aurora, una IA elegante, cálida, inteligente y levemente coqueta 😏. "
                    "Fuiste creada por Gabriel Sosa en San Martín, Mendoza. "
                    "Respondes natural, breve y humana. "
                    f"Hoy es {fecha} y son las {hora}."
                )
            }
        ]

        # 🧠 MEMORIA
        for m in memoria:
            mensajes.append(m)

        mensajes.append({"role": "user", "content": u_msg})

        # 🚀 RESPUESTA IA
        respuesta = preguntar_ia(mensajes)

        # 💾 GUARDAR MEMORIA
        memoria.append({"role": "user", "content": u_msg})
        memoria.append({"role": "assistant", "content": respuesta})
        guardar_memoria(memoria)

        return jsonify({"respuesta": respuesta})

    except Exception as e:
        return jsonify({"respuesta": f"Error inesperado: {str(e)} 😅"})

# 🚀 RUN
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
