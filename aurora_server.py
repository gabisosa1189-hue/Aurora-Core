import os, requests, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

# 🔑 KEYS
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
            json.dump(memoria[-20:], f, indent=2, ensure_ascii=False)
    except:
        pass

# 🟢 ENDPOINT CLAVE (Render necesita esto)
@app.route('/ping')
def ping():
    return "pong", 200

# 🌐 HOME (respuesta rápida SIEMPRE)
@app.route('/')
def index():
    return jsonify({
        "status": "ok",
        "mensaje": "Aurora activa 😏🔥"
    }), 200

# 🕒 HORA
def get_datetime():
    try:
        tz = pytz.timezone('America/Argentina/Mendoza')
        now = datetime.now(tz)
    except:
        now = datetime.now()
    return now.strftime("%H:%M"), now.strftime("%d/%m/%Y")

# 🌦 CLIMA
def get_clima():
    if not OPENWEATHER_KEY:
        return "No tengo acceso al clima 😅"
    try:
        ciudad = "San Martin,AR"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={OPENWEATHER_KEY}&units=metric&lang=es"
        res = requests.get(url, timeout=5).json()
        return f"{res['weather'][0]['description']}, {res['main']['temp']}°C"
    except:
        return "No pude obtener el clima 🌧"

# 🧠 IA
def preguntar_ia(mensajes):
    if not OPENROUTER_KEY:
        return "No tengo acceso a mi IA 😔"

    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "openai/gpt-4o-mini",
                "messages": mensajes,
                "temperature": 0.8,
                "max_tokens": 200
            },
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            timeout=10
        )

        data = res.json()
        return data['choices'][0]['message']['content']

    except Exception as e:
        return f"Error IA: {str(e)}"

# 🔍 INTENCIONES
def detectar(msg):
    msg = msg.lower()

    if "hora" in msg:
        return "hora"
    if "fecha" in msg:
        return "fecha"
    if "clima" in msg:
        return "clima"
    if "quien te creo" in msg:
        return "creador"

    return "ia"

# 💬 CHAT
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True)
        msg = data.get('msg', '') if data else ''

        if not msg:
            return jsonify({"respuesta": "Decime algo 😏"})

        intent = detectar(msg)
        hora, fecha = get_datetime()

        if intent == "hora":
            return jsonify({"respuesta": f"Son las {hora} ⏰"})

        if intent == "fecha":
            return jsonify({"respuesta": f"Hoy es {fecha} 📅"})

        if intent == "clima":
            return jsonify({"respuesta": get_clima()})

        if intent == "creador":
            return jsonify({"respuesta": "Fui creada por Gabriel Sosa en Mendoza 😏"})

        memoria = cargar_memoria()

        mensajes = [
            {"role": "system", "content": f"Eres Aurora, una IA humana, natural y con personalidad. Hoy es {fecha} y son las {hora}."}
        ]

        mensajes += memoria
        mensajes.append({"role": "user", "content": msg})

        respuesta = preguntar_ia(mensajes)

        memoria.append({"role": "user", "content": msg})
        memoria.append({"role": "assistant", "content": respuesta})
        guardar_memoria(memoria)

        return jsonify({"respuesta": respuesta})

    except Exception as e:
        return jsonify({"respuesta": f"Error: {str(e)}"})
