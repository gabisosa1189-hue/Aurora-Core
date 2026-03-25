import json
import os

MEMORIA_DIR = "memorias"

# Creamos la carpeta si no existe
if not os.path.exists(MEMORIA_DIR):
    os.makedirs(MEMORIA_DIR)

def obtener_historial(user_id):
    archivo = os.path.join(MEMORIA_DIR, f"{user_id}.json")
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_historial(user_id, historial):
    archivo = os.path.join(MEMORIA_DIR, f"{user_id}.json")
    # Solo guardamos los últimos 10 mensajes para que sea ultra rápida
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(historial[-10:], f, ensure_ascii=False, indent=2)

def borrar_memoria_usuario(user_id):
    archivo = os.path.join(MEMORIA_DIR, f"{user_id}.json")
    if os.path.exists(archivo):
        os.remove(archivo)
        return True
    return False