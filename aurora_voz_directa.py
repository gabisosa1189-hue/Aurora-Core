import speech_recognition as sr
import requests
import asyncio
import edge_tts
import pygame
import os
import time

# --- CONFIGURACIÓN ---
VOZ = "es-MX-DaliaNeural"
ARCHIVO_AUDIO = "respuesta_aurora.mp3"
MODELO = "llama3.1"

def hablar(texto):
    print(f"\n[AURORA]: {texto}")
    async def generar():
        communicate = edge_tts.Communicate(texto, VOZ)
        await communicate.save(ARCHIVO_AUDIO)
    asyncio.run(generar())
    
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(ARCHIVO_AUDIO)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"❌ Error al reproducir: {e}")
    finally:
        pygame.mixer.quit()

def escuchar_y_responder():
    reconocedor = sr.Recognizer()
    with sr.Microphone() as fuente:
        print("\n🎤 ESCUCHANDO... (Hablale a Aurora)")
        reconocedor.adjust_for_ambient_noise(fuente, duration=1)
        try:
            audio = reconocedor.listen(fuente, timeout=5)
            print("🧠 Entendiendo...")
            texto_usuario = reconocedor.recognize_google(audio, language='es-AR')
            print(f"👉 VOS DIJISTE: {texto_usuario}")
            
            res = requests.post("http://localhost:11434/api/chat", 
                               json={"model": MODELO, "messages": [{"role": "user", "content": texto_usuario}], "stream": False})
            
            respuesta_ai = res.json().get('message', {}).get('content', 'No pude procesar.')
            hablar(respuesta_ai)
            
        except Exception as e:
            print(f"... (Esperando voz)")

if __name__ == "__main__":
    print("\n" + "="*40)
    print("   AURORA - MODO VOZ DIRECTA")
    print("="*40)
    hablar("Hola Gabriel. Estoy conectada. ¿Qué vamos a crear hoy?")
    while True:
        escuchar_y_responder()