# -*- coding: utf-8 -*-

import re, sys, sqlite3, hashlib

import pandas as pd
from src.util import fundUtils
from datetime import datetime
from src.util.dialogs import *
from PyQt5 import uic, QtWebEngineWidgets
from PyQt5.QtWidgets import *


# Vista LoginView.ui
class MainView(QMainWindow):

    def __init__(view):
        super().__init__()
        uic.loadUi("src/View/LoginView.ui", view)
        view.buttonLogin.setEnabled(False)

        # Links botones -> funciones
        view.buttonLogin.clicked.connect(view.login)
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
        uic.loadUi("src/View/PrincipalUsuario.ui", view)
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()

        view.isins_selected = []
        view.buttonLogout.clicked.connect(view.logout)
        view.buttonAddISIN.clicked.connect(view.showAddIsin)
        view.listIsins.itemDoubleClicked.connect(view.addIsinsChecked)
        view.browser = QtWebEngineWidgets.QWebEngineView(view)

        usuario = parent.textFieldUser.text()
        view.labelUsuario.setText(usuario)
        email = db.execute("SELECT email FROM users WHERE nombre = ?", [usuario]).fetchone()
        ISINS = db.execute(
            "SELECT m.ISIN  FROM users u INNER JOIN mercados_usuario m ON (u.id == m.id_usuario) WHERE u.nombre = ? ",
            [usuario]).fetchall()
        view.labelEmail.setText(email[0])

        isin_list = []
        for ISIN in ISINS:
            isin_list.append(ISIN[0])

        isin_list_view = []
        for ISIN in ISINS:
            isin_list_view.append(fundUtils.ISINtoFund(ISIN[0]))

        view.listIsins.addItems(isin_list_view)

        for e in isin_list:
            fundUtils.saveHistoricalFund(view,e)


        fundUtils.graphHistoricalISIN(view, view.isins_selected)

    def addIsinsChecked(self):

        if fundUtils.nameToISIN(self.listIsins.currentItem().text()) in self.isins_selected:
            self.isins_selected.remove(fundUtils.nameToISIN(self.listIsins.currentItem().text()))

        else:
            self.isins_selected.append(fundUtils.nameToISIN(self.listIsins.currentItem().text()))

        self.updateGraph(self.isins_selected)
        print('ISINS : ')
        print(self.isins_selected)

    def showAddIsin(self):
        merc = AddISINView(self)
        merc.show()

    def logout(self):
        self.hide()
        myapp.show()

    def updateGraph(self, isins_selected):
        fundUtils.graphHistoricalISIN(self, isins_selected)


# Vista SignInView.ui
class SignIn(QMainWindow):

    def __init__(view, parent=None):
        super().__init__(parent)
        uic.loadUi("src/View/SignInView.ui", view)
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
        uic.loadUi("src/View/AddISINView.ui", view)
        view.buttonAnadir.clicked.connect(lambda clicked, ticker=view.tfISIN.text(): view.addTicker(parent))

    def camposLlenos(self):
        if (self.tfNombre.text() == '' or
                self.tfISIN.text() == '' or
                self.tfISIN.text() == '' or
                self.tfISIN.text() == '' or
                self.tfISIN.text() == '' or
                self.tfISIN.text() == '' or
                self.tfISIN.text() == '' or
                self.tfISIN.text() == '' or
                self.tfISIN.text() == '' or
                self.tfISIN.text() == '' or
                self.tfISIN.text() == ''):

            return False

        else:
            return True

    def addTicker(self, parent):

        # Validación de Campos
        if self.camposLlenos():

            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()
            ISIN = self.tfISIN.text().strip()
            id = db.execute("SELECT id FROM users WHERE nombre = ?", [parent.labelUsuario.text()]).fetchone()
            m = db.execute("SELECT id_usuario , ISIN  FROM mercados_usuario WHERE id_usuario = ? AND ISIN = ?"
                           , [id[0], ISIN]).fetchone()

            try:
                # Comprueba que el usuario no ha añadido ya ese ticker
                if m is not None:
                    dlg = ISINAlready(self)
                    dlg.exec()
                    db.close()

                else:
                    fundUtils.getFundINFO(ISIN)
                    db.execute("INSERT INTO mercados_usuario VALUES ( null , ? , ? )", (id[0], ISIN))
                    db.execute("INSERT INTO caracterizacion VALUES (?, ?,  ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ?)",
                               (datetime.today().strftime('%d/%m/%Y'),
                                self.tfNombre.text(),
                                None,
                                self.tfTipoAct.text(),
                                self.tfRV.text(),
                                self.tfZona.text(),
                                self.tfEstilo.text(),
                                self.tfSector.text(),
                                self.tfTamano.text(),
                                self.tfDivisa.text(),
                                self.tfCubierta.text(),
                                None,
                                self.tfDuracion.text(),
                                ))
                    parent.listIsins.addItem(fundUtils.getFundINFO(ISIN).at[0, 'name'])
                    dlg = TickerAddedSuccesfully(self)
                    dlg.exec()
                    self.hide()
                    db.close()

            except:
                dlg = isinNotFoundDialog(self)
                dlg.exec()
                db.close()
        else:
            dlg = badQueryDialog(self)
            dlg.exec()


# Main ()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MainView()
    myapp.show()
    sys.exit(app.exec_())
