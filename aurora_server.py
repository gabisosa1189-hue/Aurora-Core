import os, requests, base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# 🔑 BUSCAMOS LA LLAVE DE OPENAI (Asegurate que en Render se llame así)
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()

@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()

        if not OPENAI_KEY:
            return jsonify({"respuesta": "❌ Error: No encontré la variable OPENAI_API_KEY en Render.", "audio": None})

        # 🚀 CEREBRO: OPENAI (ChatGPT - GPT-4o-mini)
        # Este modelo es rapidísimo y muy barato.
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Sos Aurora, una IA de Mendoza. Sos amable, usás modismos mendocinos y ayudás a Gabriel con todo."},
                {"role": "user", "content": u_msg}
            ]
        }

        res = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if res.status_code != 200:
            return jsonify({"respuesta": f"OpenAI falló: {res.text}", "audio": None})

        txt = res.json()['choices'][0]['message']['content']

        # --- VOZ: ELEVENLABS ---
        audio_b64 = None
        if ELEVEN_KEY:
            voice_id = "EXAVITQu4vr4xnSDxMaL"
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            tts_res = requests.post(
                tts_url,
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
