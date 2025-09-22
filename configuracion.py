import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QCheckBox, QLabel, QPushButton
from PyQt5.QtCore import Qt
from minimapa import RadarOverlay
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import QPoint
import mouse
class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración de Variables")
        self.init_variables()
        self.init_ui()
        self.radar = RadarOverlay()
        self.radar.show()
        self.radar.make_click_through()

    def init_variables(self):
        self.limite_mascara_negro = 20
        self.ocultar_cuando_cs_sin_focus = True
        self.ocultar_cuando_no_en_partida = True
        self.ocultar_cuando_tiempo_compra = True
        self.ocultar_cuando_jugador_muerto = False
        self.rotacion_personalizada = -1
        self.usar_animacion_ocultar = False
        self.ajustar_scala_por_mapa = False
        self.usar_transparencia_en_fondo_minimapa = True
        self.modificar_tamaño_cuando_presionando_tab = True

    def init_ui(self):
        layout = QVBoxLayout()


        self.move_minimap_button = QPushButton("Mover Minimapa")

        # Conectamos el evento de clic del botón a una función
        self.move_minimap_button.clicked.connect(self.on_move_minimap_clicked)

        # Agregamos el botón al layout
        layout.addWidget(self.move_minimap_button)


        # Variable: limite_mascara_negro (QSlider)
        self.limite_mascara_negro_label = QLabel(f"Límite Máscara Negro: {self.limite_mascara_negro}")
        layout.addWidget(self.limite_mascara_negro_label)
        self.limite_mascara_negro_slider = QSlider(Qt.Horizontal)
        self.limite_mascara_negro_slider.setRange(0, 255)
        self.limite_mascara_negro_slider.setValue(self.limite_mascara_negro)
        self.limite_mascara_negro_slider.valueChanged.connect(self.update_limite_mascara_negro)
        layout.addWidget(self.limite_mascara_negro_slider)

        # Variable: rotacion_personalizada (QSlider)
        self.rotacion_personalizada_label = QLabel(f"Rotación Personalizada: {self.rotacion_personalizada}")
        layout.addWidget(self.rotacion_personalizada_label)
        self.rotacion_personalizada_slider = QSlider(Qt.Horizontal)
        self.rotacion_personalizada_slider.setRange(-1, 360)
        self.rotacion_personalizada_slider.setValue(self.rotacion_personalizada)
        self.rotacion_personalizada_slider.valueChanged.connect(self.update_rotacion_personalizada)
        layout.addWidget(self.rotacion_personalizada_slider)

        # Variables booleanas (QCheckBox)
        self.ocultar_cuando_cs_sin_focus_check = self.create_checkbox("Ocultar cuando CS sin focus", self.ocultar_cuando_cs_sin_focus, self.update_bool_var)
        layout.addWidget(self.ocultar_cuando_cs_sin_focus_check)
        self.ocultar_cuando_no_en_partida_check = self.create_checkbox("Ocultar cuando no en partida", self.ocultar_cuando_no_en_partida, self.update_bool_var)
        layout.addWidget(self.ocultar_cuando_no_en_partida_check)
        self.ocultar_cuando_tiempo_compra_check = self.create_checkbox("Ocultar cuando tiempo de compra", self.ocultar_cuando_tiempo_compra, self.update_bool_var)
        layout.addWidget(self.ocultar_cuando_tiempo_compra_check)
        self.ocultar_cuando_jugador_muerto_check = self.create_checkbox("Ocultar cuando jugador muerto", self.ocultar_cuando_jugador_muerto, self.update_bool_var)
        layout.addWidget(self.ocultar_cuando_jugador_muerto_check)
        self.usar_animacion_ocultar_check = self.create_checkbox("Usar animación de ocultar", self.usar_animacion_ocultar, self.update_bool_var)
        layout.addWidget(self.usar_animacion_ocultar_check)
        self.ajustar_scala_por_mapa_check = self.create_checkbox("Ajustar escala por mapa", self.ajustar_scala_por_mapa, self.update_bool_var)
        layout.addWidget(self.ajustar_scala_por_mapa_check)
        self.usar_transparencia_en_fondo_minimapa_check = self.create_checkbox("Usar transparencia en fondo de minimapa", self.usar_transparencia_en_fondo_minimapa, self.update_bool_var)
        layout.addWidget(self.usar_transparencia_en_fondo_minimapa_check)
        self.modificar_tamaño_cuando_presionando_tab_check = self.create_checkbox("Modificar tamaño cuando se presiona TAB", self.modificar_tamaño_cuando_presionando_tab, self.update_bool_var)
        layout.addWidget(self.modificar_tamaño_cuando_presionando_tab_check)

        self.setLayout(layout)

    def on_move_minimap_clicked(self):
        while not mouse.is_pressed('left'):
                    # Obtener la posición global del cursor
            pos = QCursor.pos()
            self.radar.actualizar_posicion(pos.x(), pos.y())
            
            # Procesar eventos para que la aplicación no se bloquee por completo
            # y la ventana del minimapa se pueda redibujar
            QApplication.processEvents()

            # Comprobar si se ha hecho clic con el botón izquierdo



    def create_checkbox(self, text, checked, slot):
        checkbox = QCheckBox(text)
        checkbox.setChecked(checked)
        checkbox.stateChanged.connect(slot)
        return checkbox

    def update_limite_mascara_negro(self, value):
        self.limite_mascara_negro = value
        self.limite_mascara_negro_label.setText(f"Límite Máscara Negro: {self.limite_mascara_negro}")
        print(f"Valor actualizado: limite_mascara_negro = {self.limite_mascara_negro}")

    def update_rotacion_personalizada(self, value):
        self.rotacion_personalizada = value
        self.rotacion_personalizada_label.setText(f"Rotación Personalizada: {self.rotacion_personalizada}")
        print(f"Valor actualizado: rotacion_personalizada = {self.rotacion_personalizada}")

    def update_bool_var(self, state):
        sender = self.sender()
        if sender == self.ocultar_cuando_cs_sin_focus_check:
            self.ocultar_cuando_cs_sin_focus = state == Qt.Checked
            print(f"Valor actualizado: ocultar_cuando_cs_sin_focus = {self.ocultar_cuando_cs_sin_focus}")
        elif sender == self.ocultar_cuando_no_en_partida_check:
            self.ocultar_cuando_no_en_partida = state == Qt.Checked
            print(f"Valor actualizado: ocultar_cuando_no_en_partida = {self.ocultar_cuando_no_en_partida}")
        elif sender == self.ocultar_cuando_tiempo_compra_check:
            self.ocultar_cuando_tiempo_compra = state == Qt.Checked
            print(f"Valor actualizado: ocultar_cuando_tiempo_compra = {self.ocultar_cuando_tiempo_compra}")
        elif sender == self.ocultar_cuando_jugador_muerto_check:
            self.ocultar_cuando_jugador_muerto = state == Qt.Checked
            print(f"Valor actualizado: ocultar_cuando_jugador_muerto = {self.ocultar_cuando_jugador_muerto}")
        elif sender == self.usar_animacion_ocultar_check:
            self.usar_animacion_ocultar = state == Qt.Checked
            print(f"Valor actualizado: usar_animacion_ocultar = {self.usar_animacion_ocultar}")
        elif sender == self.ajustar_scala_por_mapa_check:
            self.ajustar_scala_por_mapa = state == Qt.Checked
            print(f"Valor actualizado: ajustar_scala_por_mapa = {self.ajustar_scala_por_mapa}")
        elif sender == self.usar_transparencia_en_fondo_minimapa_check:
            self.usar_transparencia_en_fondo_minimapa = state == Qt.Checked
            print(f"Valor actualizado: usar_transparencia_en_fondo_minimapa = {self.usar_transparencia_en_fondo_minimapa}")
        elif sender == self.modificar_tamaño_cuando_presionando_tab_check:
            self.modificar_tamaño_cuando_presionando_tab = state == Qt.Checked
            print(f"Valor actualizado: modificar_tamaño_cuando_presionando_tab = {self.modificar_tamaño_cuando_presionando_tab}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())

#     ruta_steam = obtener_ruta_steam()
#     if ruta_steam:
#         crear_archivo_gsi(ruta_steam)

#         # Ejecutar servidor en un hilo para que no bloquee
#         servidor_hilo = threading.Thread(target=iniciar_servidor, daemon=True)
#         servidor_hilo.start()




#         if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     radar = RadarOverlay()
#     radar.show()
#     radar.make_click_through()
#     sys.exit(app.exec_())



# # Nombre parcial de la ventana que debe tener el foco para NO mostrar mensaje
# TITULO_BLOQUEADO = "Counter-Strike 2"  # o "csgo" si es más preciso

# def juego_tiene_focus(VENTANA_OBJETIVO):
#     hwnd = win32gui.GetForegroundWindow()
#     titulo = win32gui.GetWindowText(hwnd)
#     return titulo.strip() == VENTANA_OBJETIVO