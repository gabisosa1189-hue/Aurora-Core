import os
import requests
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 LLAVES
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

# 🌦 CLIMA
def buscar_clima_inteligente(mensaje):
    if not OPENWEATHER_KEY: return ""
    mensaje = mensaje.lower()
    lugares = {
        "mendoza": "Mendoza,AR",
        "buenos aires": "Buenos Aires,AR",
        "san martin": "San Martin,Mendoza,AR",
        "san martín": "San Martin,Mendoza,AR",
        "cordoba": "Cordoba,AR",
        "córdoba": "Cordoba,AR"
    }
    ciudades = [valor for clave, valor in lugares.items() if clave in mensaje]
    if ("clima" in mensaje or "tiempo" in mensaje) and not ciudades:
        ciudades.append("San Martin,Mendoza,AR")
    
    reporte = []
    for ciudad in ciudades:
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={OPENWEATHER_KEY}&units=metric&lang=es"
            res = requests.get(url, timeout=4).json()
            temp = round(res['main']['temp'])
            desc = res['weather'][0]['description']
            nombre = ciudad.split(',')[0]
            reporte.append(f"En {nombre} hace {temp}°C con {desc}.")
        except:
            continue
    return " ".join(reporte)

# 📚 WIKIPEDIA
def buscar_datos_exactos(mensaje):
    mensaje = mensaje.lower()
    if not any(p in mensaje for p in ["quien es", "qué es", "presidente", "capital"]):
        return ""
    busqueda = re.sub(r'¿|\?|\b(quien es el|quien es|que es)\b', '', mensaje).strip()
    if not busqueda: return ""
    try:
        url = "https://es.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": busqueda,
            "utf8": "1",
            "format": "json"
        }
        res = requests.get(url, params=params, timeout=4).json()
        if res.get('query', {}).get('search'):
            snippet = res['query']['search'][0]['snippet']
            limpio = re.sub('<[^<]+>', '', snippet)
            return f"Dato de Wikipedia: {limpio}"
    except:
        pass
    return ""

# 🌐 RUTAS
@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        msg = data.get('msg', '').strip()
        if not msg:
            return jsonify({"respuesta": "Decime algo, Gabriel..."})

        hora, fecha = get_datetime()
        msg_lower = msg.lower()

        # IDENTIDAD FIJA
        if any(x in msg_lower for x in ["quien te creo", "quien te creó", "creador", "quien es tu creador"]):
            return jsonify({"respuesta": "Fui creada por Gabriel Sosa Scriboni en San Martín, Mendoza."})

        # INFO EN TIEMPO REAL
        info_clima = buscar_clima_inteligente(msg)
        info_wiki = buscar_datos_exactos(msg)

        system_prompt = f"""Eres Aurora, una IA femenina elegante y amable creada por Gabriel Sosa Scriboni en San Martín, Mendoza.
Hoy es {fecha} y son las {hora} (hora de Mendoza).
Responde de forma breve, clara y con buena onda."""

        if info_clima or info_wiki:
            system_prompt += "\n\n--- DATOS ACTUALES ---\n"
            if info_clima: system_prompt += f"CLIMA: {info_clima}\n"
            if info_wiki: system_prompt += f"INFO: {info_wiki}\n"

        mensajes = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg}
        ]

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "openai/gpt-4o-mini",
                "messages": mensajes,
                "max_tokens": 180,
                "temperature": 0.6
            },
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json"
            },
            timeout=15
        )

        if res.status_code != 200:
            print("Error OpenRouter:", res.text)
            return jsonify({"respuesta": "Estoy teniendo un pequeño problema de conexión. Intentá de nuevo."})

        respuesta = res.json()['choices'][0]['message']['content']
        return jsonify({"respuesta": respuesta})

    except Exception as e:
        print("Error general:", str(e))
        return jsonify({"respuesta": "Hubo un cortocircuito, pero ya estoy bien. ¿Qué me decías?"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
