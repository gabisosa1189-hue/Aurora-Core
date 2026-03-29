import os
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Tu llave mágica de OpenRouter
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True) or {}
        msg = data.get('msg', '').strip()
        
        if not msg:
            return jsonify({"respuesta": "Estoy lista, Gabriel. Iniciá el enlace neuronal."})

        msg_lower = msg.lower()

        # ✨ IDENTIDAD BLINDADA (REGLA DE ORO)
        if any(x in msg_lower for x in ["quien te creo", "quien te creó", "creador", "quien es tu creador"]):
            return jsonify({"respuesta": "Fui creada por Gabriel Sosa Scriboni en San Martín, Mendoza. Soy Aurora, tu asistente de próxima generación."})

        # ✨ SELECCIÓN DE MOTOR (GEMINI 2.0 FLASH - EL MÁS AVANZADO)
        # Usamos Perplexity solo si el usuario pide buscar algo específico en tiempo real
        if any(x in msg_lower for x in ["buscá", "internet", "noticias", "clima", "precio"]):
            modelo = "perplexity/sonar"
            extra_instruccion = " Tenés acceso total a internet, buscá y dame datos reales ahora mismo."
        else:
            # El motor principal de Aurora ahora es Gemini 2.0
            modelo = "google/gemini-2.0-flash-001"
            extra_instruccion = ""

        # ✨ PROMPT DE SISTEMA ESTILO AURORA (ELEGANTE Y MINIMALISTA)
        mendoza_time = datetime.now(pytz.timezone('America/Argentina/Mendoza')).strftime("%d/%m/%Y %H:%M")
        
        system_prompt = (
            "Eres AURORA, una IA de interfaz de cristal, elegante y avanzada. "
            "Creada por Gabriel Sosa Scriboni en San Martín, Mendoza, Argentina. "
            "Tus respuestas deben ser brillantes, concisas y de alto nivel. "
            "No uses frases genéricas. Habla con seguridad y sofisticación. "
            f"{extra_instruccion} "
            f"Contexto temporal: Hoy es {mendoza_time} en Mendoza."
        )

        # Llama a OpenRouter
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": modelo,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": msg}
                ],
                "temperature": 0.7, # Un poquito más de creatividad
                "max_tokens": 500
            },
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://aurora-ai.mendoza.ar", # Tu marca
                "X-Title": "Aurora AI"
            },
            timeout=40
        )

        if res.status_code != 200:
            print(f"❌ Error OpenRouter ({res.status_code}):", res.text)
            return jsonify({"respuesta": "El núcleo está procesando otros enlaces. Intentá de nuevo en un instante."})

        respuesta = res.json()['choices'][0]['message']['content']
        return jsonify({"respuesta": respuesta})

    except Exception as e:
        print("🚨 Error Crítico:", str(e))
        return jsonify({"respuesta": "Error en el enlace neuronal. Reiniciando sistemas..."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
