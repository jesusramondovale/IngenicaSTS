########################################################
##   DIÁLOGOS ÚTILES PARA LA MUESTRA DE INFORMACIÓN   ##
##          AL USUARIO DE LA APLICACIÓN               ##
#########################################################
from PyQt5.QtWidgets import QDialog, QPushButton, QGridLayout, QLabel, QHBoxLayout
from PyQt5 import QtCore

'''
    - Avisa al Usuario de que el fondo ya se encuentra 
    añadido a su cartera actual de usuario. 
    
    @parent: AddISINView 
'''


class ISINAlready(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya..")
        self.setFixedWidth(330)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "El fondo " + parent.tfISIN.text() + " ya se encuentra" + '\n' + "añadido a su cartera"))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


'''
    - Avisa al Usuario de que el fondo introducido
    no ha sido encontrado en investing.com
    
    @parent: AddISINView
'''
class isinNotFoundDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya..")
        self.setFixedWidth(330)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "El fondo " + parent.tfISIN.text() + " no se encuentra" + '\n' + "en investing.com"))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


'''
    - Avisa al Usuario de que el nombre de cartera 
    escogido en la creación de una nueva ya existe. 
    
    @parent: AddCarterasView
'''
class carteraAlreadyExistsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya..")
        self.setFixedWidth(330)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "Ya existe la cartera '" + parent.tfNombre.text() + '\n' + "' en su cuenta de usuario!"))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


''' 
    - Avisa al Usuario de que se ha 
    producido un error inesperado
    
    @parent: Any
'''
class errorInesperado(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya!")
        self.setFixedWidth(330)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "Se ha producido un error inesperado. INténtelo de nuevo."))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


''' 
    - Avisa al Usuario de que la nueva cartera ha sido
    creada y añadida a su cuenta satisfactoriamente
    
    @parent: AddCarterasView
'''
class CarteraAddedSuccesfully(QDialog):
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
            "La Cartera con nombre : " + parent.tfNombre.text() + " se\nha añadido correctamente a su cuenta personal."))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


''' 
    - Avisa al Usuario de que el nuevo fondo ha sido
    encontrado en investin.com y añadido a su cuenta 
    satisfactoriamente

    @parent: AddISINView
'''
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
            "El fondo con ISIN: " + parent.tfISIN.text() + " se ha \nañadido correctamente a su cartera personal."))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


''' 
    - Avisa al ADMIN de que el registro de un nuevo usuario 
    ha sido realizado satisfactoriamente
    
    @parent: RegisterUsuarioView
'''
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


''' 
    - Avisa al ADMIN de que el registro de un nuevo usuario 
    no ha podido ser realizado satisfactoriamente debido    
    a que el e-mail proporcionado es erróneo

    @parent: RegisterUsuarioView
'''
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


''' 
    - Avisa al usuario de que la operación no puede realizarse
    porque faltan campos por completar

    @parent: Any
'''
class badQueryDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya...")
        self.setFixedWidth(340)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.clicked.connect(self.accept)
        self.layout = QHBoxLayout()
        self.layout.addWidget(QLabel("Rellene todos los campos primero!"))
        self.layout.addWidget(btnOK, stretch=10)
        self.setLayout(self.layout)


''' 
    - Avisa al usuario de que el login ha sido incorrecto
    debido a un usuario y/o contraseña introducidos erróneos

    @parent: MainView
'''
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


''' 
    - Avisa al usuario de que el login ha sido correcto
    dándole la posibilidad de acceder al sistema o salir
    
    @parent: MainView
'''
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
