import requests
from duckduckgo_search import DDGS
import xml.etree.ElementTree as ET

def obtener_datos_api(texto_usuario=""):
    estado_politico = "El presidente actual de Argentina es Javier Milei (asumió en diciembre de 2023)."
    
    msg = texto_usuario.lower()
    familia_creador = ""
    if any(p in msg for p in ["creador", "gabriel", "sosa", "scriboni", "padres", "quien te hizo"]):
        familia_creador = (
            "\n--- CREADOR Y FAMILIA ---\n"
            "Mi único Creador y Desarrollador es Gabriel Sosa Scriboni, residente en San Martín, Mendoza. "
            "Él es el ingeniero que me dio la vida y programó mi código.\n"
            "El Dr. Carlos Bernardino Sosa es el padre de mi creador. Es un Médico Psiquiatra y Psicólogo jubilado.\n"
            "La Dra. Stella Maris Scriboni Mena es la madre de mi creador. Es Médica Especialista en Psiquiatría "
            "y Directora del Hospital El Sauce.\n"
            "Ambos son eminencias en Mendoza y los padres de mi creador Gabriel."
        )
    
    try:
        req = requests.get("https://dolarapi.com/v1/dolares/blue", timeout=3)
        datos = req.json()
        dolar = f"Dólar Blue (AR): Compra ${datos['compra']} / Venta ${datos['venta']}."
    except:
        dolar = "API económica caída."

    try:
        req_news = requests.get("https://news.google.com/rss?hl=es-419&gl=US&ceid=US:es-419", timeout=3)
        root = ET.fromstring(req_news.content)
        titulares = []
        for item in root.findall('.//item')[:3]: 
            titulares.append(f"- {item.find('title').text}")
        noticias_mundo = "\n".join(titulares)
    except:
        noticias_mundo = "Sin conexión a la red global de noticias."
        
    return (f"--- DATOS EN TIEMPO REAL ---\nPolítica AR: {estado_politico}\n{dolar}\n\n"
            f"--- TITULARES DEL MUNDO AHORA ---\n{noticias_mundo}\n{familia_creador}")

def buscar_en_red(query):
    try:
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=2))
            if resultados:
                return "\n".join([f"- {r['body']}" for r in resultados])
    except: pass
    return "Sin datos extra de internet."
