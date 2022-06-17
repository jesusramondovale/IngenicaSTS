##############################################################################
##   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    AddISIN  ##
##############################################################################

import sqlite3
import pycountry_convert as pc


# Importamos las librerías de carga y Widgets de Python QT v5
# para graficar el contenido de los ficheros GUI
import threading

from PyQt5 import uic
from PyQt5.QtWidgets import *
from datetime import date
# Librerías útiles personalizadas para consulta de datos sobre fondos
from src.util import fundUtils

# Diálogos personalizados para mostrar avisos al usuario
from src.util.dialogs import *

# Vista AddISINViewReal.ui
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


class AddISINViewReal(QMainWindow):

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
                    self.tfTipoAct.text() == '' or
                    self.tfDivisa.text() == '' or
                    self.tfCubierta.text() == '' or
                    self.tfRV.text() == ''):
                return False

            else:
                try:
                    float(self.tfRV.text())
                    return True

                except ValueError:
                    badRVdialog(self).exec()
                    return False

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
            try:
                name = fundUtils.getFundINFO(self, ISIN).at[0, 'name']
                currency = fundUtils.getFundINFO(self, ISIN).at[0, 'currency']
                country = fundUtils.getFundINFO(self, ISIN).at[0, 'country'].title()
                sector = fundUtils.getFundINFO(self, ISIN).at[0, 'asset_class'].capitalize()
                issuer = fundUtils.getFundINFO(self, ISIN).at[0, 'issuer']

                self.tfNombre.setText(name)
                self.tfDivisa.setText(currency)
                self.tfPais.setText(country)
                self.tfTipoAct.setText('Fondo')
                self.tfGestora.setText(issuer)
                self.tfSector.setText(sector)

                try:
                    zona = pc.country_alpha2_to_continent_code(pc.country_name_to_country_alpha2(country))
                    self.tfZona.setText(pc.convert_continent_code_to_continent_name(zona))
                except  KeyError:
                    self.tfZona.setText('')
                    pass


            except RuntimeError:
                dlg = isinNotFoundDialog(self)
                self.tfNombre.setText('')
                self.tfGestora.setText('')
                self.tfDivisa.setText('')
                self.tfPais.setText('')
                self.tfZona.setText('')
                self.tfTipoAct.setText('')
                dlg.exec()

        else:
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

            # Carga del posible mismo ISIN/Symbol ya introducido previamente en cartera actual para el ID de usuario
            # actual
            temp = db.execute(
                "SELECT * FROM carteras_usuario_real cu INNER JOIN carteras_real c USING(nombre_cartera)"
                "WHERE cu.id_usuario == ? AND cu.ISIN == ? AND c.nombre_cartera == ? ",
                [id[0], ISIN, self.parent().currentCarteraReal]).fetchone()

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
                    db.execute("INSERT INTO carteras_usuario_real VALUES ( ? , ? , ? )",
                               (id[0], parent.currentCarteraReal, ISIN))

                    # Si el ISIN no ha sido grabado previamente en la tabla caracterización
                    if len(db.execute('SELECT * FROM caracterizacion WHERE ISIN == ?' ,
                                      ([self.tfISIN.text()])).fetchall()) == 0:

                        #Inserción de las características del fondo en la tabla caracterización
                        db.execute("INSERT INTO caracterizacion VALUES (?, ?,  ? , ? , ? , ? , ? , ? , ? , ? , ?  , ? , ? , ?)",
                                       (date.today().strftime('%d/%m/%Y'),
                                        self.tfISIN.text(),
                                        self.tfNombre.text(),
                                        self.tfGestora.text(),
                                        'F',
                                        self.tfRV.text(),
                                        self.tfZona.text(),
                                        self.tfPais.text(),
                                        self.tfEstilo.text(),
                                        self.tfSector.text(),
                                        self.tfTamano.text(),
                                        self.tfDivisa.text(),
                                        self.tfCubierta.text(),
                                        self.tfDuracion.text(),
                                        ))

                    db.close()

                    # Descarga los históricos completos del fondo y los almacena en BD
                    # (solo en caso de que no existan ya)
                    t = threading.Thread(target=fundUtils.saveHistoricalFund, args=(self, ISIN))
                    t.start()

                    # Añade el NOMBRE del Fondo introducido en la Lista de Cartera de Usuario
                    self.parent().isin_list.append(ISIN)

                    #self.parent().ISINS_real.append(ISIN)
                    self.parent().refreshIsinsEnCartera()
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
