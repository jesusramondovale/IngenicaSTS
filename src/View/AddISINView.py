##############################################################################
##   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    AddISIN  ##
##############################################################################

import sqlite3

# Importamos las librerías de carga y Widgets de Python QT v5
# para graficar el contenido de los ficheros GUI
import threading

from PyQt5 import uic
from PyQt5.QtWidgets import *

# Librerías útiles personalizadas para consulta de datos sobre fondos
from src.util import fundUtils

# Diálogos personalizados para mostrar avisos al usuario
from src.util.dialogs import *

# Vista AddISINView.ui
'''
 - Formulario de adición de nuevos fondos a la cartera actual.
 - @parent: UserView (ventana principal de usuario)
 - @children: isinAlreadyDialog | isinNotFoundDialog |  TickerAddedSuccesfully
 
 - Busca en investing.com por ISIN/Symbol introducido y añade 
 la info del fondo a la tabla de caracterización. 
 - Esta ventana podrá ser accesible siempre y cuando 
 un usuario registrado haya hecho su login y se encuentre
 en su ventana principal, y además tenga carteras creadas.
 - Contiene un formulario para introducir la información
 del fondo a añadir.
 
'''


class AddISINView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)

        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/AddISINView.ui", view)

        # Conexión del Botón AÑADIR y REFRESH a la lógica de control
        view.buttonAnadir.clicked.connect(lambda clicked, ticker=view.tfISIN.text(): view.addTicker(parent))
        view.buttonRefresh.clicked.connect(view.refresh)

    '''
    - Comprueba que todos los campos del formulario han sido rellenados
    @params: self (la propia instancia GUI AddISINView)
    @returns : True si todos los campos han sido rellenados
             : False en cualquier otro caso
    '''

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

    '''
        - Controlador del evento clicked sobre el botón REFRESH de la vista AddISINView
        - Refresca los campos "Nombre" , "Zona" y "Divisa" automáticamente
        con los valores correspondientes al ISIN/Symbol introducido descargando
        la información de Internet (investing.com)
    '''
    def refresh(self):


        # Caputrar el ISIN/SYmbol
        ISIN = self.tfISIN.text().strip()

        if ISIN != '':
            # Si existe, se desarga su información y se escribe en el formulario
            try :
                name = fundUtils.getFundINFO(self, ISIN).at[0, 'name']
                currency = fundUtils.getFundINFO(self, ISIN).at[0, 'currency']
                country = fundUtils.getFundINFO(self, ISIN).at[0, 'country'].capitalize()
                tipo = fundUtils.getFundINFO(self, ISIN).at[0, 'asset_class'].capitalize()

                self.tfNombre.setText(name)
                self.tfDivisa.setText(currency)
                self.tfZona.setText(country)
                self.tfTipoAct.setText(tipo)

            except RuntimeError:
                dlg = isinNotFoundDialog(self)
                dlg.exec()

        else :
            pass


    '''
    - Añade el ISIN/Symbol introducido en el formulario 
    a la cartera actual, si existe en investing.com
    @params : self (propio GUI) , parent (GUI del padre: UserView)
    '''

    def addTicker(self, parent):

        # Validación de que los campos han sido rellenados

        # SI han sido rellenados
        if self.camposLlenos():

            # Conexión con la BD y creación de un cursor de consultas
            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()

            # Captura del ISIN/Symbol introducido en el formulario
            ISIN = self.tfISIN.text().strip()

            # Captura del ID de Usuario Actual a través de BD
            id = db.execute("SELECT id FROM users WHERE nombre = ?", [parent.labelUsuario.text()]).fetchone()

            # Carga del posible mismo ISIN/Symbol ya introducido previamente en cartera actual para el ID de usuario actual
            temp = db.execute(
                "SELECT * FROM carteras_usuario cu INNER JOIN carteras c USING(nombre_cartera)"
                "WHERE cu.id_usuario == ? AND cu.ISIN == ? AND c.nombre_cartera == ? ",
                [id[0], ISIN, parent.cbCarteras.currentText()]).fetchone()

            # Si el usuario YA DISPONE de ese ISIN/Symbol en su cartera actual
            # entonces temp no estará vacío -> no se añade dos veces el mismo fondo
            if temp is not None:
                # Muestra el diálogo al usuario avisando de que ya
                # existe ese ISIN/Symbol en su cartera actual
                dlg = ISINAlready(self)
                dlg.exec()
                db.close()

            # El usuario NO DISPONE de dicho ISIN/Symbol en su cartera actual
            else:

                try:
                    # Busca la información del fondo introducido en investing.com
                    # para lanzar un posible RunTimeError (capturado más abajo)
                    # en caso de que el fondo no exista
                    fundUtils.getFundINFO(self, ISIN)

                    # Introduce, si existe, dicho ISIN/Symbol en la cartera actual
                    db.execute("INSERT INTO carteras_usuario VALUES ( ? , ? , ? )",
                               (id[0], parent.cbCarteras.currentText(), ISIN))

                    '''
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
                        '''


                    db.close()

                    # Descarga los históricos completos del fondo y los almacena en BD
                    # (solo en caso de que no existan ya)
                    t = threading.Thread(target=fundUtils.saveHistoricalFund, args=(self, ISIN))
                    t.start()

                    # Añade el NOMBRE del Fondo introducido en la Lista de Cartera de Usuario
                    parent.listIsins.addItem(str(fundUtils.getFundINFO(self, ISIN).at[0, 'name']) + "  (" + ISIN + ")")

                    # Avisa al usuario de la operación completada con éxito y
                    # esconde la ventana actual (vuelve a UserView)
                    dlg = TickerAddedSuccesfully(self)
                    dlg.exec()
                    self.hide()



                # Captura del Error lanzado por la API de investing.com
                # en caso de no encontrarse el ISIN/Symbol introducido
                except RuntimeError:
                    # Avisa al usuario de que el ISIN/Symbol no se encuentra
                    dlg = isinNotFoundDialog(self)
                    dlg.exec()
                    db.close()

        # No han sido rellenados todos los campos del formulario
        else:
            # Avisa al usuario de la necesidad de rellenar todos los campos
            dlg = badQueryDialog(self)
            dlg.exec()
