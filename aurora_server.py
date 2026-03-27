import os, requests, base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import pytz # Para la hora exacta de Mendoza

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 LLAVES
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        u_msg = request.json.get('msg', '').strip()
        if not u_msg:
            return jsonify({"respuesta": "No recibí mensaje.", "audio": None})

        # 🕒 CALCULAMOS LA HORA DE MENDOZA
        tz_mza = pytz.timezone('America/Argentina/Mendoza')
        hora_actual = datetime.now(tz_mza).strftime("%H:%M")
        fecha_actual = datetime.now(tz_mza).strftime("%d/%m/%Y")

        # 🚀 URL DE GOOGLE (v1beta tiene mejor soporte para herramientas)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

        # 📦 PAYLOAD CON GOOGLE SEARCH (Herramientas)
        payload = {
            "contents": [{
                "parts": [{"text": 
                    f"Eres Aurora, una IA elegante creada por Gabriel Sosa Scriboni en San Martín, Mendoza.\n"
                    f"INFO REAL: Hoy es {fecha_actual} y son las {hora_actual} en Mendoza.\n"
                    f"INSTRUCCIÓN: Si el usuario pregunta por noticias, presidentes o datos actuales, USA GOOGLE SEARCH.\n"
                    f"REGLA: Responde siempre de forma breve y cálida.\n\n"
                    f"Usuario dice: {u_msg}"
                }]
            }],
            "tools": [{"google_search_retrieval": {}}] # 🔍 AQUÍ ACTIVAMOS GOOGLE
        }

        res = requests.post(url, json=payload, timeout=25)

        if res.status_code != 200:
            return jsonify({"respuesta": f"Error de conexión (Código: {res.status_code}). Intentá de nuevo, Gabriel.", "audio": None})

        data = res.json()
        # El texto puede venir en 'content' o como respuesta de la herramienta
        txt = data['candidates'][0]['content']['parts'][0]['text']

        # --- 🎤 VOZ (Opcional) ---
        audio_b64 = None
        if ELEVEN_KEY:
            voice_id = "EXAVITQu4vr4xnSDxMaL"
            tts_res = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                json={"text": txt, "model_id": "eleven_multilingual_v2"},
                headers={"xi-api-key": ELEVEN_KEY},
                timeout=20
            )
            if tts_res.status_code == 200:
                audio_b64 = base64.b64encode(tts_res.content).decode('utf-8')

        return jsonify({"respuesta": txt, "audio": audio_b64})

    except Exception as e:
        return jsonify({"respuesta": f"Hubo un desliz técnico: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
