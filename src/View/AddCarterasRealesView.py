##################################################################################
##   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    AddCarteras  ##
##################################################################################
import sqlite3

from datetime import datetime

# Importamos las librerías de carga y Widgets de Python QT v5
# para graficar el contenido de los ficheros GUI
from PyQt5 import uic
from PyQt5.QtWidgets import *
from src.util.dialogs import *

'''
 - Formulario de adición de nuevos carteras REALES para el usuario actual.
 - @parent: UserView (ventana principal de usuario)
 - @children: carteraAlreadyExistsDialog | CarteraAddedSuccesfully

 - Crea y añade a la BD una nueva Cartera de Usuario
 - Esta ventana podrá ser accesible siempre y cuando 
 un usuario registrado haya hecho su login correctamente.
 - Contiene un formulario simple para introducir el nombre de la 
 cartera a añadir.

'''


# Vista AddCarterasRealesView.ui
class AddCarterasRealesView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)

        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/AddCarterasView.ui", view)

        # Captura del ID de usuario procedente de la vista parent (UserView)
        view.id_usuario = parent.id_usuario

        # Desactiva el botón Crear (hasta que el usuario introduzca un nombre)
        view.buttonCrear.setEnabled(False)

        # Conexión del Botón CREAR a la lógica de control de la función crear
        view.buttonCrear.clicked.connect(view.crear)

        # Conexión de la señal TextChanged del TextField Nombre para la activación del botón
        view.tfNombre.textChanged.connect(view.activarBoton)

    '''
        - Función controladora del evento clicked sobre el botón Crear en la vista actual
        - Añade la Cartera con Nombre introducido en el TextField a la
        cuenta del usuario actual en caso de que el nombre no sea repetido

        @params: self (AddCarterasView)
        @returns: None
    '''

    def crear(self):
        # Conexión con la BD y creación de un cursor de consultas
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()

        # Captura del Nombre introducido en el formulario
        nombre_cartera = self.tfNombre.text()

        # Carga de la posible cartera ya creada previamente con ese mismo nombre
        temp = db.execute("SELECT num_cartera FROM carteras_real WHERE id_usuario = ? AND nombre_cartera = ? ",
                          [self.id_usuario[0], nombre_cartera]).fetchone()

        # Si el usuario NO DISPONE previamente de una cartera con ese mismo nombre
        # entonces temp estará vacío
        if temp is None:

            # Graba en BD la nueva Cartera para el ID de Usuario Actual
            db.execute(
                "INSERT INTO carteras_real VALUES (?,?,?,?) ",
                [self.id_usuario[0], None, nombre_cartera,
                 datetime.today().strftime('%d/%m/%Y')]).fetchone()

            db.execute("CREATE TABLE [" + str(self.id_usuario[0]) + "_" + nombre_cartera + "] ( 'Fecha' TEXT NOT NULL, 'ISIN' TEXT NOT NULL, 'Participaciones' NUMERIC NOT NULL, 'Importe'	NUMERIC NOT NULL, 'Porcentaje' NUMERIC NOT NULL);" , [])

            # Actualiza el valor de las carteras de usuario
            self.carteras_usuario = db.execute(
                "SELECT num_cartera , nombre_cartera FROM carteras_real WHERE id_usuario = ? ORDER BY (nombre_cartera)",
                ([self.id_usuario[0]])).fetchall()

            # Actualiza los nombres de las carteras para rellenar el ComboBox

            # self.carteras_usuario.append([0,nombre_cartera])

            # Activa el botón de Borrar Carteras (por si acaso estaba desactivado)

            # Avisa al usuario de que la operación se ha realizado con éxito
            dlg = CarteraAddedSuccesfully(self)
            dlg.exec()

            # Cierra la ventana de creación de nuevas carteras
            self.hide()

            for i in reversed(range(self.parent().layoutButtonsCarteras.count())):
                if not i == 0:
                    self.parent().layoutButtonsCarteras.itemAt(i).widget().setParent(None)

            for nombre in self.carteras_usuario:
                self.button = QPushButton(nombre[1], self.parent())
                self.button.clicked.connect(
                    lambda clicked, nombre_cartera=self.button.text(): self.parent().updatePieChart(nombre_cartera))

                self.button.clicked.connect(
                    lambda clicked, nombre_cartera=self.button.text(): self.parent().refreshLabelCartera(nombre_cartera))

                self.button.clicked.connect(
                    lambda clicked, nombre_cartera=self.button.text(): self.parent().UpdateTableOperaciones(nombre_cartera))
                self.button.clicked.connect(
                    lambda clicked, isins_selected=self.parent().isins_selected: self.parent().refreshIsinsEnCartera())

                self.parent().layoutButtonsCarteras.addWidget(self.button)



            self.parent().frameButtonsCarteras.setLayout(self.parent().layoutButtonsCarteras)
            self.parent().currentCarteraReal = nombre_cartera
            self.parent().refreshLabelCartera(self.parent().currentCarteraReal)
            self.parent().updatePieChart(self.parent().currentCarteraReal)
            self.parent().UpdateTableOperaciones(self.parent().currentCarteraReal)
            self.parent().refreshIsinsEnCartera()
            self.parent().refreshButtons()

        # El usuario ya dispone con una cartera con ese mismo nombre
        else:
            # Se le informa y no se graba de nuevo una segunda cartera repetida
            dlg = carteraAlreadyExistsDialog(self)
            dlg.exec()

    '''
        - Función controladora del evento TextChanged sobre 
        el TextField Nombre de la vista actual para activar
        o desactivar el botón de Crear Cartera

        @params: self (AddCarterasView)
        @returns: None
    '''

    def activarBoton(self):
        if self.tfNombre.text():
            self.buttonCrear.setEnabled(True)
        else:
            self.buttonCrear.setEnabled(False)