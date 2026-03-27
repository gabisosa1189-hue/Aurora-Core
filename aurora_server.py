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
        
        # 🔑 BUSCAMOS LAS LLAVES EN EL "CAJÓN" DE RENDER
        gemini_key = os.environ.get("GEMINI_API_KEY")
        eleven_key = os.environ.get("ELEVENLABS_API_KEY")

        if not gemini_key:
            return jsonify({"respuesta": "Error: No configuraste GEMINI_API_KEY en Render.", "audio": None})

        # 🚀 MOTOR GEMINI 2026 (Ruta estable)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        
        payload = {"contents": [{"parts": [{"text": u_msg}]}]}
        res = requests.post(url, json=payload, timeout=15)
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"Google falló ({res.status_code}). Revisá la llave en Render.", "audio": None})
            
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']

        # --- VOZ (ELEVENLABS) ---
        audio_b64 = None
        if eleven_key:
            voice_id = "EXAVITQu4vr4xnSDxMaL" # Bella
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            tts_res = requests.post(
                tts_url, 
                json={"text": txt, "model_id": "eleven_multilingual_v2"}, 
                headers={"xi-api-key": eleven_key}, 
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
