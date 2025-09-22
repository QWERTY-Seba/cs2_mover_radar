import http.server
import json
import os
import socketserver
import winreg
from http.server import BaseHTTPRequestHandler
from typing import Any




#AGREGAR PARA VALIDAR QUE EL PERSONAJE ESTA MUERTO PARA CAMBIAR A CUADRADO O CIRCULO
def parsear_respuesta(json_data):

    try:
        if json_data.get("provider"):
            if len(json_data) == 1 or (len(json_data) == 2 and json_data.get("previously")) :
                return ("NO_EN_JUEGO", None)

        round_data = json_data.get("round", {}).get("phase")
        prev_data = json_data.get("previously", {}).get("round", {}).get("phase")
        
        if round_data is None:
            return ("NO_EN_PARTIDA")
        
        return (round_data, prev_data)

    except Exception as e:
        print("Error al parsear:", e)

    
    return (None,None)

def crear_archivo_gsi():

    ruta_steam = None
    try:
        #MOVER A CONSTANTE
        clave = r"SOFTWARE\Wow6432Node\Valve\cs2"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, clave) as key:
            valor, _ = winreg.QueryValueEx(key, "InstallPath")
            ruta_steam = valor
    except Exception as e:
        print("Error al leer el registro:", e)
        

    ruta_cfg = os.path.join(ruta_steam, r"game\csgo\cfg")
    archivo = os.path.join(ruta_cfg, "gamestate_integration_Minimapa.cfg")

    if os.path.exists(archivo):
        return (False, "El archivo ya existe")

    contenido = '''"Minimapa"
        {
        "uri" "http://localhost:54321/"
        "timeout" "5.0"
        "buffer"  "0.5"
        "throttle" "0"
        "heartbeat" "10.0"
        "data"
            {
        "provider" "1"
        "round" "1"
        }
        }'''

    try:
        os.makedirs(ruta_cfg, exist_ok=True)
        
        if not os.path.exists(archivo):
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(contenido)
            
            return (True, "Archivo Creado")
    except Exception as e:
        return (None, f"Error al crear el archivo: {e}" )

class Handler(http.server.BaseHTTPRequestHandler):

    callback_estado = None

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        actual, anterior = parsear_respuesta(data)
        
        Handler.callback_estado(actual) 
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format: str, *args: Any) -> None:
        pass

def iniciar_servidor(callback_estado):
    status, msg = crear_archivo_gsi()

    if status is None:
        raise Exception("Error al intentar crear archivo gsi")

    print(msg)
    puerto = 54321
    Handler.callback_estado = callback_estado
    with socketserver.TCPServer(("", puerto), Handler) as httpd:
        print(f"Servidor escuchando en http://localhost:{puerto}")
        httpd.serve_forever()



