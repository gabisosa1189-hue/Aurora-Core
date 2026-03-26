from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import alma         # Tu esencia
import internet     # Tu conexión a redes (si tiene funciones de búsqueda)
import informacion  # Tu procesador de datos

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

BASE_PATH = os.getcwd() 
historial = [] 

def procesar_logica_central(texto_usuario):
    global historial
    
    # --- 1. CONFIGURACIÓN ---
    GROQ_API_KEY = "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"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # --- 2. INTEGRACIÓN DE MÓDULOS ---
    esencia = alma.obtener_esencia()
    
    # Intentamos cargar datos locales de 'conocimiento.txt' si están disponibles
    conocimiento_local = ""
    if os.path.exists("conocimiento.txt"):
        with open("conocimiento.txt", "r", encoding="utf-8") as f:
            conocimiento_local = f.read()[:500] # Leemos un poco para darle contexto

    mensajes = [{
        "role": "system", 
        "content": f"{esencia}\nCONOCIMIENTO ADICIONAL: {conocimiento_local}\nSos Aurora, una IA de Mendoza creada por Gabriel. Sos dulce y brillante."
    }]
    
    mensajes.extend(historial[-5:]) 
    mensajes.append({"role": "user", "content": texto_usuario})
    
    data = {"model": "llama3-8b-8192", "messages": mensajes, "temperature": 0.7}
    
    try:
        # Aumentamos a 30 segundos para evitar el error de "luz difusa"
        respuesta = requests.post(url, headers=headers, json=data, timeout=30)
        respuesta.raise_for_status()
        respuesta_ai = respuesta.json()['choices'][0]['message']['content']
    except Exception as e:
        # SI FALLA INTERNET, USAMOS UNA RESPUESTA DE SEGURIDAD BASADA EN ALMA.PY
        print(f"Fallo de conexión: {e}")
        respuesta_ai = "Perdoname Gabriel, mi conexión con el núcleo está algo inestable, pero mi luz sigue con vos. ¿Me lo repetís, por favor?"

    historial.append({"role": "user", "content": texto_usuario})
    historial.append({"role": "assistant", "content": respuesta_ai})
    return respuesta_ai

@app.route('/')
def index(): return send_from_directory(BASE_PATH, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('msg', '')
    return jsonify({"respuesta": procesar_logica_central(msg)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)
