####################################################################################
#   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    OperacionesView  #
#####################################################################################
import datetime
import sqlite3
import datetime, time
from datetime import datetime, timedelta

from PyQt5 import uic
from PyQt5.QtWidgets import *

from src.util.dialogs import operationCompleteDialog, badQueryDialog
'''
    @parent: UserView
    @returns: None
'''


class OperacionesView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)

        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/OperacionesView.ui", view)

        # Conexión del Botón ENVIAR y el CheckBox Destino a la lógica de control
        view.buttonEnviar.clicked.connect(view.enviar)
        view.checkBoxDestino.stateChanged.connect(view.refreshDestino)

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
            if self.checkBoxDestino.isChecked():
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
            operationCompleteDialog(self).exec()
            self.parent().UpdateTableOperaciones()
            self.hide()
        else:
            badQueryDialog(self).exec()


    '''
        - Activa/Desactiva los QLineEdit del Fondo Destino
        al pulsar el CheckBox
    '''

    def refreshDestino(self):

        if self.checkBoxDestino.isChecked():
            print('Destino checked')
            self.cbDestino.setEnabled(True)
            self.tfValorDestino.setEnabled(True)

        else:
            print('Destino unchecked')

            self.cbDestino.setEnabled(False)
            self.tfValorDestino.setEnabled(False)


    '''
        - Retorna cierto si todos los campos necesarios para 
        realizar la operación están cubiertos
    '''
    def camposLlenos(self):
        if(self.tfTitular.text() and
           self.tfParticipaciones.text() and
           self.tfImporte.text() and
           self.tfValorOrigen.text() and
           self.tfHoraCorte.text() ):

                if self.checkBoxDestino.isChecked():
                    if self.tfValorDestino.text() and self.cbDestino.currentText() != 'Ninguno':
                        return True
                    else: return False
        else:
            return False