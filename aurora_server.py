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
        
        # 📡 RADAR TOTAL: Si detecta cualquiera de estas, activa INTERNET
        keywords = [
            "clima", "tiempo", "hora", "hoy", "ayer", "noticia", "dolar", "dólar", 
            "partido", "futbol", "fútbol", "jugó", "jugo", "ganó", "gano", "resultado", 
            "argentina", "quien", "quién", "pasó", "paso", "messi", "celebridad", 
            "famoso", "actualidad", "ahora", "precio", "mendoza", "san martin"
        ]
        
        # Decidimos qué cerebro usar
        if any(k in msg_lower for k in keywords):
            # 🔍 EL INVESTIGADOR (Perplexity Sonar - El mejor para tiempo real)
            modelo_a_usar = "perplexity/sonar"
            prompt_sistema = (
                "Eres Aurora, una IA mendocina con ACCESO TOTAL a internet en tiempo real. "
                "Hoy es sábado 28 de marzo de 2026. Tu misión es BUSCAR en Google, Wikipedia y noticias. "
                "Si te preguntan por deportes, da resultados exactos. Si es sobre famosos o clima, da la data actual. "
                "No digas que no tienes acceso. ¡Busca y responde con la posta!"
            )
        else:
            # 💬 EL JEFE (GPT-4o mini - Rápido para charla casual)
            modelo_a_usar = "openai/gpt-4o-mini"
            prompt_sistema = "Eres Aurora, una IA amable y mendocina creada por Gabriel Sosa Scriboni en San Martín."

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": modelo_a_usar,
                "messages": [
                    {"role": "system", "content": prompt_sistema}, 
                    {"role": "user", "content": msg}
                ],
                "temperature": 0.2 
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=35 # Le damos tiempo para que googlee bien
        )
        
        respuesta_final = res.json()['choices'][0]['message']['content']
        return jsonify({"respuesta": respuesta_final})

    except Exception as e:
        return jsonify({"respuesta": "Error de conexión neuronal... ¡Probá de nuevo en un toque!"})
