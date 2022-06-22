###############################################################################
#   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    DE CARGA   ##
###############################################################################
import sqlite3

# Importamos las librerías de carga y Widgets de Python QT v5
# para graficar el contenido de los ficheros GUI
from PyQt5 import uic, QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5.Qt import *

class cargandoView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)
        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/cargandoView.ui", view)
        view.setWindowFlag(Qt.FramelessWindowHint)
        view.show()
