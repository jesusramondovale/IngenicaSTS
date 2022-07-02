####################################################################################
#   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    OperacionesView  #
#####################################################################################

import datetime
import sqlite3
import random
import datetime, time

from datetime import datetime, timedelta
from PyQt5 import uic, QtWebEngineWidgets
from PyQt5.QtWidgets import *
from src.util.dialogs import operationCompleteDialog, badQueryDialog, badOperationDialog
from src.util.fundUtils import *

'''
    @parent: UserView
    @returns: None
'''


class OperacionesVentaView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)

        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/OperacionesView.ui", view)

        # Conexión del Botón ENVIAR y el CheckBox Destino a la lógica de control
        view.buttonEnviar.clicked.connect(view.enviar)

        view.tfParticipaciones.textChanged.connect(view.refreshImporte)


        # Conexión con la BD y creación de un cursor de consultas
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()

        # Carga de todas las Fondos en la Cartera actual del Usuario
        view.isins_usuario = db.execute(
            "SELECT ca.Nombre FROM carteras_usuario_real cr " +
            "INNER JOIN caracterizacion ca USING(ISIN) " +
            "WHERE cr.id_usuario = ? AND cr.nombre_cartera = ?",
            ([view.parent().id_usuario[0], parent.currentCarteraReal])).fetchall()

        for e in view.isins_usuario:
            view.cbOrigen.addItem(e[0])

        tmp = db.execute('select titular from carteras_usuario_real where id_usuario == ? '
                         'group by titular', ([view.parent().id_usuario[0]])).fetchall()

        for e in tmp:
            view.cbTitular.addItem(e[0])

        db.close()


    '''
        - Actualiza automáticamente el valor del campo 'Importe'
        en función de las participaciones introducidas en el campo
        tfParticipaciones, haciendo uso del último valor disponible 
        del fondo en cuestión 
        
        @ params: self
        @ returns: None
    '''

    def refreshImporte(self):

        # Conexión con la BD y creación de un cursor de consultas
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()

        fondo = self.cbOrigen.currentText()
        isin = FundtoISINOffline(fondo)

        try:
            part = int(self.tfParticipaciones.text())
        except:
            return

        lastValue = db.execute('SELECT Close FROM ' + '[' + isin + '] '
                                                                   'ORDER BY Date DESC LIMIT 1').fetchone()
        importe = part * lastValue[0]
        self.tfImporte.setText(str(importe))



    '''
        - Ejecuta la operación demandada por el usuario
        tomando los valores suministrados en la interfaz.
        Escribe la Operación a ejecutar en la tabla 
        'Operaciones' de la BD

        @params: self (OperacionesView)
        @returns: None
    '''

    def enviar(self):

        # Conexión con la BD y creación de un cursor de consultas
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()

        print('Pulsación boton  (Venta)\n' +
              'Con Origen: ' + self.cbOrigen.currentText())
        ISIN_origen = db.execute("select ISIN , Participaciones , Importe , Porcentaje "
                                   "from ( select t.*, row_number() over(partition by ISIN "
                                   "order by Fecha desc) rn "
                                   "from [" + str(self.parent().id_usuario[0]) + "_" +
                                   str(self.parent().currentCarteraReal) + "] t) t "
                                  "where rn = 1 and ISIN = ? order by ISIN", ([FundtoISINOffline(self.cbOrigen.currentText())])).fetchone()

        newOrigen = False
        if ISIN_origen is None:
            ISIN_origen = [(FundtoISINOffline(self.cbOrigen.currentText())), 0,0,0]

        if self.camposLlenos():

            if ISIN_origen[2] >= int(self.tfImporte.text()) and ISIN_origen[1] >= int(self.tfParticipaciones.text()):
                # Captura de la fecha y hora de operación
                t = time.localtime()



                # Captura de los ISINS seleccionados
                ISINorigen = db.execute(('SELECT ISIN FROM caracterizacion WHERE Nombre = ?'),
                                        [self.cbOrigen.currentText()]).fetchone()
                valorDestino = None

                # Escribe en la 'cartilla' de operaciones
                SQL = 'INSERT INTO operaciones VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
                random_number = random.randint(0, 200000000)
                hex_number = format(random_number, 'x')

                db.execute(SQL, [
                    hex_number,
                    datetime.today().strftime('%d/%m/%Y'),
                    'ENVIADA',
                    self.parent().id_usuario[0],
                    self.parent().currentCarteraReal,
                    self.cbTitular.currentText(),
                    time.strftime('%H.%M', t),
                    self.tfHoraCorte.text(),
                    'I',
                    self.tfValorOrigen.text(),
                    valorDestino,
                    'D',
                    ISINorigen[0],
                    self.tfParticipaciones.text(),
                    self.tfImporte.text(),
                    'Monedero'

                ])

                # Calcula el valor total de Cartera actual a fecha última (hoy)

                importeTotal = 0
                ISINS_cartera = db.execute("select ISIN , Participaciones , Importe , Porcentaje "
                                           "from ( select t.*, row_number() over(partition by ISIN "
                                           "order by Fecha desc) rn "
                                           "from [" + str(self.parent().id_usuario[0]) + "_" +
                                           str(self.parent().currentCarteraReal) + "] t) t "
                                                                                   "where rn = 1 order by ISIN",
                                           ([])).fetchall()

                # Recorre los ISINS en Cartera
                for isins in ISINS_cartera:
                    isin_origen = db.execute("SELECT ISIN FROM caracterizacion WHERE Nombre = ?",
                                             ([self.cbOrigen.currentText()])).fetchone()[0]
                    if not isins[0] == isin_origen:
                        importeTotal = importeTotal + isins[2]
                    else:
                        importeTotal = importeTotal + isins[2] - int(self.tfImporte.text())



                # Recorre los fondos de cartera actual
                for isin in ISINS_cartera:
                    isin_origen = db.execute("SELECT ISIN FROM caracterizacion WHERE Nombre = ?",
                                             ([self.cbOrigen.currentText()])).fetchone()[0]

                    # Compra de participaciones. No hay fondo de destino

                    # Captamos último dato
                    isin_last_data = db.execute("SELECT * FROM [" + str(self.parent().id_usuario[0]) + "_" +
                                                self.parent().currentCarteraReal + "] "
                                                                                   "WHERE ISIN = ? ORDER BY Fecha DESC",
                                                [isin[0]]).fetchone()

                    # Current isin es el seleccionado
                    if isin_origen == isin[0]:

                        db.execute("INSERT INTO [" + str(self.parent().id_usuario[0]) + "_" +
                                   self.parent().currentCarteraReal + "]"
                                                                      "VALUES (?,?,?,?,?)",
                                   [datetime.today().strftime('%Y%m%d %H%M%S%f'),
                                    isin[0],
                                    isin_last_data[2] - int(self.tfParticipaciones.text()),
                                    isin_last_data[3] - int(self.tfImporte.text()),
                                    int(isin_last_data[3] - int(self.tfImporte.text())) / importeTotal * 100
                                    ])



                    # Current isin no es el que varía
                    else:

                        # Captamos último dato
                        isin_last_data = db.execute("SELECT * FROM [" + str(self.parent().id_usuario[0]) + "_" +
                                                    self.parent().currentCarteraReal + "] "
                                                                                       "WHERE ISIN = ? ORDER BY Fecha DESC",
                                                    [isin[0]]).fetchone()

                        try:
                            db.execute("INSERT INTO [" + str(self.parent().id_usuario[0]) + "_" +
                                       self.parent().currentCarteraReal + "]"
                                                                          "VALUES (?,?,?,?,?)",
                                       [datetime.today().strftime('%Y%m%d %H%M%S%f'),
                                        isin[0],
                                        isin_last_data[2],
                                        isin_last_data[3],
                                        isin_last_data[3] / importeTotal * 100
                                        ])
                        except TypeError:
                            db.execute("INSERT INTO [" + str(self.parent().id_usuario[0]) + "_" +
                                       self.parent().currentCarteraReal + "]"
                                                                          "VALUES (?,?,?,?,?)",
                                       [datetime.today().strftime('%Y%m%d %H%M%S%f'),
                                        isin[0],
                                        int(self.tfParticipaciones.text()),
                                        int(self.tfImporte.text()),
                                        int(self.tfImporte.text()) / importeTotal * 100
                                        ])

                print('TOTAL EN CARTERA TRAS VENTA ($) = ' + str(importeTotal))
                self.parent().labelValorTotal.setText("{:.2f}".format(importeTotal) + '€')

                self.parent().monedero = self.parent().monedero + int(self.tfImporte.text())

                db.execute('UPDATE users SET monedero = ? WHERE id = ?',
                           ([self.parent().monedero, self.parent().id_usuario[0]]))



                db_connection.commit()
                db.close()
                operationCompleteDialog(self).exec()
                self.parent().refreshLabelCartera(self.parent().currentCarteraReal)
                self.parent().UpdateTableOperaciones(self.parent().currentCarteraReal)
                self.parent().updatePieChart(self.parent().currentCarteraReal)
                self.parent().refreshIsinsEnCartera()

                self.hide()
            else:
                badOperationDialog(self).exec()


        else:
            badQueryDialog(self).exec()


    '''
        - Retorna cierto si todos los campos necesarios para 
        realizar la operación están cubiertos
    '''

    def camposLlenos(self):

        if (
                self.tfParticipaciones.text() and
                self.tfImporte.text() and
                self.tfValorOrigen.text() and
                self.tfHoraCorte.text()):
            return True

        else:
            return False
