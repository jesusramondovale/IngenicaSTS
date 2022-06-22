########################################################
#   DIÁLOGOS ÚTILES PARA LA MUESTRA DE INFORMACIÓN   ##
#         AL USUARIO DE LA APLICACIÓN                ##
#########################################################
from PyQt5.QtWidgets import QDialog, QPushButton, QGridLayout, QLabel, QHBoxLayout, QVBoxLayout
from PyQt5 import QtCore


'''
    - Avisa al Usuario de que está a punto de actualizar 
    los registros de la tabla operaciones

    @parent: UserView 
'''


class confirmSaveDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("¿Seguro?")
        self.setFixedWidth(380)

        # CONTENIDO
        btnYes = QPushButton('Confirmar')
        btnNo = QPushButton('Cancelar')
        btnYes.setFixedWidth(100)
        btnYes.setFixedHeight(20)
        btnNo.setFixedWidth(100)
        btnNo.setFixedHeight(20)


        btnYes.clicked.connect(self.accept)
        btnNo.clicked.connect(self.reject)

        self.layoutVert = QVBoxLayout()
        self.layoutVert.addWidget(QLabel("¿Está seguro de que desea continuar?"))
        self.layoutVert.addWidget(QLabel("Revise los datos introducidos"))

        self.layoutHor = QHBoxLayout()
        self.layoutHor.addWidget(btnYes)
        self.layoutHor.addWidget(btnNo)

        self.layoutVert.addLayout(self.layoutHor)

        self.setLayout(self.layoutVert)



'''
    - Avisa al Usuario de que está intentando realizar una operación
    sobre cartera real con parámetros erróneos

    @parent: UserView

'''
class badOperationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya..")
        self.setFixedWidth(400)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "Fondos Insuficientes para realizar la operación!"))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)



'''
    - Avisa al Usuario de que está intentando añadir un fondo
    con un valor de Renta Variable erróneo

    @parent: AddISINViewReal

'''
class badRVdialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya..")
        self.setFixedWidth(330)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            parent.tfRV.text() + " no es un valor de R.V válido!"))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)



'''
    - Avisa al Usuario de que está a punto de actualizar online 
    los registros de fondos históricos 

    @parent: UserView 
'''


class confirmAutoRefresh(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("¿Seguro?")
        self.setFixedWidth(380)

        # CONTENIDO
        btnYes = QPushButton('Confirmar')
        btnNo = QPushButton('Cancelar')
        btnYes.setFixedWidth(100)
        btnYes.setFixedHeight(20)
        btnNo.setFixedWidth(100)
        btnNo.setFixedHeight(20)


        btnYes.clicked.connect(self.accept)
        btnNo.clicked.connect(self.reject)

        self.layoutVert = QVBoxLayout()
        self.layoutVert.addWidget(QLabel("¿Está seguro de que desea continuar?"))
        self.layoutVert.addWidget(QLabel("Esta operación puede tardar varios segundos"))

        self.layoutHor = QHBoxLayout()
        self.layoutHor.addWidget(btnYes)
        self.layoutHor.addWidget(btnNo)

        self.layoutVert.addLayout(self.layoutHor)

        self.setLayout(self.layoutVert)


class badPasswords(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya..")
        self.setFixedWidth(330)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "Las contraseñas no coinciden!\nInténtelo de nuevo"))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


class userChangedSuccesfully(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Éxito!")
        self.setFixedWidth(330)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "El cambio de contraseña \nse ha realizado correctamente"))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


class userNotFound(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya..")
        self.setFixedWidth(330)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "No existe el usuario con \nnombre " + self.parent().tfNombre.text()))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)




'''
    - Avisa al Usuario de que está intentando actualizar un fondo
    online sin conexión a Internet 

    @parent: UserView 
'''

class connectionError(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya..")
        self.setFixedWidth(330)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "No se ha podido descargar!\nInténtelo de forma manual"))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


'''
    - Avisa al Usuario de que está a punto de Cerrar su seción
    (hacer logout), permitiéndole confirmar o cancelar su 
    operación
    
    @parent: UserView
    
'''


class confirmLogoutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("¿Seguro?")
        self.setFixedWidth(330)

        # CONTENIDO
        btnYes = QPushButton('Confirmar')
        btnNo = QPushButton('Cancelar')
        btnYes.setFixedWidth(100)
        btnYes.setFixedHeight(20)
        btnNo.setFixedWidth(100)
        btnNo.setFixedHeight(20)

        btnYes.clicked.connect(self.accept)
        btnNo.clicked.connect(self.reject)

        self.layoutVert = QVBoxLayout()
        self.layoutVert.addWidget(QLabel("¿Está seguro de que desea\ncerrar su sesión?"))

        self.layoutHor = QHBoxLayout()
        self.layoutHor.addWidget(btnYes)
        self.layoutHor.addWidget(btnNo)

        self.layoutVert.addLayout(self.layoutHor)

        self.setLayout(self.layoutVert)



'''
    - Avisa al Usuario de que no ha seleccionado ningún elemento 
    (cartera/fondo) en la vista y que debe hacerlo para ejecutar 
    la operación de borrado 

    @parent: UserView 
'''


class selectAnyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Vaya...")
        self.setFixedWidth(330)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "Seleccione primero un elemento\n para eliminar."))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


'''
    - Avisa al Usuario de que está a punto de borrar una de sus carteras
    permitiéndole cancelar o confirmar su acción. 

    @parent: UserView 
'''


class confirmDeleteCarteraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("¿Seguro?")
        self.setFixedWidth(330)

        # CONTENIDO
        btnYes = QPushButton('Confirmar')
        btnNo = QPushButton('Cancelar')
        btnYes.setFixedWidth(100)
        btnYes.setFixedHeight(20)
        btnNo.setFixedWidth(100)
        btnNo.setFixedHeight(20)

        btnYes.clicked.connect(self.accept)
        btnNo.clicked.connect(self.reject)

        self.layoutVert = QVBoxLayout()
        self.layoutVert.addWidget(QLabel("¿Está seguro de que desea\nborrar la cartera seleccionada?"))

        self.layoutHor = QHBoxLayout()
        self.layoutHor.addWidget(btnYes)
        self.layoutHor.addWidget(btnNo)

        self.layoutVert.addLayout(self.layoutHor)

        self.setLayout(self.layoutVert)



'''
    - Avisa al Usuario de que está a punto de borrar un fondo de su cartera
    permitiéndole cancelar o confirmar su acción. 

    @parent: UserView
'''


class confirmDeleteFundDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("¿Seguro?")
        self.setFixedWidth(300)

        # CONTENIDO
        btnYes = QPushButton('Confirmar')
        btnNo = QPushButton('Cancelar')
        btnYes.setFixedWidth(100)
        btnYes.setFixedHeight(20)
        btnNo.setFixedWidth(100)
        btnNo.setFixedHeight(20)
        btnYes.clicked.connect(self.accept)
        btnNo.clicked.connect(self.reject)

        self.layoutVert = QVBoxLayout()
        self.layoutVert.addWidget(QLabel("¿Está seguro de que desea\nborrar el fondo seleccionado?"))

        self.layoutHor = QHBoxLayout()
        self.layoutHor.addWidget(btnYes)
        self.layoutHor.addWidget(btnNo)

        self.layoutVert.addLayout(self.layoutHor)

        self.setLayout(self.layoutVert)


'''
    - Avisa al Usuario de que el fondo ya se encuentra 
    añadido a su cartera actual de usuario. 
    
    @parent: AddISINView 
'''


class downloadingIsinDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Espere...")
        self.setFixedWidth(330)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "El fondo aún está descargándose.\n Espere unos instantes."))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)


'''
    - Avisa al Usuario de que el fondo introducido
    ya está en su cartere
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
        btnOK.setFixedHeight(20)
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
        btnOK.setFixedHeight(20)
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
        btnOK.setFixedHeight(20)
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
        btnOK.setFixedHeight(20)

        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "Se ha producido un error inesperado. \nInténtelo de nuevo."))
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
        self.setFixedWidth(390)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel(
            "La Cartera con nombre : " + parent.tfNombre.text() + " se ha\nañadido correctamente a su cuenta personal."))
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
        self.setFixedWidth(380)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
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
        self.setFixedWidth(330)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("El Registro se ha realizado\nadecuadamente"))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)





''' 
    - Avisa al Usuario de que la operación de fondos en cartera
    ha sido realizada satisfactoriamente

    @parent: UserView
'''
class operationCompleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Éxito!")
        self.setFixedWidth(410)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("La operación se ha realizado adecuadamente"))
        self.layout.addWidget(btnOK, 3, 0, 2, 0, QtCore.Qt.AlignRight)
        self.setLayout(self.layout)



''' 
    - Avisa al Usuario de que la actualización de históricos
    ha sido realizada satisfactoriamente

    @parent: UserView
'''


class refreshCompleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # TITULO  DE  LA VENTANA
        self.setWindowTitle("Éxito!")
        self.setFixedWidth(390)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
        btnOK.clicked.connect(self.accept)
        self.layout = QGridLayout()
        self.layout.addWidget(QLabel("Los datos se han actualizado adecuadamente"))
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
        self.setFixedWidth(350)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
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
        self.setFixedWidth(380)
        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
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
        self.setFixedWidth(330)
        self.setFixedHeight(100)

        # CONTENIDO
        btnOK = QPushButton('OK')
        btnOK.setFixedWidth(50)
        btnOK.setFixedHeight(20)
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
        btnEntrar.setFixedWidth(100)
        btnEntrar.setFixedHeight(20)
        btnSalir.setFixedWidth(100)
        btnSalir.setFixedHeight(20)
        btnEntrar.clicked.connect(self.accept)
        btnSalir.clicked.connect(self.reject)

        self.layout = QHBoxLayout()
        self.layout.addWidget(btnEntrar)
        self.layout.addWidget(btnSalir)

        self.setLayout(self.layout)
