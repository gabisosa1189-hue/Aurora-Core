Set objShell = CreateObject("WScript.Shell")

' 1. Cerramos CUALQUIER proceso de python previo
objShell.Run "taskkill /F /IM python.exe", 0, True
WScript.Sleep 1000

' 2. Iniciamos el server que acabas de subir
' (Asegurate que el archivo se llame exactamente aurora_server.py)
objShell.Run "python C:\AURORA-CORP-APP\aurora_server.py", 0, False

' 3. Esperamos a que Ollama despierte
WScript.Sleep 5000

' 4. Lanzamos la App
objShell.Run "msedge --app=http://localhost:5000", 1, False