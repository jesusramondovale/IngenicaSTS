###########################################################################################
##   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    MainView (LoginView)  ##
###########################################################################################
import hashlib
import sqlite3

# Librerías Pandas DataFrame
import pandas as pd

# Importamos las librerías de carga y Widgets de Python QT v5
# para graficar el contenido de los ficheros GUI
from PyQt5 import uic
from PyQt5.QtWidgets import *

# Importamos la lógica necesaria de otras vistas
from src.View.SignInView import SignIn
from src.View.UserView import UserView
from src.util.dialogs import *

'''
    - Ventana de Acceso a la aplicación (LogIn) 

     @parent: None (instancia creada en launcher.pyw al ejecutar la aplicación)
     @children: UserView | badLoginDialog 
'''
# Vista LoginView.ui
class MainView(QMainWindow):


    def __init__(view):
        super().__init__()

        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/LoginView.ui", view)
        view.buttonLogin.setEnabled(False)

        # COnexión de eventos del botón LogIn y de los TextFields de la vista a la lógica de controlador
        view.buttonLogin.clicked.connect(view.login)
        view.textFieldUser.textChanged.connect(view.dispatcher)
        view.textFieldPassword.textChanged.connect(view.dispatcher)
        view.textFieldPassword.returnPressed.connect(view.login)

    '''
        - Controlador del evento clicked sobre el botón SignIn

        @params: view (MainView) 
        @returns: None
    '''
    def showSignInView(self):
        self.hide()
        signin = SignIn(self)
        signin.show()

    '''
        - Controlador del evento clicked sobre el botón Entrar en el diálogo goodLogin

        @params: view (MainView) 
        @returns: None
    '''
    def showUserView(self, QMainWindow):
        self.hide()
        userView = UserView(QMainWindow)
        userView.show()

    '''
        - Controlador del evento clicked sobre el botón LogIn

        @params: view (MainView) 
        @returns: None
    '''
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

    '''
        - Controlador de eventos de teclado sobre los TextField User y Pass de la vista
        - Activa el botón de Login siempre y cuando haya texto en los campos Usuario y Contraseña
        @params: view (MainView) 
        @returns: None
    '''
    # Captador de eventos de teclado sobre tfUser y tfPass que pone enabled=True el botón "LOGIN"
    def dispatcher(self):
        if self.textFieldPassword.text() and self.textFieldUser.text():
            self.buttonLogin.setEnabled(True)
