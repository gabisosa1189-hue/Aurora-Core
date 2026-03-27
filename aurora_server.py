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
        
        # 🔑 LLAVES DESDE RENDER
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        el_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()

        if not api_key:
            return jsonify({"respuesta": "Falta GEMINI_API_KEY en Render.", "audio": None})

        # 🚀 LA DIRECCIÓN QUE NO FALLA EN 2026
        # Usamos v1 y el modelo 2.0 que es el estándar actual
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        payload = {"contents": [{"parts": [{"text": u_msg}]}]}
        
        res = requests.post(url, json=payload, timeout=15)
        
        # SI DA 404, VAMOS A BUSCAR QUÉ MODELOS TENÉS DISPONIBLES
        if res.status_code == 404:
            list_url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
            models_res = requests.get(list_url).json()
            return jsonify({
                "respuesta": f"Error 404: Google dice que ese modelo no existe. Modelos que podés usar: {models_res}",
                "audio": None
            })

        if res.status_code != 200:
            return jsonify({"respuesta": f"Google falló ({res.status_code}): {res.text}", "audio": None})
            
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']

        # --- VOZ ---
        audio_b64 = None
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
        return jsonify({"respuesta": f"Error crítico: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
