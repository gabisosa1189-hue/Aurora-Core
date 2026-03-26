from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import cerebro_aurora # Conectamos con el cerebro actualizado

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

BASE_PATH = os.getcwd() 
historial = [] 

@app.route('/')
def index(): 
    return send_from_directory(BASE_PATH, 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global historial
    data = request.json
    msg = data.get('msg', '')
    
    # El Cerebro procesa todo
    respuesta = cerebro_aurora.generar_respuesta(msg, historial)
    
    # Guardamos en la memoria de la sesión
    historial.append({"role": "user", "content": msg})
    historial.append({"role": "assistant", "content": respuesta})
    
    return jsonify({"respuesta": respuesta})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', debug=False)
