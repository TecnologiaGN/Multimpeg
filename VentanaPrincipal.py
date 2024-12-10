import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from Video_cutter import create_video_cutter_window  # Importar la función del cortador de video
from Subir_audio import create_audio_uploader_window  # Importar la función de subir audio
from Peso import create_reduce_video_size_window  # Importar la clase para bajar peso de video
from Concatenar import create_video_concatenator_window
from Cambiar_Formato import create_format_changer_window
import tkinter as tk  # Importar tkinter para ejecutar ventanas independientes

# Función resource_path para manejar rutas de recursos con PyInstaller
def resource_path(relative_path):
    """Obtiene la ruta absoluta de los recursos, maneja rutas para PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Prueba

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MULTIMPEG")

        # Establecer un tamaño inicial para la ventana
        self.setFixedSize(600, 500)

        # Crear un layout vertical principal para incluir el texto, botones y la imagen
        layout_principal = QVBoxLayout()

        # Crear un QLabel para el texto superior
        label_titulo = QLabel("Seleccione el proceso que desea realizar", self)
        label_titulo.setAlignment(Qt.AlignCenter)  # Centrar el texto
        
        # Aumentar el tamaño de la letra
        label_titulo.setStyleSheet("font-size: 18px; font-weight: bold;")  # Cambia el tamaño según lo necesites

        layout_principal.addWidget(label_titulo)  # Añadir el texto al layout

        # Crear un layout horizontal para dividir la ventana en dos partes (botones e imagen)
        layout_botones_imagen = QHBoxLayout()

        # Layout para los botones
        layout_botones = QVBoxLayout()

        # Crear los botones
        btn_video = QPushButton("Cortador de Video")
        btn_audio = QPushButton("Subir Audio")
        btn_peso = QPushButton("Bajar peso")
        btn_concat = QPushButton("Concatenar Videos")
        btn_formato = QPushButton("Cambiar Formato")

        # Ajustar el tamaño de los botones
        for btn in [btn_video, btn_audio, btn_peso, btn_concat, btn_formato]:
            btn.setMinimumSize(120, 40)
            btn.setMaximumSize(150, 50)
            btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        # Conectar los botones a sus respectivas funciones
        btn_video.clicked.connect(self.abrir_cortador_video)
        btn_audio.clicked.connect(self.abrir_subir_audio)
        btn_peso.clicked.connect(self.abrir_bajar_peso)
        btn_concat.clicked.connect(self.abrir_concatenar_videos)
        btn_formato.clicked.connect(self.abrir_cambiar_formato)

        # Añadir los botones al layout vertical
        layout_botones.addWidget(btn_video)
        layout_botones.addWidget(btn_audio)
        layout_botones.addWidget(btn_peso)
        layout_botones.addWidget(btn_concat)
        layout_botones.addWidget(btn_formato)

        # Crear un QLabel para la imagen
        label_imagen = QLabel(self)
        # Usar resource_path para acceder a la imagen correctamente en PyInstaller
        pixmap = QPixmap(resource_path(r".\images\icoo.png"))  # Cargar la imagen
        label_imagen.setPixmap(pixmap)
        label_imagen.setScaledContents(True)  # Ajustar la imagen al tamaño del QLabel
        label_imagen.setMinimumSize(200, 200)  # Tamaño mínimo de la imagen

        # Crear un efecto de sombra
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(50)  # Radio de desenfoque
        sombra.setOffset(10, 10)  # Desplazamiento de la sombra (x, y)
        sombra.setColor(Qt.black)  # Color de la sombra (negra)
        
        # Aplicar la sombra a la imagen
        label_imagen.setGraphicsEffect(sombra)

        # Añadir los layouts (botones e imagen) al layout horizontal
        layout_botones_imagen.addLayout(layout_botones)  # Botones a la izquierda
        layout_botones_imagen.addWidget(label_imagen)  # Imagen a la derecha

        # Añadir el layout de botones e imagen al layout principal
        layout_principal.addLayout(layout_botones_imagen)

        # Establecer el layout central
        central_widget = QWidget()
        central_widget.setLayout(layout_principal)
        self.setCentralWidget(central_widget)

    def abrir_cortador_video(self):
        create_video_cutter_window()  # Abre la ventana del cortador de video

    def abrir_subir_audio(self):
        create_audio_uploader_window()  # Abre la ventana de subir audio
        
    def abrir_bajar_peso(self):
        create_reduce_video_size_window()
  
    def abrir_concatenar_videos(self):
        create_video_concatenator_window()  # Abre la ventana de concatenar videos

    def abrir_cambiar_formato(self):
        create_format_changer_window()  # Abre la ventana de cambiar formato


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())
