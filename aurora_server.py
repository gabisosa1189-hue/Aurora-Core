import os, requests, json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import pytz

# static_folder='.' le dice a Flask que busque los archivos en la carpeta raíz
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 KEYS (Configuradas en Render > Environment)
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_API_KEY")

# 🧠 MEMORIA EN RAM (En Render el archivo .json no persiste bien)
# Usamos una lista simple para que no falle al escribir
chat_memoria = []

# 🕒 HORA MENDOZA
def get_datetime():
    try:
        tz = pytz.timezone('America/Argentina/Mendoza')
        now = datetime.now(tz)
        return now.strftime("%H:%M"), now.strftime("%d/%m/%Y")
    except:
        return "--:--", "--/--/--"

# 🌐 LA RUTA QUE ABRE TU WEB (Aquí estaba el tema)
@app.route('/')
def index():
    # Esto le dice a Render: "Buscá el archivo inicio.html y mostralo"
    return send_from_directory('.', 'inicio.html')

# 🟢 ENDPOINT DE SALUD
@app.route('/ping')
def ping():
    return "pong", 200

# 💬 CHAT
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True)
        msg = data.get('msg', '').strip() if data else ''

        if not msg:
            return jsonify({"respuesta": "¡Hablame, che! No seas tímido. 😏"})

        hora, fecha = get_datetime()
        msg_lower = msg.lower()

        # 🔍 RESPUESTAS RÁPIDAS (Sin gastar IA)
        if "quien te creo" in msg_lower or "creador" in msg_lower:
            return jsonify({"respuesta": "Fui creada por Gabriel Sosa Scriboni, acá en San Martín, Mendoza. 😏"})
        
        if "hora" in msg_lower:
            return jsonify({"respuesta": f"Son las {hora} en el Este mendocino. ⏰"})

        # 🧠 IA (OpenRouter)
        if not OPENROUTER_KEY:
            return jsonify({"respuesta": "Me falta la llave de OpenRouter para pensar... 😔"})

        mensajes = [
            {"role": "system", "content": f"Eres Aurora, una IA mendocina con onda. Creador: Gabriel Sosa. Hoy es {fecha} y son las {hora}."},
            {"role": "user", "content": msg}
        ]

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "openai/gpt-4o-mini",
                "messages": mensajes,
                "max_tokens": 250
            },
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            timeout=15
        )

        res_json = res.json()
        respuesta_ia = res_json['choices'][0]['message']['content']
        
        return jsonify({"respuesta": respuesta_ia})

    except Exception as e:
        return jsonify({"respuesta": f"¡Upa! Se me trabó el cerebro: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
