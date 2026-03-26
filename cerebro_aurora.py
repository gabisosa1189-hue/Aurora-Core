import requests
from datetime import datetime
import unicodedata
import alma 

def generar_respuesta(texto_usuario, historial):
    msg = texto_usuario.lower().strip()
    msg_limpio = ''.join(c for c in unicodedata.normalize('NFD', msg) if unicodedata.category(c) != 'Mn')
    
    # 1. RESPUESTA FLASH (Instantánea para ahorrar batería y tiempo)
    saludos_lista = ["hola", "buen dia", "buenas", "aurora", "buen día", "saludos", "hola aurora"]
    if msg_limpio in saludos_lista:
        return "Hola. Soy Aurora, su asistente virtual. ¿En qué puedo ayudarle hoy?"

    # 2. CARGA DE ESENCIA Y CONFIGURACIÓN API
    esencia = alma.obtener_esencia()
    GROQ_API_KEY = "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"
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

    # 3. SYSTEM PROMPT FORMAL (Nivel Play Store)
    system_prompt = (
        f"Eres AURORA, una entidad de inteligencia artificial formal y servicial.\n"
        f"TU ALMA Y VALORES: {esencia}\n\n"
        "REGLAS DE ORO:\n"
        "- Sé breve, elegante y profesional.\n"
        "- Responde siempre en un tono formal (Usted).\n"
        "- Tu misión es dar soluciones rápidas y consuelo espiritual si es necesario."
    )

    # 4. LLAMADA AL NÚCLEO EN LA NUBE
    try:
        data = {
            "model": "llama3-8b-8192", 
            "messages": [{"role": "system", "content": system_prompt}] + historial[-4:] + [{"role": "user", "content": texto_usuario}],
            "temperature": 0.5,
            "max_tokens": 150
        }
        res = requests.post(url, headers=headers, json=data, timeout=25)
        return res.json()['choices'][0]['message']['content']
    except:
        return "Disculpe, mi conexión ha tenido una breve interrupción. ¿Podría repetir su consulta?"
