import os, requests, base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 LLAVES (Sacalas de Environment en Render)
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

        # 🚀 MODELO ESTABLE (2.0 Flash no falla en v1)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={API_KEY}"

        payload = {
            "contents": [{
                "parts": [{"text": 
                    f"Eres Aurora, una IA femenina elegante y amable creada por Gabriel Sosa Scriboni en San Martín, Mendoza.\n\n"
                    f"Reglas:\n"
                    f"- Si te preguntan quién te creó, responde: 'Fui creada por Gabriel Sosa Scriboni en San Martín, Mendoza.'\n"
                    f"- Responde de forma breve, clara y educada.\n"
                    f"- Tono cálido pero maduro.\n\n"
                    f"Usuario dice: {u_msg}"
                }]
            }]
        }

        res = requests.post(url, json=payload, timeout=15)

        if res.status_code != 200:
            # Esto nos dirá qué dice Google exactamente si falla
            return jsonify({"respuesta": f"Error de Google: {res.status_code}", "audio": None})

        data = res.json()
        txt = data['candidates'][0]['content']['parts'][0]['text']

        # --- 🎤 MOTOR DE VOZ (Opcional) ---
        audio_b64 = None
        if ELEVEN_KEY:
            voice_id = "EXAVITQu4vr4xnSDxMaL" # Tu ID de voz
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            tts_res = requests.post(
                tts_url,
                json={"text": txt, "model_id": "eleven_multilingual_v2"},
                headers={"xi-api-key": ELEVEN_KEY},
                timeout=15
            )
            if tts_res.status_code == 200:
                audio_b64 = base64.b64encode(tts_res.content).decode('utf-8')

        return jsonify({"respuesta": txt, "audio": audio_b64})

    except Exception as e:
        return jsonify({"respuesta": f"Error interno: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
