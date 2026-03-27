import os, requests, base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 RECOGEMOS LAS LLAVES DE RENDER
# Verificá que en 'Environment' se llamen exactamente así
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()

        if not GEMINI_KEY:
            return jsonify({"respuesta": "Falta la llave GEMINI_API_KEY en Render.", "audio": None})

        # 🚀 LA RUTA QUE NO FALLA (v1beta + gemini-1.5-flash a secas)
        # En 2026, 'v1' es muy mañosa con los nombres. 'v1beta' es la que va.
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": f"Sos Aurora, una IA de Mendoza. Sé breve y amable. Respondé esto: {u_msg}"}]
            }]
        }
        
        res = requests.post(url, json=payload, timeout=15)
        
        # Si Google nos rebota, queremos ver el motivo real
        if res.status_code != 200:
            error_info = res.json().get('error', {}).get('message', 'Error desconocido')
            return jsonify({"respuesta": f"Google dice: {error_info}", "audio": None})
            
        # Extraemos el texto de la respuesta
        txt = res.json()['candidates'][0]['content']['parts'][0]['text']

        # --- VOZ (ELEVENLABS) ---
        audio_b64 = None
        if ELEVEN_KEY:
            voice_id = "EXAVITQu4vr4xnSDxMaL" # Tu ID de voz de ElevenLabs
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
        return jsonify({"respuesta": f"Error crítico: {str(e)}", "audio": None})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
