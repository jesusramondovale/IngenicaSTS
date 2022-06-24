#####################################################################################
#   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    ManualRefresh  ####
#####################################################################################
import pandas.errors
import sqlite3 , datetime
from PyQt5 import uic
from PyQt5.QtWidgets import *

import pandas as pd

from src.util.dialogs import badFileDialog, badQueryDialog, operationCompleteDialog, confirmSaveDialog, badDateDialog

class ManualRefreshView(QMainWindow):

    def __init__(view, parent=QMainWindow):

        super().__init__(parent)
        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/ManualRefreshView.ui", view)
        view.tfFichero.setReadOnly(True)

        # Conexión de los eventos de botones clickados a la lógica de los controladores
        view.buttonNueva.clicked.connect(view.nuevaTabla)
        view.buttonOpenFile.clicked.connect(view.openFile)
        view.buttonCorregir.clicked.connect(view.corregir)

    '''
        - Carga el path del fichero .csv en el TextField
    '''
    def openFile(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter(str("Tabla de Excel (*.csv)"))
        if dialog.exec_():
            path = dialog.selectedFiles()[0]
            self.tfFichero.setText(path)


    def ficheroFondoLleno(self):
        if self.tfFondo.text() and self.tfFichero.text():
            return True
        else:
            return False

    '''
           - Actualiza la tabla de históricos 
           del fondo introducido en el TextField
           con los valores de tabla en el fichero.csv
    '''
    def corregir(self):
        if self.ficheroFondoLleno():

            if confirmSaveDialog(self).exec():
                # Conexión con la BD y creación de un cursor de consultas
                db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
                db = db_connection.cursor()

                try:
                    path = self.tfFichero.text()
                    data = pd.read_csv(filepath_or_buffer=path, delimiter=';')

                except:
                    badFileDialog(self).exec()
                    db_connection.close()
                    return

                try:
                    for (column, vals) in data.iteritems():
                        if column == 'Date':
                            for v in vals.values:
                                 datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
                except:
                    badDateDialog(self).exec()
                    db_connection.close()
                    return

                try:

                    data.to_sql(con=db_connection, index=False, name=self.tfFondo.text(), if_exists='append')
                    # Elimina duplicados
                    db.execute('DELETE FROM [' + self.tfFondo.text() + '] '
                               'WHERE RowId NOT IN (SELECT MAX(RowId) '
                               'FROM [' + self.tfFondo.text() + '] '
                               'GROUP BY Date)' , [])

                    db.execute('DELETE FROM [' + self.tfFondo.text() + '] '
                                'WHERE Date IS NULL  ',[])

                    operationCompleteDialog(self).exec()
                    db_connection.close()
                    self.close()

                except:
                    badFileDialog(self).exec()
                    db_connection.close()


        else:
            badQueryDialog(self).exec()
            db_connection.close()





    '''
        - Elimina por completo la tabla de históricos 
        del fondo introducido en el TextField
        y la reemplaza por la tabla en el fichero.csv
    '''
    def nuevaTabla(self):
        if self.ficheroFondoLleno():

            if confirmSaveDialog(self).exec():

                # Conexión con la BD y creación de un cursor de consultas
                db_connection = sqlite3.connect('DemoData.db', isolation_level=None)

                try:
                    path = self.tfFichero.text()
                    data = pd.read_csv(filepath_or_buffer=path, delimiter=';')

                except:
                    badFileDialog(self).exec()
                    db_connection.close()
                    return

                try:
                    for (column, vals) in data.iteritems():
                        if column == 'Date':
                            for v in vals.values:
                                 datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
                except:
                    badDateDialog(self).exec()
                    db_connection.close()
                    return


                try:
                    path = self.tfFichero.text()
                    data = pd.read_csv(filepath_or_buffer=path, delimiter=';')
                    data.to_sql(con=db_connection , index=False , name=self.tfFondo.text() , if_exists='replace')
                    operationCompleteDialog(self).exec()
                    db_connection.close()
                    self.close()

                except:
                    badFileDialog(self).exec()
                    db_connection.close()

        else:
            badQueryDialog(self).exec()
            db_connection.close()
