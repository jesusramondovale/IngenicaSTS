# -*- coding: utf-8 -*-
import json, re, sys, requests, sqlite3, hashlib
import pandas as pd
from PyQt5 import QtCore, uic, QtWidgets, QtWebEngineWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import *


class TickerAddedSuccesfully(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Éxito!")
        self.setFixedWidth(330)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "El fondo con ISIN: " + parent.tfTicker.text() + " se ha añadido\ncorrectamente a su cartera personal."))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


class registerCompleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Éxito!")
        self.setFixedWidth(300)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("El Registro se ha realizado\nadecuadamente"))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


class badEmailDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Error!")
        self.setFixedWidth(300)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.clicked.connect(self.accept)

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("La dirección de correo introducida"))
        self.layout.addWidget(QLabel("no es válida !"))
        self.layout.addWidget(btnOK, 3, 0, 1, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


class badQueryDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya...")
        self.setFixedWidth(300)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.clicked.connect(self.accept)
        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel("Rellena los campos primero!"))
        self.layout.addWidget(btnOK, stretch=10)
        self.setLayout(self.layout)


class badLoginDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Error!")
        self.setFixedWidth(300)
        self.setFixedHeight(100)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.clicked.connect(self.accept)

        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("Usuario o contraseña incorrectos !"), 0, 0, 0, 0, QtCore.Qt.AlignTop)
        self.layout.addWidget(btnOK, 6, 0, 1, 0, QtCore.Qt.AlignRight)

        self.setLayout(self.layout)


class goodLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Bienvenido!")
        self.setFixedWidth(280)

        # CONTENIDO
        btnEntrar = QPushButton('Entrar')
        btnSalir = QPushButton('Salir')

        btnEntrar.clicked.connect(self.accept)
        btnSalir.clicked.connect(self.reject)

        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel("Bienvenido, señor Admin!"))
        self.layout.addWidget(btnEntrar)
        self.layout.addWidget(btnSalir)

        self.setLayout(self.layout)


# Vista LoginView.ui
class MainView(QMainWindow):

    def __init__(view):
        super().__init__()
        uic.loadUi("LoginView.ui", view)
        view.buttonLogin.setEnabled(False)

        # Links botones -> funciones
        view.buttonLogin.clicked.connect(view.login)
        view.buttonSignin.clicked.connect(view.showSignInView)
        view.textFieldUser.textChanged.connect(view.dispatcher)
        view.textFieldPassword.textChanged.connect(view.dispatcher)
        view.textFieldPassword.returnPressed.connect(view.login)

    # Función para el botón "SIGN IN" (registrar nuevo usuario)
    def showSignInView(self):
        self.hide()
        signin = SignIn(self)
        signin.show()

    # Función para el botón "ENTRAR" del diálogo goodLogin
    def showUserView(self, QMainWindow):
        self.hide()
        userView = UserView(QMainWindow)
        userView.show()

    # Función para el botón "LOGIN"
    def login(self):

        user = self.textFieldUser.text()
        password = self.textFieldPassword.text()

        SHA_password = hashlib.sha256(self.textFieldPassword.text().encode(encoding='UTF-8')).hexdigest()

        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()
        loginResult = db.execute("SELECT id FROM users WHERE nombre = ? AND password = ? ",
                                 (user, SHA_password)).fetchall()

        SHA_passwords = db.execute("SELECT password FROM users").fetchall()
        dfPasswords = pd.DataFrame(SHA_passwords)

        if loginResult.__len__() != 0:
            dlg = goodLoginDialog(self)
            if dlg.exec():
                self.showUserView(self)
                # print("Pulsado botón Entrar")

            else:
                print("Pulsado el botón salir")


        else:
            dlg = badLoginDialog(self)
            dlg.exec()

        print('User: ' + user)
        print('Pass: ' + password)
        print('Pass (SHA256): ' + SHA_password)

        db_connection.close()

    # Captador de eventos de teclado sobre tfUser y tfPass que pone enabled=True el botón "LOGIN"
    def dispatcher(self):
        if self.textFieldPassword.text() and self.textFieldUser.text():
            self.buttonLogin.setEnabled(True)


# Vista UserView.ui
class UserView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)
        uic.loadUi("UserView.ui", view)

        usuario = parent.textFieldUser.text()
        view.tfNombre.setText(usuario)
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()
        email = db.execute("SELECT email FROM users WHERE nombre = ?", [usuario]).fetchone()
        ISINS = db.execute(
            "SELECT m.ISIN  FROM users u INNER JOIN mercados_usuario m ON (u.id == m.id_usuario) WHERE u.nombre = ? ",
            [usuario]).fetchall()
        view.tfEmail.setText(email[0])
        view.actionLog_Out.triggered.connect(view.logout)
        view.actionA_adir_Mercados.triggered.connect(view.showAddMercados)

        for ISIN in ISINS:
            action = QtWidgets.QAction(view)
            view.menuSeleccionar_Mercado.addAction(action)
            action.setText(QtCore.QCoreApplication.translate("UserView", ISIN[0]))
            action.triggered.connect(lambda clicked, ticker=action.text(): view.updateGraph(ticker))

        view.browser = QtWebEngineWidgets.QWebEngineView(view)
        url = 'https://funds.ddns.net/h.php?isin=' + ISINS[0][0]
        q_url = QUrl(url)

        view.browser.load(q_url)
        view.layout.addWidget(view.browser)

    def showAddMercados(self):
        merc = AddISINView(self)
        merc.show()

    def logout(self):
        self.hide()
        myapp.show()

    def updateGraph(self, isin):
        print("Selector de Isin pulsado: " + isin)

        url = 'https://funds.ddns.net/h.php?isin=' + isin
        q_url = QUrl(url)

        self.browser.load(q_url)
        self.layout.addWidget(self.browser)


# Vista SignInView.ui
class SignIn(QMainWindow):

    def __init__(view, parent=None):
        super().__init__(parent)
        uic.loadUi("SignInView.ui", view)
        view.buttonRegistrar.clicked.connect(view.registrar)
        view.buttonSalir.clicked.connect(view.salir)

    def salir(self):
        self.hide()
        myapp.show()

    # Retorna True si la cadena email es una dirección de correo válida
    def checkMail(self, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if (re.fullmatch(regex, email)):
            return True
        else:
            return False

    # Función para el botón "REGISTRAR"
    def registrar(view):

        nombre = view.tfNombre.text()
        email = view.tfEmail.text()
        pass_SHA = ''

        if view.tfPass.text() != '':
            pass_SHA = hashlib.sha256(view.tfPass.text().encode(encoding='UTF-8')).hexdigest()

        if nombre == '' or email == '' or pass_SHA == '':
            dlg = badQueryDialog(view)
            dlg.exec()

        else:
            if not view.checkMail(email):
                dlg = badEmailDialog(view)
                dlg.exec()

            else:
                db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
                db = db_connection.cursor()
                db.execute("INSERT INTO users VALUES ( null , ? , ? , ?)", (nombre, email, pass_SHA))
                db.close()
                dlg = registerCompleteDialog(view)
                dlg.exec()


# Vista AddTickersView.ui
class AddISINView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)
        uic.loadUi("AddISINView.ui", view)
        view.buttonAnadir.clicked.connect(lambda clicked, ticker=view.tfTicker.text(): view.addTicker(parent))

    def addTicker(self, parent):
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()
        ISIN = self.tfTicker.text()
        id = db.execute("SELECT id FROM users WHERE nombre = ?", [parent.tfNombre.text()]).fetchone()
        db.execute("INSERT INTO mercados_usuario VALUES ( null , ? , ? )", (id[0], ISIN))

        action = QtWidgets.QAction(self)
        parent.menuSeleccionar_Mercado.addAction(action)
        action.setText(QtCore.QCoreApplication.translate("UserView", self.tfTicker.text()))
        action.triggered.connect(lambda clicked, ticker=action.text(): parent.updateGraph(ticker))
        dlg = TickerAddedSuccesfully(self)
        dlg.exec()
        self.hide()
        db.close()


# Main ()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MainView()
    myapp.show()
    # cargaDatos()
    sys.exit(app.exec_())
