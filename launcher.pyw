# -*- coding: utf-8 -*-
import re, sys, sqlite3, hashlib
import pandas as pd

from fundUtils import *
from dialogs import *
from PyQt5 import QtCore, uic, QtWidgets, QtWebEngineWidgets
from PyQt5.QtWidgets import *
from highstock import Highstock


# Vista LoginView.ui
class MainView(QMainWindow):

    def __init__(view):
        super().__init__()
        uic.loadUi("View/LoginView.ui", view)
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
        uic.loadUi("View/PrincipalUsuario.ui", view)
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()
        view.isins_selected = []
        view.buttonLogout.clicked.connect(view.logout)
        view.buttonAddISIN.clicked.connect(view.showAddMercados)
        view.listIsins.itemDoubleClicked.connect(view.addIsinsChecked)

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
        view.listIsins.addItems(isin_list)

        name = getFundINFO(ISIN[0][0]).at[0, 'name']
        country = getFundINFO(ISIN[0][0]).at[0, 'country']
        currency = getFundINFO(ISIN[0][0]).at[0, 'currency']
        data = investpy.funds.get_fund_historical_data(
            fund=name,
            country=country,
            from_date='01/04/2000',
            to_date='13/05/2022',
            as_json=False
        )
        values = []
        for i in range(0, len(data.index), 1):
            tuple = (data.index[i], data['Open'][i])
            values.append(tuple)
        H = Highstock()
        H.add_data_set(values, "line", name)
        options = {
            # 'colors': ['#a0a0a0'],

            'chart': {
                'zoomType': 'x',
                'backgroundColor': '#a0a0a0',
                'animation': {
                    'duration': 2000
                },
            },
            'title': {
                'text': name
            },

            "rangeSelector": {"selected": 6},

            "yAxis": {
                'opposite': True,
                'title': {
                    'text': currency,
                    'align': 'middle'
                },
                'labels': {
                    'align': 'left'
                },

                "plotLines": [{"value": 0, "width": 2, "color": "silver"}],
            },

            # "plotOptions": {"series": {"compare": "percent"}},

            "tooltip": {
                "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ',
                "valueDecimals": 2,
            },
        }
        H.set_dict_options(options)
        view.browser = QtWebEngineWidgets.QWebEngineView(view)
        view.browser.setHtml(H.htmlcontent)
        view.layout.addWidget(view.browser)

        # Figure Method
        '''
        VÍA FIGURE
        fig = go.Figure()

        fig.add_trace(go.Candlestick(x=data.index,
                                     open=data['Open'],
                                     high=data['High'],
                                     low=data['Low'],
                                     close=data['Close'],
                                     name='Valor de mercado'))

        fig.update_layout(
            title=name,
            yaxis_title=currency

        )

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=15, label='15 M', step='minute', stepmode='backward'),
                    dict(count=45, label='45 M', step='minute', stepmode='backward'),
                    dict(count=1, label='1 H', step='hour', stepmode='todate'),
                    dict(count=2, label='2 H', step='hour', stepmode='backward'),
                    dict(step='all')

                ])
            )
        )

        view.browser = QtWebEngineWidgets.QWebEngineView(view)
        view.layout.addWidget(view.browser)
        view.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        '''

        # Grafico HTML Method
        ''' Vía llamada HTML 
        view.browser = QtWebEngineWidgets.QWebEngineView(view)
        url = 'https://funds.ddns.net/h.php?isin=' + ISINS[0][0]
        q_url = QUrl(url)

        view.browser.load(q_url)
        view.layout.addWidget(view.browser)
        '''


    def addIsinsChecked(self):

        if self.listIsins.item(self.listIsins.currentRow()).text() in self.isins_selected:
            self.isins_selected.remove(self.listIsins.item(self.listIsins.currentRow()).text())

        else :
            self.isins_selected.append(self.listIsins.item(self.listIsins.currentRow()).text())

        # updateGraph
        print('ISINS : ')
        print(self.isins_selected)



    def showAddMercados(self):
        merc = AddISINView(self)
        merc.show()

    def logout(self):
        self.hide()
        myapp.show()

    def updateGraph(self, isin):
        print("Selector de Isin pulsado: " + isin)

        name = getFundINFO(isin).at[0, 'name']
        country = getFundINFO(isin).at[0, 'country']
        currency = getFundINFO(isin).at[0, 'currency']

        data = investpy.funds.get_fund_historical_data(
            fund=name,
            country=country,
            from_date='01/04/2000',
            to_date='13/05/2022',
            as_json=False
        )

        values = []
        for i in range(0, len(data.index), 1):
            tuple = (data.index[i], data['Open'][i])
            values.append(tuple)

        H = Highstock()

        H.add_data_set(values, "line", name)

        options = {

            'title': {
                'text': name
            },

            "rangeSelector": {"selected": 6},

            "yAxis": {
                "labels": {
                    "formatter": "function () {\
                                   return (this.value);\
                               }"
                },
                "plotLines": [{"value": 0, "width": 2, "color": "silver"}],
            },

            # "plotOptions": {"series": {"compare": "percent"}},
            "tooltip": {
                "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ({point.change}%)<br/>',
                "valueDecimals": 2,
            },
        }

        H.set_dict_options(options)

        self.browser.setHtml(H.htmlcontent)
        self.layout.addWidget(self.browser)


# Vista SignInView.ui
class SignIn(QMainWindow):

    def __init__(view, parent=None):
        super().__init__(parent)
        uic.loadUi("View/SignInView.ui", view)
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
        uic.loadUi("View/AddISINView.ui", view)
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
    sys.exit(app.exec_())
