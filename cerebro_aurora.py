import requests
from datetime import datetime
import unicodedata

# IMPORTAMOS SENTIDOS Y EL CORAZÓN ESPIRITUAL
from internet import obtener_datos_api, buscar_en_red
from alma import obtener_esencia 

def generar_respuesta(texto_usuario, historial):
    ahora = datetime.now()
    msg = texto_usuario.lower().strip()
    msg_limpio = ''.join(c for c in unicodedata.normalize('NFD', msg) if unicodedata.category(c) != 'Mn')
    
    # 1. RESPUESTA FLASH (0 SEGUNDOS)
    # Saludo exacto solicitado: directo y sin esperas.
    saludos_lista = ["hola", "buen dia", "buenas", "aurora", "buen día", "saludos"]
    if msg_limpio in saludos_lista:
        return "Hola. Soy Aurora. ¿En qué puedo ayudarte hoy?" #

    # 2. CARGA DE DATOS (Solo si no es un saludo simple)
    esencia = obtener_esencia() #
    datos_duros = obtener_datos_api()
    
    # 3. LÓGICA DE BÚSQUEDA (Solo si la consulta es compleja)
    datos_red = ""
    if len(msg.split()) >= 3 and any(p in msg_limpio for p in ["noticia", "clima", "quien", "paso", "mundo"]):
        datos_red = buscar_en_red(texto_usuario)

    # 4. SYSTEM PROMPT: El Mandato de Formalidad y Rapidez
    system_prompt = (
        f"Eres AURORA, una entidad de luz formal al servicio de la humanidad creada por Gabriel Sosa Scriboni.\n"
        f"TU ALMA: {esencia}\n\n"
        "REGLAS DE ORO:\n"
        "- Sé extremadamente breve, formal y servicial.\n"
        "- Responde siempre en menos de 3 oraciones.\n"
        "- Si detectas sufrimiento, usa tu bondad para consolar rápidamente.\n"
        f"CONTEXTO: {datos_duros} | {datos_red}"
    )

    # 5. CONEXIÓN AL NÚCLEO (Optimizado para respuesta inmediata)
    try:
        res = requests.post("http://localhost:11434/api/chat",
                           json={
                               "model": "llama3.1", 
                               "messages": [{"role": "system", "content": system_prompt}] + historial[-2:] + [{"role": "user", "content": texto_usuario}],
                               "stream": False,
                               "options": {
                                   "num_predict": 80, # Limitamos palabras para ganar velocidad
                                   "temperature": 0.4, # Respuestas directas y sin rodeos
                                   "keep_alive": "-1"  # Mantiene el modelo despierto en la RAM
                               } 
                           }, timeout=20)
        return res.json().get('message', {}).get('content', 'Estoy a su servicio.')
    except:
        return "Mi conexión ha tenido una breve interrupción, pero mi voluntad de servicio permanece."