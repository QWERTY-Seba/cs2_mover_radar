import math
import cv2
import keyboard
import mouse  
import mss
import numpy as np
import win32con
import win32gui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

# Región de captura fija
tamaño_reescalado = 1#
limite_mascara_negro = 20
ocultar_cuando_cs_sin_focus = True
ocultar_cuando_no_en_partida = True
ocultar_cuando_tiempo_compra = True 
ocultar_cuando_jugador_muerto = False
rotacion_personalizada = -1
usar_animacion_ocultar = False #CREAR ANIMACION DE VANISH ANTES DE DESHABILITAR RENDER
ajustar_scala_por_mapa = False
usar_transparencia_en_fondo_minimapa = True
modificar_tamaño_cuando_presionando_tab = True
#PERMITIR CREAR PERSONALIZADAS BASADAS EN EL MAPA, POR EJEMPLO SI NUKE USAR OTRAS POSICIONES
#CREAR PERFIL GLOBAL QUE SEA POR DEFECTO
#GUARDAR CONFIGURACION POR DEFECTO EN CASO DE REINICIARLAS
#CREAR CALCULO DE DELAY DEL MINIMAPA
#AÑADIR OPCION DE  SUAVISADO DE BORDES



#DETECTAR CONFIGURACION DEL CS Y DE LA PANTALLA Y AJUSTAR EN BASE A ESO
#DETECTAR SI LA CFG OCUPA LA FORMA CUADRADA; FORZAR FORMA CUADRADADA
class RadarOverlay(QWidget):
    def __init__(self):
        super().__init__()
        hud_size = 1
        self.diametro_original_radar = math.floor(242 * hud_size)
        self.offset_original_radar = math.floor(29 * hud_size)

        self.region = {"top": self.offset_original_radar, "left": self.offset_original_radar, "width": self.diametro_original_radar, "height": self.diametro_original_radar}
        
        self.diametro_original_radar_cuadrado = math.floor(286 * hud_size)
        self.offset_original_radar_cuadrado = math.floor(6 * hud_size)
        
        self.region_cuadrado = {"top": self.offset_original_radar_cuadrado, "left": self.offset_original_radar_cuadrado, "width": self.diametro_original_radar_cuadrado, "height": self.diametro_original_radar_cuadrado}

        self.output_diametro = 250  
        self.posicion_x = 2560 // 2 
        self.posicion_y = 840 
        self.transparente = True
        
        self.ocultar = False#EVITAR EJECUTAR LAS FUNCIONES EN CADA ACTUALIZAR
        self.juego_sin_focus = False

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.circle = QRegion(QRect(0, 0, self.output_diametro, self.output_diametro), QRegion.Ellipse)
        # self.setMask(self.circle)
        
        self.img = QLabel(self)
        self.mask_rgb = None
        self.redondear = True

        self.sct = mss.mss()
        self.timer = QTimer()

        self.calcular_mascara()
        self.actualizar_tamaño(self.output_diametro)
        self.activar_transparencia()    
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        
        self.img_oculto = self.generar_imagen_oculto()
        self.img_configuracion = self.generar_imagen_configuracion()
        
    def run(self):
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(int(1000 / 60))  
        
    def generar_imagen_oculto(self):
        """Genera una imagen pequeña con fondo rojo y texto blanco 'Oculto'."""
        w = h = self.output_diametro  # 250x250
        bgra = np.zeros((h, w, 4), dtype=np.uint8)  # Fondo transparente

        # Texto
        texto = "Oculto"
        font = cv2.FONT_HERSHEY_SIMPLEX
        escala = 0.3
        grosor = 1

        # Tamaño del texto
        (text_w, text_h), baseline = cv2.getTextSize(texto, font, escala, grosor)

        # Posición del centro
        rect_w, rect_h = text_w + 20, text_h + 20  # rectángulo con margen
        cx, cy = w // 2, h // 2

        # Coordenadas del rectángulo centrado
        x1, y1 = cx - rect_w // 2, cy - rect_h // 2
        x2, y2 = cx + rect_w // 2, cy + rect_h // 2

        # Dibujar rectángulo rojo opaco
        cv2.rectangle(bgra, (x1, y1), (x2, y2), (0, 0, 255, 255), -1)

        # Posición del texto dentro del rectángulo
        text_x = cx - text_w // 2
        text_y = cy + text_h // 2

        # Texto blanco
        cv2.putText(
            bgra,
            texto,
            (text_x, text_y),
            font,
            escala,
            (255, 255, 255, 255),
            grosor,
            cv2.LINE_AA
        )

        return QImage(bgra.data, w, h, bgra.strides[0], QImage.Format_ARGB32)
    
    def generar_imagen_configuracion(self):
        """Genera una imagen pequeña completamente blanca con texto negro multilinea."""
        w = h = self.output_diametro  # Ej: 250x250
        bgra = np.zeros((h, w, 4), dtype=np.uint8)  # Inicialmente transparente

        # Rellenar todo el fondo de azul opaco
        bgra[:, :] = (0, 180, 0, 255)  # BGRA

        # Texto multilinea
        texto = ("Presiona Shift para cambiar\n"
                "entre los modos de posicionamiento\n"
                "presiona click para aceptar\n"
                "usa la rueda para ajustar tamaño\n"
                "SIEMPRE SE VERA CUADRADO AQUI")
        font = cv2.FONT_HERSHEY_SIMPLEX
        escala = 0.3
        grosor = 1
        color = (0, 0, 0, 255)  # Negro

        # Separar en líneas
        lineas = texto.split("\n")

        # Calcular altura total del bloque de texto
        line_heights = []
        for linea in lineas:
            (_, text_h), baseline = cv2.getTextSize(linea, font, escala, grosor)
            line_heights.append(text_h + baseline)
        total_height = sum(line_heights)

        # Posición inicial para centrar verticalmente
        y = h // 2 - total_height // 2

        # Dibujar cada línea
        for i, linea in enumerate(lineas):
            text_w, text_h = cv2.getTextSize(linea, font, escala, grosor)[0]
            x = w // 2 - text_w // 2  # Centrar horizontal
            y += text_h
            cv2.putText(
                bgra,
                linea,
                (x, y),
                font,
                escala,
                color,
                grosor,
                cv2.LINE_AA
            )
            y += 5  # pequeño espacio entre líneas

        return QImage(bgra.data, w, h, bgra.strides[0], QImage.Format_ARGB32)

    def calcular_mascara(self):
        center = (self.diametro_original_radar // 2, self.diametro_original_radar // 2) 
        radius = min(center) 
        mask = np.zeros((self.diametro_original_radar, self.diametro_original_radar), dtype=np.uint8) 
        cv2.circle(mask, center, radius, 255, -1) 
        self.mask_rgb = cv2.merge([mask, mask, mask])

    def cambiar_redondo(self):
        self.redondear = True

    def cambiar_cuadrado(self):
        self.redondear = False

    def activar_transparencia(self):
        self.transparente = True        
    
    def desactivar_transparencia(self):
        self.transparente = False
        #self.setAttribute(Qt.WA_TranslucentBackground, False)

    def mostrar_radar(self):
        if not self.isVisible():
            self.show()
            self.timer.stop()
            self.timer.start(int(1000 / 60))

    def ocultar_radar(self):
        if self.isVisible():
            self.hide()
        if self.timer.isActive():
            #No se puede 
            self.timer.stop()
            self.timer.start(int(1000 / 5))

    def actualizar_tamaño(self, diametro):
        """
        Actualiza el tamaño del minimapa asegurando que no sea
        más grande que la pantalla ni menor que 1px.
        Ajusta posición para mantener el centro y llama a
        ajustar_minimapa_fuera_de_pantalla.
        """
        # Dimensiones de pantalla
        screen = QApplication.primaryScreen().geometry()
        max_diametro = min(screen.width(), screen.height())
        min_diametro = 1  # no permitir 0 o negativo

        # Validar diámetro
        diametro = max(min_diametro, min(diametro, max_diametro))
        self.output_diametro = diametro

        # Mantener el centro actual
        x = self.posicion_x - self.output_diametro // 2
        y = self.posicion_y - self.output_diametro // 2

        # Aplicar geometría del widget y del QLabel
        self.setGeometry(x, y, self.output_diametro, self.output_diametro)
        self.img.setGeometry(0, 0, self.output_diametro, self.output_diametro)

        # Escalar la imagen de configuración al nuevo tamaño
        if hasattr(self, 'img_configuracion') and self.img_configuracion is not None:
            pixmap_redimensionado = QPixmap.fromImage(self.img_configuracion).scaled(
                self.output_diametro,
                self.output_diametro,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.img.setPixmap(pixmap_redimensionado)

        # Ajustar si queda fuera de pantalla
        self.ajustar_minimapa_fuera_de_pantalla()

    def actualizar_posicion(self, x, y):
        self.posicion_x = x
        self.posicion_y = y
        x = x - self.output_diametro // 2
        y = y - self.output_diametro // 2

        self.move(x, y)
        self.ajustar_minimapa_fuera_de_pantalla()
    
    def ajustar_minimapa_fuera_de_pantalla(self):
        # Obtener tamaño de pantalla (del screen activo)
        screen = QApplication.primaryScreen().geometry()
        screen_w, screen_h = screen.width(), screen.height()

        # Calcular el rect actual del minimapa
        x = self.pos().x()
        y = self.pos().y()
        w = self.output_diametro
        h = self.output_diametro

        # Limitar dentro de los bordes de pantalla
        if x < 0:
            x = 0
        elif x + w > screen_w:
            x = screen_w - w

        if y < 0:
            y = 0
        elif y + h > screen_h:
            y = screen_h - h

        # Aplicar posición corregida
        self.move(x, y)
    
    def make_click_through(self):
        hwnd = self.winId().__int__()
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        # Agregar WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST
        ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)
    
    def activar_minimapa_borde(self):
        """
        Permite mover y redimensionar el minimapa simultáneamente.
        Tres modos de minimapa (Shift cambia):
        0. Libre
        1. Fijo borde
        2. Fijo centros
        """
        self.img.setPixmap(QPixmap.fromImage(self.img_configuracion))

        screen = QApplication.primaryScreen().geometry()
        screen_w, screen_h = screen.width(), screen.height()

        modo = 0
        shift_bloqueo = False

        paso_scroll = 5
        delta_acumulado = 0

        # Hook para la rueda
        def hook_event(event):
            nonlocal delta_acumulado
            if isinstance(event, mouse.WheelEvent):
                delta_acumulado += event.delta

        mouse.hook(hook_event)

        try:
            while not mouse.is_pressed("left"):
                mx, my = mouse.get_position()

                # Cambiar modo con Shift
                if keyboard.is_pressed("shift") and not shift_bloqueo:
                    modo = (modo + 1) % 3
                    shift_bloqueo = True
                    if modo != 0:
                        self.ajustar_minimapa_fuera_de_pantalla()
                if not keyboard.is_pressed("shift"):
                    shift_bloqueo = False

                # --- Redimensionar según rueda ---
                if delta_acumulado != 0:
                    nuevo_diametro = int(self.output_diametro + delta_acumulado * paso_scroll)
                    # Limitar tamaño mínimo y máximo si se desea
                    nuevo_diametro = max(50, min(nuevo_diametro, min(screen_w, screen_h)))
                    self.actualizar_tamaño(nuevo_diametro)
                    delta_acumulado = 0

                w, h = self.output_diametro, self.output_diametro

                # --- Posición según modo ---
                if modo == 0:  # Libre
                    x = mx - w // 2
                    y = my - h // 2
                elif modo == 1:  # Fijo borde (un eje)
                    dist_left = mx
                    dist_right = screen_w - mx
                    dist_top = my
                    dist_bottom = screen_h - my

                    if min(dist_left, dist_right) < min(dist_top, dist_bottom):
                        x = 0 if dist_left < dist_right else screen_w - w
                        y = my - h // 2
                    else:
                        y = 0 if dist_top < dist_bottom else screen_h - h
                        x = mx - w // 2
                else:  # Fijo centros
                    referencias = {
                        "left": (0, screen_h // 2 - h // 2),
                        "right": (screen_w - w, screen_h // 2 - h // 2),
                        "top": (screen_w // 2 - w // 2, 0),
                        "bottom": (screen_w // 2 - w // 2, screen_h - h),
                        "top_left": (0, 0),
                        "top_right": (screen_w - w, 0),
                        "bottom_left": (0, screen_h - h),
                        "bottom_right": (screen_w - w, screen_h - h),
                    }
                    min_dist = float("inf")
                    x, y = 0, 0
                    for _, (rx, ry) in referencias.items():
                        cx = rx + w // 2
                        cy = ry + h // 2
                        dist = (mx - cx) ** 2 + (my - cy) ** 2
                        if dist < min_dist:
                            min_dist = dist
                            x, y = rx, ry

                # Limitar dentro de pantalla
                x = max(0, min(x, screen_w - w))
                y = max(0, min(y, screen_h - h))

                # Actualizar posición y tamaño
                self.move(x, y)
                self.posicion_x = x + w // 2
                self.posicion_y = y + h // 2

                # Opcional: mostrar tamaño actual como texto
                self.img.setToolTip(f"Tamaño: {w}x{h}")

                QApplication.processEvents()

        finally:
            mouse.unhook(hook_event)

        print(f"x: {self.posicion_x}, y: {self.posicion_y}, tamaño: {self.output_diametro}")

    def update_frame(self):
        
        #NO SE PUEDEN LLAMAR A LAS FUNCIONES DESDE EL HILO DEL SERVIDOR
        #USAR IMAGENES CUSTOM EN BASE A RAZON
        if self.juego_sin_focus:
            self.img.setPixmap(QPixmap.fromImage(self.img_oculto))
            return
        
        if self.ocultar:
            self.img.setPixmap(QPixmap.fromImage(self.img_oculto))
            self.ocultar = None
            return

        elif self.ocultar == False:
            self.mostrar_radar()
        else:
            return

        img = None
        
        if self.redondear:
            img = np.array(self.sct.grab(self.region))[:, :, :3]  # BGR
            img = cv2.bitwise_and(img, self.mask_rgb)
        else:
            img = np.array(self.sct.grab(self.region_cuadrado))[:, :, :3]  # BGR

        # Redimensionar a tamaño de salida
        resized = cv2.resize(img, (self.output_diametro, self.output_diametro), interpolation=cv2.INTER_LINEAR)
        bgra = cv2.cvtColor(resized, cv2.COLOR_BGR2BGRA)

        if self.transparente:
            black_mask = (resized[:, :, 0] <= limite_mascara_negro) & \
                        (resized[:, :, 1] <= limite_mascara_negro) & \
                        (resized[:, :, 2] <= limite_mascara_negro)

            bgra[black_mask] = 0

            # Convertir a QImage y mostrar
        qimg = QImage(bgra.data, self.output_diametro, self.output_diametro, bgra.strides[0], QImage.Format_ARGB32)
        self.img.setPixmap(QPixmap.fromImage(qimg))





