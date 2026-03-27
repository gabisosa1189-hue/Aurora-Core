from flask import Flask, request, jsonify, send_from_directory
import os, requests, datetime

app = Flask(__name__, static_folder='.')

# MEMORIA TEMPORAL
memoria_global = []

# 1. RUTA PARA EL VIDEO Y ARCHIVOS (INMORTAL)
@app.route('/<path:path>')
def servirlos(path):
    return send_from_directory('.', path)

# 2. RUTA PRINCIPAL
@app.route('/')
def index():
    return send_from_directory('.', 'inicio.html')

# 3. EL CHAT CON DETECTOR DE ERRORES
@app.route('/chat', methods=['POST'])
def chat():
    global memoria_global
    try:
        data = request.json
        u_msg = data.get('msg', '').strip()
        
        # BUSCAMOS LA LLAVE
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"respuesta": "ERROR: Falta la GEMINI_API_KEY en Render (Environment Variables)."})

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        
        # CONTEXTO SIMPLE PARA QUE NO FALLE NADA
        contexto = f"Eres Aurora, una IA avanzada de Mendoza. Hora actual: {datetime.datetime.now().strftime('%H:%M')}"
        
        payload = {
            "contents": [{"role": "user", "parts": [{"text": f"{contexto}\nUsuario: {u_msg}"}]}],
            "generationConfig": {"temperature": 0.7}
        }

        res = requests.post(url, json=payload, timeout=15)
        res_data = res.json()

        if res.status_code != 200:
            return jsonify({"respuesta": f"Error de Google: {res_data.get('error', {}).get('message', 'Desconocido')}"})

        txt_ai = res_data['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"respuesta": txt_ai})

    except Exception as e:
        # ESTO TE VA A DECIR EL ERROR REAL EN EL CHAT
        return jsonify({"respuesta": f"Error interno: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
