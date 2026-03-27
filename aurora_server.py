import os, requests, base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 LLAVES (Sacalas de la pestaña Environment de Render)
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
EL_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        
        if not API_KEY:
            return jsonify({"respuesta": "Falta la llave GEMINI_API_KEY en Render.", "audio": None})

        # 🚀 ESTRATEGIA DE TRIPLE INTENTO (Para matar el Error 404)
        # Probamos diferentes modelos y versiones hasta que uno ande
        modelos_a_probar = [
            "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent"
        ]
        
        txt = None
        error_final = ""

        for url in modelos_a_probar:
            res = requests.post(f"{url}?key={API_KEY}", 
                                json={"contents": [{"parts": [{"text": f"Sos Aurora, una IA de Mendoza. Respondé corto: {u_msg}"}]}]}, 
                                timeout=10)
            if res.status_code == 200:
                txt = res.json()['candidates'][0]['content']['parts'][0]['text']
                break # ¡LO LOGRAMOS! Salimos del bucle
            else:
                error_final = res.text

        if not txt:
            return jsonify({"respuesta": f"Google sigue rechazando: {error_final}", "audio": None})

        # --- VOZ: ELEVENLABS ---
        audio_b64 = None
        if EL_KEY:
            # Tu Voice ID de ElevenLabs
            voice_id = "EXAVITQu4vr4xnSDxMaL" 
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            tts_res = requests.post(
                tts_url,
                json={"text": txt, "model_id": "eleven_multilingual_v2"},
                headers={"xi-api-key": EL_KEY},
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
