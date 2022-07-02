######################################################################################
#   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    addTitular         #
######################################################################################
import datetime
import sqlite3

from datetime import datetime, timedelta
from PyQt5 import uic, QtWebEngineWidgets

from PyQt5.QtWidgets import *

from src.util.fundUtils import *


'''
    @parent: UserView
    @returns: None
'''

class addTitularView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)

        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/AddTitularView.ui", view)

        view.buttonNuevo.clicked.connect(view.nuevoTitular)


    def nuevoTitular(self):
        if self.tfTitular.text():
            self.parent().cbTitular.addItem(self.tfTitular.text())
