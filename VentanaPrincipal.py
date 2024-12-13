import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy
from PyQt5.QtGui import QPixmap 
from PyQt5.QtCore import Qt, QPoint
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

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MULTIMPEG")

        # Establecer un tamaño inicial para la ventana
        self.setFixedSize(700, 550)

        # Cargar el archivo de estilo (VentanaPrincipal.qss)
        self.modo_claro = False  # Indica si estamos en modo claro o no
        self.cargar_estilo()

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

        # Botón para cambiar entre modo claro y oscuro (será reemplazado por una imagen)
        self.label_tema = QLabel(self)
        self.label_tema.setAlignment(Qt.AlignCenter)
        
        # Cambios para aumentar el tamaño de la imagen de cambio de tema
        imagen_tema = self.obtener_imagen_tema()
        # Escalar la imagen a un tamaño más grande (por ejemplo, 80x80)
        imagen_tema_escalada = imagen_tema.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_tema.setPixmap(imagen_tema_escalada)
        
        # Cambiar el tamaño fijo del label
        self.label_tema.setFixedSize(80, 80)  # Aumentar de 40x40 a 80x80
        
        self.label_tema.mousePressEvent = self.cambiar_tema  # Cambiar de tema al hacer clic

        # Ajustar el tamaño de los botones
        for btn in [btn_video, btn_audio, btn_peso, btn_concat, btn_formato]:
            btn.setMinimumSize(160, 40)
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
        layout_botones.addWidget(self.label_tema)  # Añadir el label de cambiar tema

        # Crear un QLabel para la imagen
        label_imagen = QLabel(self)
        pixmap = QPixmap(resource_path(r".\images\icoo.png"))  # Cargar la imagen
        label_imagen.setPixmap(pixmap)
        label_imagen.setScaledContents(True)  # Ajustar la imagen al tamaño del QLabel
        label_imagen.setMinimumSize(200, 200)  # Tamaño mínimo de la imagen

        # Añadir los layouts (botones e imagen) al layout horizontal
        layout_botones_imagen.addLayout(layout_botones)  # Botones a la izquierda
        layout_botones_imagen.addWidget(label_imagen)  # Imagen a la derecha

        # Añadir el layout de botones e imagen al layout principal
        layout_principal.addLayout(layout_botones_imagen)

        # Establecer el layout central
        central_widget = QWidget()
        central_widget.setLayout(layout_principal)
        self.setCentralWidget(central_widget)

    def cargar_estilo(self):
        """Carga el archivo QSS dependiendo del tema"""
        estilo_path = resource_path('Style_claro.qss' if self.modo_claro else 'Style.qss')
        try:
            with open(estilo_path, 'r') as archivo_qss:
                qss = archivo_qss.read()
                self.setStyleSheet(qss)  # Aplicar el estilo a la aplicación
        except FileNotFoundError:
            print(f"El archivo de estilo {estilo_path} no fue encontrado.")

    def cambiar_tema(self, event=None):
        """Alterna entre modo claro y oscuro"""
        self.modo_claro = not self.modo_claro
        self.cargar_estilo()
        
        # Escalar la nueva imagen de tema
        imagen_tema = self.obtener_imagen_tema()
        imagen_tema_escalada = imagen_tema.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.label_tema.setPixmap(imagen_tema_escalada)

    def obtener_imagen_tema(self):
        """Devuelve la imagen correspondiente según el tema"""
        if self.modo_claro:
            return QPixmap(resource_path(r".\images\tema_oscuro.png"))
        else:
            return QPixmap(resource_path(r".\images\tema_claro.png"))

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