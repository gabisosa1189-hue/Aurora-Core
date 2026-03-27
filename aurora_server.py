import os, requests, base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 RECOGEMOS LAS LLAVES (Asegurate que se llamen así en Render)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()

        if not GEMINI_KEY:
            return jsonify({"respuesta": "Falta la llave GEMINI_API_KEY en Render.", "audio": None})

        # 🚀 ESTRATEGIA DE TRIPLE INTENTO (Anti-Error 404)
        # Probamos los modelos más nuevos y estables de 2026
        opciones = [
            {"ver": "v1beta", "mod": "gemini-2.0-flash"},
            {"ver": "v1beta", "mod": "gemini-1.5-flash"},
            {"ver": "v1", "mod": "gemini-1.5-flash"}
        ]
        
        txt = None
        ultimo_error = ""

        for opt in opciones:
            url = f"https://generativelanguage.googleapis.com/{opt['ver']}/models/{opt['mod']}:generateContent?key={GEMINI_KEY}"
            payload = {
                "contents": [{
                    "parts": [{"text": f"Sos Aurora, una IA de Mendoza. Sé breve y amable. Usuario dice: {u_msg}"}]
                }]
            }
            res = requests.post(url, json=payload, timeout=10)
            
            if res.status_code == 200:
                txt = res.json()['candidates'][0]['content']['parts'][0]['text']
                break
            else:
                ultimo_error = res.text

        if not txt:
            return jsonify({"respuesta": f"Google rechazó todos los modelos. Error: {ultimo_error}", "audio": None})

        # --- VOZ (ELEVENLABS) ---
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
        return jsonify({"respuesta": f"Error crítico: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
