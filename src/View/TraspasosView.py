####################################################################################
#   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    OperacionesView  #
#####################################################################################
import datetime
import sqlite3
import datetime, time
from datetime import datetime, timedelta
from PyQt5 import uic, QtWebEngineWidgets

from PyQt5.QtWidgets import *

from src.util.dialogs import operationCompleteDialog, badQueryDialog
from src.util.fundUtils import *
'''
    @parent: UserView
    @returns: None
'''


class TraspasosView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)

        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/TraspasosView.ui", view)

        # Conexión del Botón ENVIAR y el CheckBox Destino a la lógica de control
        view.buttonEnviar.clicked.connect(view.enviar)

        # Conexión con la BD y creación de un cursor de consultas
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()



        # Carga de todas las Fondos en la Cartera actual del Usuario
        view.isins_usuario = db.execute(
            "SELECT ca.Nombre FROM carteras_usuario_real cr " +
            "INNER JOIN caracterizacion ca USING(ISIN) " +
            "WHERE cr.id_usuario = ? AND cr.nombre_cartera = ?",
            ([parent.id_usuario[0], parent.cbCarterasReal.currentText()])).fetchall()

        for e in view.isins_usuario:
            view.cbOrigen.addItem(e[0])
            view.cbDestino.addItem(e[0])

        db.close()

    '''
        - Ejecuta la operación demandada por el usuario
        tomando los valores suministrados en la interfaz.
        Escribe la Operación a ejecutar en la tabla 
        'Operaciones' de la BD
        
        @params: self (OperacionesView)
        @returns: None
    '''

    def enviar(self):
        print('Pulsación boton Enviar\n' +
              'Con Origen: ' + self.cbOrigen.currentText() + '\n' +
              'Con Destino: ' + self.cbDestino.currentText())

        if self.camposLlenos():
            # Captura de la hora de operación
            t = time.localtime()

            # Conexión con la BD y creación de un cursor de consultas
            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()

            # Captura de los ISINS seleccionados
            ISINorigen = db.execute(('SELECT ISIN FROM caracterizacion WHERE Nombre = ?'),
                                    [self.cbOrigen.currentText()]).fetchone()
            ISINdestino = None
            valorDestino = None

            tmp = db.execute(('SELECT ISIN FROM caracterizacion WHERE Nombre = ?'),
                                 [self.cbDestino.currentText()]).fetchone()
            ISINdestino = tmp[0]
            if self.tfValorDestino.text():
                valorDestino = self.tfValorDestino.text()

            SQL = 'INSERT INTO operaciones VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            db.execute(SQL, [

                datetime.today().strftime('%d/%m/%Y'),
                'ENVIADA',
                self.parent().id_usuario[0],
                self.parent().cbCarterasReal.currentText(),
                self.tfTitular.text(),
                time.strftime('%H.%M', t),
                self.tfHoraCorte.text(),
                'I',
                self.tfValorOrigen.text(),
                valorDestino,
                'D',
                ISINorigen[0],
                self.tfParticipaciones.text(),
                self.tfImporte.text(),
                ISINdestino

            ])

            # Calcula el valor total de Cartera actual a fecha de HOY

            importeTotal = 0
            ISINS_cartera = db.execute("select ISIN , Participaciones , Importe , Porcentaje "
                                       "from ( select t.*, row_number() over(partition by ISIN "
                                       "order by Fecha desc) rn "
                                       "from [" + str(self.parent().id_usuario[0]) + "_" +
                                       self.parent().cbCarterasReal.currentText() + "] t) t "
                                       "where rn = 1 order by ISIN",
                                       ([])).fetchall()

            # Recorre los ISINS en Cartera
            for isins in ISINS_cartera:
                isin_origen = db.execute("SELECT ISIN FROM caracterizacion WHERE Nombre = ?",
                                         ([self.cbOrigen.currentText()])).fetchone()[0]



                if not isins[0] == isin_origen:
                    importeTotal = importeTotal + isins[2]
                else:
                    importeTotal = importeTotal + isins[2]

            print('TOTAL EN CARTERA ($) = ' + str(importeTotal))

            isin_origen = db.execute("SELECT ISIN FROM caracterizacion WHERE Nombre = ?",
                                     ([self.cbOrigen.currentText()])).fetchone()[0]

            isin_destino = db.execute("SELECT ISIN FROM caracterizacion WHERE Nombre = ?",
                                      ([self.cbDestino.currentText()])).fetchone()[0]

            # Recorre los fondos de cartera actual
            for isin in ISINS_cartera:


                # Transferencia de participaciones. Sí hay fondo de destino
                 # Captamos último dato
                isin_last_data = db.execute("SELECT * FROM [" + str(self.parent().id_usuario[0]) + "_" +
                                                self.parent().cbCarterasReal.currentText() + "] "
                                                "WHERE ISIN = ? ORDER BY Fecha DESC",
                                                [isin[0]]).fetchone()

                # Current isin es el seleccionado como origen
                if isin_origen == isin[0]:
                        db.execute("INSERT INTO [" + str(self.parent().id_usuario[0]) + "_" +
                                   self.parent().cbCarterasReal.currentText() + "]"
                                   "VALUES (?,?,?,?,?)",
                                   [datetime.today().strftime('%Y%m%d %H%M%S%f'),
                                    isin[0],
                                    isin_last_data[2] - int(self.tfParticipaciones.text()),
                                    isin_last_data[3] - int(self.tfImporte.text()),
                                    int(isin_last_data[3] - int(self.tfImporte.text())) / importeTotal * 100
                                    ])
                else:

                    # Current isin es el seleccionado como destino
                    if isin_destino == isin[0]:
                        db.execute("INSERT INTO [" + str(self.parent().id_usuario[0]) + "_" +
                                       self.parent().cbCarterasReal.currentText() + "]"
                                                                                    "VALUES (?,?,?,?,?)",
                                       [datetime.today().strftime('%Y%m%d %H%M%S%f'),
                                        isin[0],
                                        isin_last_data[2] + int(self.tfParticipaciones.text()),
                                        isin_last_data[3] + int(self.tfImporte.text()),
                                        int(isin_last_data[3] + int(self.tfImporte.text())) / importeTotal * 100
                                        ])

                    # Current isin no es el que varía
                    else:

                        # Captamos último dato
                        isin_last_data = db.execute("SELECT * FROM [" + str(self.parent().id_usuario[0]) + "_" +
                                                        self.parent().cbCarterasReal.currentText() + "] "
                                                        "WHERE ISIN = ? ORDER BY Fecha DESC",
                                                        [isin[0]]).fetchone()

                        db.execute("INSERT INTO [" + str(self.parent().id_usuario[0]) + "_" +
                                       self.parent().cbCarterasReal.currentText() + "]"
                                                                                    "VALUES (?,?,?,?,?)",
                                       [datetime.today().strftime('%Y%m%d %H%M%S%f'),
                                        isin[0],
                                        isin_last_data[2],
                                        isin_last_data[3],
                                        isin_last_data[3] / importeTotal * 100
                                        ])

            db_connection.commit()
            db.close()
            operationCompleteDialog(self).exec()
            self.parent().UpdateTableOperaciones()
            self.parent().updatePieChart()
            self.hide()

        else:
            badQueryDialog(self).exec()





    '''
        - Retorna cierto si todos los campos necesarios para 
        realizar la operación están cubiertos
    '''

    def camposLlenos(self):

        if (self.tfTitular.text() and
                self.tfParticipaciones.text() and
                self.tfImporte.text() and
                self.tfValorOrigen.text() and
                self.tfHoraCorte.text() and
                self.tfValorDestino.text()):
                    return True

        else:
              return False