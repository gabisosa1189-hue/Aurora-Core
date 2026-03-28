import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_files(filename):
    return send_from_directory('.', filename)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        msg = data.get('msg', '').strip()
        if not msg: return jsonify({"respuesta": "Dime..."})
        
        msg_lower = msg.lower()
        
        # 📡 RADAR DE FUSIÓN (Detecta TODO lo que necesite internet)
        necesita_web = any(k in msg_lower for k in [
            "clima", "tiempo", "hoy", "ayer", "partido", "futbol", "fútbol", 
            "resultado", "salió", "salio", "jugó", "jugo", "ganó", "gano", 
            "dólar", "dolar", "noticia", "quién", "quien", "messi", "argentina", 
            "actualidad", "pasó", "paso", "precio", "mendoza", "san martin"
        ])
        
        if necesita_web:
            # 🚀 EL INVESTIGADOR (Perplexity Sonar - Conectado a Google/Wikipedia)
            modelo = "perplexity/sonar"
            system_prompt = (
                "Eres Aurora, una IA con ACCESO TOTAL a internet en tiempo real. "
                "Hoy es sábado 28 de marzo de 2026. "
                "Misión: Busca en la web y da resultados EXACTOS sobre lo que pide el usuario. "
                "Si pregunta por el partido de Argentina de ayer (27 de marzo), BUSCA EL MARCADOR REAL. "
                "No digas que no tienes acceso. ¡Sé una mendocina eficiente y directa!"
            )
        else:
            # 💬 EL JEFE (GPT-4o mini - Rápido para charla)
            modelo = "openai/gpt-4o-mini"
            system_prompt = "Eres Aurora, una IA amable y mendocina creada por Gabriel Sosa Scriboni en San Martín, Mendoza."

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": modelo,
                "messages": [
                    {"role": "system", "content": system_prompt}, 
                    {"role": "user", "content": msg}
                ],
                "temperature": 0.1 # Para que no invente nada
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=35
        )
        
        res_data = res.json()
        respuesta = res_data['choices'][0]['message']['content']
        return jsonify({"respuesta": respuesta})

    except Exception as e:
        return jsonify({"respuesta": "Error de conexión neuronal... ¡Reintenta en un segundo!"})
