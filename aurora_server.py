from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, requests, base64

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

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
        
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            return jsonify({"respuesta": "ERROR: Me falta la llave GEMINI_API_KEY en Render.", "audio": None})
            
        # 🚀 MODELO 2026: Gemini 3 Flash
        # Usamos la versión v1beta que es donde siempre están los modelos más nuevos
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={gemini_api_key}"
        
        gemini_payload = {"contents": [{"role": "user", "parts": [{"text": u_msg}]}]}
        res = requests.post(gemini_url, json=gemini_payload, timeout=10)
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"ERROR DE GOOGLE (URL: {gemini_url}): {res.text}", "audio": None})
            
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']

        # --- ELEVENLABS ---
        elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY")
        audio_b64 = None
        if elevenlabs_api_key:
            voice_id = "EXAVITQu4vr4xnSDxMaL"
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": elevenlabs_api_key}
            tts_payload = {"text": txt, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
            tts_res = requests.post(tts_url, json=tts_payload, headers=headers, timeout=15)
            if tts_res.status_code == 200:
                audio_b64 = base64.b64encode(tts_res.content).decode('utf-8')

        return jsonify({"respuesta": txt, "audio": audio_b64})
        
    except Exception as e:
        return jsonify({"respuesta": f"ERROR DEL SERVIDOR: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
