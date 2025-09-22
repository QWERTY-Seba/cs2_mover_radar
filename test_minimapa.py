import os
import sys
import threading
import time
import keyboard
import win32gui
from PyQt5.QtWidgets import QApplication
from minimapa import RadarOverlay
from server import iniciar_servidor


#VALIDAR FONDO NEGRO
variables = {
    "cl_radar_square_always": None,
    "cl_radar_square_with_scoreboard" : None,
    "setting.defaultres"	:	None,
    "setting.defaultresheight"	:	None,
    "setting.fullscreen"	:	None,
    "setting.nowindowborder"	:	None,
    "setting.aspectratiomode"	:	None
}

#Leer archivo y buscar valores
def extraer_valores(full_path):
    if os.path.isfile(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            for line in f:
                # Limpiar la línea y saltar vacías o comentarios
                line = line.strip()
                if not line or line.startswith("//"):
                    continue

                # Cada línea esperada: "nombre_variable" "valor"
                if line.startswith('"'):
                    parts = line.split('"')
                    if len(parts) >= 4:
                        nombre = parts[1]
                        valor = parts[3]
                        if nombre in variables:
                            variables[nombre] = valor

base_path = r"C:\Program Files (x86)\Steam\userdata\0\730\local\cfg"  # <-- cambia por tu path
archivos = ["cs2_machine_convars.vcfg", "cs2_video.txt"]
for archivo in archivos:
    extraer_valores(os.path.join(base_path, archivo))

app = QApplication([])
radar = RadarOverlay()
radar.show()
radar.make_click_through()






def process_event(event):
    if event.event_type == 'down' and event.name == 'tab':
        radar.cambiar_cuadrado()
    
    if event.event_type == 'up' and event.name == 'tab':
        radar.cambiar_redondo()

# DAR ALERTA SI NO ESTA EN WINDOW O BORDERLESS
# USAR WIN32 SI SE USA WINDOW
# "setting.defaultres"		"2560"
# "setting.defaultresheight"		"1080"
# "setting.fullscreen"		"0"
# "setting.nowindowborder"		"1"
# SI SE USA MSS REVISAR EN QUE MONITOR ESTA EL JUEGO
# REVISAR EL BIND DE MOSTRAR EL LEADERBOARD


if variables["cl_radar_square_always"] == True:
    radar.cambiar_cuadrado()


if True or variables["cl_radar_square_with_scoreboard"] == True and not variables["cl_radar_square_always"] == True:
    keyboard.hook(lambda e: threading.Thread(target=process_event, args=(e,)).start())


def manejar_estado(estado):
    if estado not in ("live", "over"):
        radar.ocultar = True
    else:
        radar.ocultar = False

def juego_tiene_focus():
    while True:
        hwnd = win32gui.GetForegroundWindow()
        titulo = win32gui.GetWindowText(hwnd)
        if "Counter-Strike 2" == titulo:
            radar.juego_sin_focus = False
        else:
            radar.juego_sin_focus = True
            
        time.sleep(0.5)  

thread = threading.Thread(target=iniciar_servidor, kwargs={"callback_estado": manejar_estado}, daemon=True)
thread.start()

thread2 = threading.Thread(target=juego_tiene_focus, daemon=True)
thread2.start()

radar.activar_minimapa_borde()
radar.run()

radar.actualizar_tamaño(diametro=350)
radar.actualizar_posicion(x=1280,y=900)

sys.exit(app.exec_())
