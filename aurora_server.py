from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, base64

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# =========================================================
# 🔑 TUS LLAVES (Usa llaves NUEVAS, las anteriores ya son públicas y peligrosas)
# =========================================================
GOOGLE_KEY = "TU_NUEVA_LLAVE_AQUÍ"
ELEVEN_KEY = "TU_NUEVA_LLAVE_AQUÍ"
# =========================================================

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        
        # 🚀 DIRECCIÓN ESTABLE 2026 (v1 + gemini-2.0-flash)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GOOGLE_KEY}"
        
        payload = {"contents": [{"parts": [{"text": u_msg}]}]}
        res = requests.post(url, json=payload, timeout=15)
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"Google dice error {res.status_code}: {res.text}", "audio": None})
            
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']

        # --- VOZ (ELEVENLABS) ---
        audio_b64 = None
        if ELEVEN_KEY and "TU_NUEVA" not in ELEVEN_KEY:
            voice_id = "EXAVITQu4vr4xnSDxMaL"
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            # Ajustamos para máxima calidad en español
            tts_payload = {
                "text": txt,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
            }
            
            tts_res = requests.post(tts_url, json=tts_payload, headers={"xi-api-key": ELEVEN_KEY}, timeout=15)
            
            if tts_res.status_code == 200:
                audio_b64 = base64.b64encode(tts_res.content).decode('utf-8')

        return jsonify({"respuesta": txt, "audio": audio_b64})
        
    except Exception as e:
        return jsonify({"respuesta": f"Error crítico: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
