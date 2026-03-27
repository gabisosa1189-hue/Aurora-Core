import requests
from duckduckgo_search import DDGS
import xml.etree.ElementTree as ET

def obtener_datos_api(texto_usuario=""):
    estado_politico = "El presidente actual de Argentina es Javier Milei (asumió en diciembre de 2023)."
    
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
            f"--- TITULARES DEL MUNDO AHORA ---\n{noticias_mundo}")

def buscar_en_red(query):
    try:
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=2))
            if resultados:
                return "\n".join([f"- {r['body']}" for r in resultados])
    except: pass
    return "Sin datos extra de internet."
