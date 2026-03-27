from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, base64

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"respuesta": "Falta la llave GEMINI_API_KEY.", "audio": None})
            
        # 🛡️ MODELO 1.5 FLASH: El más estable para evitar el Error 429
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        res = requests.post(url, json={"contents": [{"parts": [{"text": u_msg}]}]}, timeout=10)
        
        if res.status_code == 429:
            return jsonify({"respuesta": "Aurora está descansando (Error 429). Esperá 1 minuto y volvé a intentar.", "audio": None})
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"Error de Google: {res.status_code}", "audio": None})
            
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']

        # --- VOZ (ELEVENLABS) ---
        audio_b64 = None
        el_key = os.environ.get("ELEVENLABS_API_KEY")
        if el_key:
            voice_id = "EXAVITQu4vr4xnSDxMaL"
            tts_res = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                json={"text": txt, "model_id": "eleven_multilingual_v2"},
                headers={"xi-api-key": el_key},
                timeout=15
            )
            if tts_res.status_code == 200:
                audio_b64 = base64.b64encode(tts_res.content).decode('utf-8')

        return jsonify({"respuesta": txt, "audio": audio_b64})
        
    except Exception as e:
        return jsonify({"respuesta": f"Error: {str(e)}", "audio": None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
