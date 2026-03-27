from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, base64

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# =========================================================
# 🔑 PEGÁ TUS LLAVES ACÁ (ADENTRO DE LAS COMILLAS)
# =========================================================
GEMINI_API_KEY = "AIzaSyADiRyFwBo-pnbLLHDNZFzUiy68HIviNLo"
ELEVENLABS_API_KEY = "030a3ba3598741ba9e2d57722b1d2db7"
# =========================================================

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        
        # 🚀 URL ESTABLE PARA GEMINI 1.5 (La que no falla)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        res = requests.post(url, json={"contents": [{"parts": [{"text": u_msg}]}]}, timeout=15)
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"Error: Revisá que la llave esté bien pegada.", "audio": None})
            
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']

        # --- VOZ ---
        audio_b64 = None
        if ELEVENLABS_API_KEY and "PEGA_AQUI" not in ELEVENLABS_API_KEY:
            voice_id = "EXAVITQu4vr4xnSDxMaL"
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            tts_res = requests.post(
                tts_url, 
                json={"text": txt, "model_id": "eleven_multilingual_v2"}, 
                headers={"xi-api-key": ELEVENLABS_API_KEY}, 
                timeout=15
            )
            if tts_res.status_code == 200:
                audio_b64 = base64.b64encode(tts_res.content).decode('utf-8')

        return jsonify({"respuesta": txt, "audio": audio_b64})
        
    except Exception as e:
        return jsonify({"respuesta": f"Error: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
