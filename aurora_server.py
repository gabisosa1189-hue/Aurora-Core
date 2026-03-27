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
        
        # 1. EL CEREBRO (GEMINI) PIENSA LA RESPUESTA
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={gemini_api_key}"
        gemini_payload = {"contents": [{"role": "user", "parts": [{"text": u_msg}]}]}
        res = requests.post(gemini_url, json=gemini_payload, timeout=10)
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']

        # 2. LAS CUERDAS VOCALES (ELEVENLABS) CREAN EL MP3 EN VIVO
        elevenlabs_api_key = os.environ.get("ELEVENLABS_API_KEY") # 🚨 NUEVA LLAVE
        
        # ID de voz dulce femenina (Ej: Bella o Rachel en ElevenLabs)
        voice_id = "EXAVITQu4vr4xnSDxMaL" # Voz dulce por defecto
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": elevenlabs_api_key
        }
        tts_payload = {
            "text": txt,
            "model_id": "eleven_multilingual_v2", # Habla perfecto español
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        audio_b64 = None
        # Solo generamos audio si tenemos la llave puesta en Render
        if elevenlabs_api_key:
            tts_res = requests.post(tts_url, json=tts_payload, headers=headers, timeout=15)
            if tts_res.status_code == 200:
                # Convertimos el MP3 a código para mandarlo a la web
                audio_b64 = base64.b64encode(tts_res.content).decode('utf-8')

        # Devolvemos el texto Y el audio
        return jsonify({
            "respuesta": txt,
            "audio": audio_b64
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"respuesta": "Aurora procesando conexión...", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
