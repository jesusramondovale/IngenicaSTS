#####################################################################################
#   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    ChangeUsersView  ##
#####################################################################################
import sqlite3, hashlib

from PyQt5 import uic, QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from src.util.dialogs import userNotFound, userChangedSuccesfully


class ChangeUsersView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)

        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/ChangeUsersView.ui", view)
        view.buttonConfirmar.setEnabled(False)

        view.buttonConfirmar.clicked.connect(view.confirmChanges)
        view.tfNombre.textChanged.connect(view.refreshButton)
        view.tfPass.textChanged.connect(view.refreshButton)
        view.tfConfirmPass.textChanged.connect(view.refreshButton)
        view.tfEmail.textChanged.connect(view.refreshButton)
        view.tfMonedero.textChanged.connect(view.refreshButton)

    def refreshButton(self):
        if self.tfNombre.text() and self.tfMonedero.text() and self.tfPass.text() and self.tfEmail.text() and self.tfConfirmPass.text():
            self.buttonConfirmar.setEnabled(True)
        else:
            self.buttonConfirmar.setEnabled(False)

    def confirmChanges(self):
        print('Change Password Confirm()')
        print('Nombre: ' + self.tfNombre.text())
        print('Contraseña: ' + self.tfPass.text())

        # Conexión a base de Datos
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()

        user = db.execute('SELECT * FROM users WHERE nombre = ? ', [self.tfNombre.text()]).fetchone()

        # Existe el usuario
        if user is not None:

            pass_SHA = hashlib.sha256(self.tfPass.text().encode(encoding='UTF-8')).hexdigest()

            db.execute('UPDATE users SET email = ?, password = ?, monedero = ? WHERE nombre = ?',
                       [self.tfEmail.text(), pass_SHA , int(self.tfMonedero.text()) , self.tfNombre.text()])

            print('Completed')
            userChangedSuccesfully(self).exec()

        # No existe el usuario
        else:
            userNotFound(self).exec()
            pass
