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
        
        # 1. LLAVE DE SEGURIDAD
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            return jsonify({"respuesta": "ERROR: Falta la clave GEMINI_API_KEY en Render.", "audio": None})
            
        # 2. CONFIGURACIÓN GEMINI 3 FLASH (2026 Standard)
        # Importante: v1beta es la única que reconoce al modelo 3 Flash actualmente
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={gemini_api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": u_msg}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 800
            }
        }
        
        res = requests.post(gemini_url, json=payload, timeout=15)
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"Error de Google ({res.status_code}): {res.text}", "audio": None})
            
        res_json = res.json()
        txt = res_json['candidates'][0]['content']['parts'][0]['text']

        # 3. VOZ DE ELEVENLABS
        audio_b64 = None
        el_key = os.environ.get("ELEVENLABS_API_KEY")
        
        if el_key:
            voice_id = "EXAVITQu4vr4xnSDxMaL" # Voz de Bella
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            tts_payload = {
                "text": txt,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
            }
            tts_res = requests.post(tts_url, json=tts_payload, headers={"xi-api-key": el_key}, timeout=20)
            
            if tts_res.status_code == 200:
                audio_b64 = base64.b64encode(tts_res.content).decode('utf-8')
            else:
                txt += f" (Nota: Mi voz falló, pero aquí estoy: {tts_res.status_code})"

        return jsonify({"respuesta": txt, "audio": audio_b64})
        
    except Exception as e:
        return jsonify({"respuesta": f"Error crítico: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
