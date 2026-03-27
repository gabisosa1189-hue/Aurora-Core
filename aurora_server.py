import os, requests, base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 LLAVES (Asegurate que en Render diga GEMINI_API_KEY)
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        
        if not API_KEY:
            return jsonify({"respuesta": "❌ Error: No encontré la llave en Render.", "audio": None})

        # 🚀 LA RUTA QUE NO FALLA (v1 estable)
        # Cambiamos v1beta por v1 y usamos gemini-1.5-flash-latest
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": u_msg}]
            }]
        }
        
        res = requests.post(url, json=payload, timeout=15)
        
        # Si vuelve a dar error, que nos diga exactamente qué pasó
        if res.status_code != 200:
            error_detail = res.json().get('error', {}).get('message', 'Error desconocido')
            return jsonify({"respuesta": f"Google dice: {error_detail}", "audio": None})
            
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']

        # --- VOZ: ELEVENLABS ---
        audio_b64 = None
        if ELEVEN_KEY:
            voice_id = "EXAVITQu4vr4xnSDxMaL"
            tts_res = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                json={"text": txt, "model_id": "eleven_multilingual_v2"},
                headers={"xi-api-key": ELEVEN_KEY},
                timeout=15
            )
            if tts_res.status_code == 200:
                audio_b64 = base64.b64encode(tts_res.content).decode('utf-8')

        return jsonify({"respuesta": txt, "audio": audio_b64})
        
    except Exception as e:
        return jsonify({"respuesta": f"Error del servidor: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
