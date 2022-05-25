# -*- coding: utf-8 -*-

import hashlib
import re
import sqlite3
import sys
from datetime import datetime

import pandas as pd
from PyQt5 import uic, QtWebEngineWidgets
from PyQt5.QtWidgets import *

from src.util import fundUtils
from src.util.dialogs import *


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


# Vista PrincipalUsuario.ui
class UserView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)
        uic.loadUi("src/View/PrincipalUsuario.ui", view)
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()
        usuario = parent.textFieldUser.text()

        view.id_usuario = db.execute("SELECT id FROM users WHERE nombre = ?", [usuario]).fetchone()
        view.currentCartera = db.execute(
            "SELECT nombre_cartera FROM carteras WHERE id_usuario = ? ORDER BY (nombre_cartera)",
            ([view.id_usuario[0]])).fetchone()

        view.isins_selected = []
        view.buttonLogout.clicked.connect(view.logout)
        view.buttonAddISIN.clicked.connect(view.showAddIsin)
        view.buttonAddCarteras.clicked.connect(view.showAddCarteras)

        view.listIsins.itemClicked.connect(view.addIsinsChecked)
        view.browser = QtWebEngineWidgets.QWebEngineView(view)
        view.cbModo.addItems(['Absoluto', 'Evolución'])

        view.labelUsuario.setText(usuario)
        email = db.execute("SELECT email FROM users WHERE nombre = ?", [usuario]).fetchone()

        view.carteras_usuario = db.execute(
            "SELECT num_cartera , nombre_cartera FROM carteras WHERE id_usuario = ? ORDER BY (nombre_cartera)",
            ([view.id_usuario[0]])).fetchall()
        view.nombres_carteras = []
        for e in view.carteras_usuario:
            view.nombres_carteras.append(e[1])

        view.cbCarteras.addItems(view.nombres_carteras)

        ISINS = db.execute(
            "SELECT cu.ISIN FROM carteras c INNER JOIN carteras_usuario cu "
            "USING (num_cartera)"
            "WHERE c.nombre_cartera = ? AND cu.id_usuario = ? ",
            ([view.currentCartera[0], view.id_usuario[0]])).fetchall()
        view.labelEmail.setText(email[0])

        isin_list = []
        for ISIN in ISINS:
            isin_list.append(ISIN[0])

        isin_list_view = []
        for ISIN in ISINS:
            isin_list_view.append(fundUtils.ISINtoFund(ISIN[0]))

        for x in isin_list_view:
            item = QListWidgetItem(str(x))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | ~QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            view.listIsins.addItem(item)

        for e in isin_list:
            fundUtils.saveHistoricalFund(view, e)

        fundUtils.graphHistoricalISIN(view, view.isins_selected, False)

        view.cbCarteras.currentIndexChanged.connect(view.updateQList)
        view.cbModo.currentIndexChanged.connect(lambda clicked, isins_selected=view.isins_selected: view.updateGraph(view.isins_selected))


    def updateQList(view):

        view.listIsins.clear()
        view.isins_selected = []
        view.labelCartera.setText('Fondos en ' + view.cbCarteras.currentText())
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()
        ISINS = db.execute(
            "SELECT cu.ISIN FROM carteras c INNER JOIN carteras_usuario cu "
            "USING (num_cartera)"
            "WHERE c.nombre_cartera = ? AND cu.id_usuario = ?   ",
            ([str(view.cbCarteras.currentText()), view.id_usuario[0]])).fetchall()

        isin_list = []
        for ISIN in ISINS:
            isin_list.append(ISIN[0])

        isin_list_view = []
        for ISIN in ISINS:
            isin_list_view.append(fundUtils.ISINtoFund(ISIN[0]))

        for x in isin_list_view:
            item = QListWidgetItem(str(x))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            view.listIsins.addItem(item)

        for e in isin_list:
            fundUtils.saveHistoricalFund(view, e)

        fundUtils.graphHistoricalISIN(view, view.isins_selected, True)

    def addIsinsChecked(self):
        print("Captada la pulsación")
        try:
            if fundUtils.nameToISIN(self.listIsins.item(self.listIsins.currentRow()).text()) in self.isins_selected:
                # if fundUtils.nameToISIN(self.listIsins.item(self.listIsins.currentItem()).text()) in self.isins_selected:

                self.isins_selected.remove(fundUtils.nameToISIN(self.listIsins.currentItem().text()))
                self.listIsins.currentItem().setCheckState(False)
            else:
                self.isins_selected.append(fundUtils.nameToISIN(self.listIsins.currentItem().text()))
                self.listIsins.currentItem().setCheckState(True)

            self.updateGraph(self.isins_selected)

        except AttributeError:
            dlg = errorInesperado(self)
            dlg.exec()

        print('ISINS : ')
        print(self.isins_selected)

    def showAddCarteras(self):
        cart = AddCarterasView(self)
        cart.show()

    def showAddIsin(self):
        merc = AddISINView(self)
        merc.show()

    def logout(self):
        self.hide()
        myapp.show()

    def updateGraph(self, isins_selected):
        if self.cbModo.currentIndex() == 0:
            fundUtils.graphHistoricalISIN(self, isins_selected, True)
        else:
            fundUtils.graphHistoricalISIN(self, isins_selected, False)


# Vista AddCarterasView.ui
class AddCarterasView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)
        uic.loadUi("src/View/AddCarterasView.ui", view)

        view.id_usuario = parent.id_usuario
        view.buttonCrear.setEnabled(False)
        view.buttonCrear.clicked.connect(view.crear)
        view.tfNombre.textChanged.connect(view.activarBoton)

    def crear(self):
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()

        nombre_cartera = self.tfNombre.text()
        temp = db.execute("SELECT num_cartera FROM carteras WHERE id_usuario = ? AND nombre_cartera = ? ",
                          [self.id_usuario[0], nombre_cartera]).fetchone()
        if temp is None:
            db.execute(
                "INSERT INTO carteras VALUES (?,?,?,?) ",
                [self.id_usuario[0], None, nombre_cartera,
                 datetime.today().strftime('%d/%m/%Y')]).fetchone()

            self.carteras_usuario = db.execute(
                "SELECT num_cartera , nombre_cartera FROM carteras WHERE id_usuario = ? ORDER BY (nombre_cartera)",
                ([self.id_usuario[0]])).fetchall()

            self.nombres_carteras = []

            for e in self.carteras_usuario:
                self.nombres_carteras.append(e[1])

            dlg = CarteraAddedSuccesfully(self)
            dlg.exec()
            self.parent().cbCarteras.addItems(self.nombres_carteras)

        else:
            dlg = carteraAlreadyExistsDialog(self)
            dlg.exec()

    def activarBoton(self):
        if self.tfNombre.text():
            self.buttonCrear.setEnabled(True)
        else:
            self.buttonCrear.setEnabled(False)


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
            m = db.execute(
                "SELECT id_usuario , ISIN  FROM carteras_usuario WHERE id_usuario = ? AND ISIN = ? AND nombre_cartera = ? "
                , [id[0], ISIN]).fetchone()

            try:
                # Comprueba que el usuario no ha añadido ya ese ticker
                if m is not None:
                    dlg = ISINAlready(self)
                    dlg.exec()
                    db.close()

                else:
                    fundUtils.getFundINFO(ISIN)
                    db.execute("INSERT INTO carteras_usuario VALUES ( null , ? , ? )", (id[0], ISIN))
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
