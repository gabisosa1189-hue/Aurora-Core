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
        
        msg_minusculas = msg.lower()
        # Ampliamos el radar para que no se le escape nada de hoy
        palabras_clave = ["clima", "tiempo", "hora", "noticia", "hoy", "precio", "dólar", "dolar", "internet", "actual", "busca", "partido", "jugo", "gano", "resultado", "argentina", "futbol", "fútbol"]
        
        necesita_internet = any(palabra in msg_minusculas for palabra in palabras_clave)
        
        if necesita_internet:
            modelo_a_usar = "perplexity/sonar"
            # PROMPT REFORZADO: Le decimos que SEA un buscador total
            prompt_sistema = "Eres Aurora, una IA con acceso total a internet en tiempo real. Tu misión es buscar en la web y dar respuestas precisas sobre noticias, deportes (fútbol), clima y actualidad de hoy. Habla con tono amable y mendocino."
        else:
            modelo_a_usar = "openai/gpt-4o-mini"
            prompt_sistema = "IA amable y mendocina creada por Gabriel Sosa Scriboni de San Martín, Mendoza."

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": modelo_a_usar,
                "messages": [
                    {"role": "system", "content": prompt_sistema}, 
                    {"role": "user", "content": msg}
                ]
            },
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            timeout=30
        )
        return jsonify({"respuesta": res.json()['choices'][0]['message']['content']})
    except Exception as e:
        return jsonify({"respuesta": "Error de conexión neuronal..."})
