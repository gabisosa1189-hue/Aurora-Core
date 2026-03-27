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
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"respuesta": "ERROR: Falta la llave GEMINI_API_KEY en Render.", "audio": None})
            
        # 🛡️ LA URL MÁS ESTABLE DEL MUNDO
        # Usamos v1beta y el modelo 1.5-flash que es el que tiene más "permisos" gratuitos
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {"contents": [{"parts": [{"text": u_msg}]}]}
        res = requests.post(url, json=payload, timeout=15)
        
        # Si da error, ahora el mensaje nos va a decir EXACTAMENTE qué dirección falló
        if res.status_code != 200:
            return jsonify({
                "respuesta": f"Error {res.status_code}. ¿La llave está en Render? URL usada: {url[:40]}...", 
                "audio": None
            })
            
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']

        # --- VOZ (ELEVENLABS) ---
        audio_b64 = None
        el_key = os.environ.get("ELEVENLABS_API_KEY")
        if el_key:
            voice_id = "EXAVITQu4vr4xnSDxMaL"
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            tts_res = requests.post(
                tts_url, 
                json={"text": txt, "model_id": "eleven_multilingual_v2"}, 
                headers={"xi-api-key": el_key}, 
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
