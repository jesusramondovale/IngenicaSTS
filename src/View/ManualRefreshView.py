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

        # TextField no modificable
        view.tfFichero.setReadOnly(True)

        # Conexión de los eventos de botones clickados a la lógica de los controladores
        view.buttonNueva.clicked.connect(view.nuevaTabla)
        view.buttonOpenFile.clicked.connect(view.openFile)
        view.buttonCorregir.clicked.connect(view.corregir)


    '''
        - Carga el path del fichero .csv en el TextField
        
        @params: self (ManualRefreshView
    '''
    def openFile(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setNameFilter(str("Tabla de Excel (*.csv)"))
        if dialog.exec_():
            path = dialog.selectedFiles()[0]
            self.tfFichero.setText(path)


    '''
        - Comprueba si el fichero ha sido seleccionado 
        y el nombre del fondo ha sido rellenado 
        
        @returns : True si han sido rellenados
                   False en caso contrario
    '''
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

        # Comprueba si han sido rellenados los parámetros (fichero y nombre)
        if self.ficheroFondoLleno():

            # Diálogo de confirmación
            if confirmSaveDialog(self).exec():

                # Conexión con la BD y creación de un cursor de consultas
                db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
                db = db_connection.cursor()

                try:
                    # Captura la ruta escrita previamente en el TextField
                    path = self.tfFichero.text()

                    # Genera el DataFrame leyendo del fichero
                    data = pd.read_csv(filepath_or_buffer=path, delimiter=';')

                # Error en read_csv -> ficher erróneo
                except:
                    badFileDialog(self).exec()
                    db_connection.close()
                    return

                # Examina todas y cada una de las celdas de la columna Date
                # para comprobar si cumplen el formato adecuado
                try:
                    for (column, vals) in data.iteritems():
                        if column == 'Date':
                            for v in vals.values:
                                 datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")

                #Captura la excepción de formato no adecuado
                except:

                    #Diálogo de aviso
                    badDateDialog(self).exec()
                    db_connection.close()
                    return

                try:
                    # Escribe en DB el DataFrame generado previamente
                    data.to_sql(con=db_connection, index=False, name=self.tfFondo.text(), if_exists='append')

                    # Elimina duplicados
                    db.execute('DELETE FROM [' + self.tfFondo.text() + '] '
                               'WHERE RowId NOT IN (SELECT MAX(RowId) '
                               'FROM [' + self.tfFondo.text() + '] '
                               'GROUP BY Date)' , [])

                    db.execute('DELETE FROM [' + self.tfFondo.text() + '] '
                                'WHERE Date IS NULL  ',[])

                    #Diálogo de operación completada
                    operationCompleteDialog(self).exec()
                    db_connection.close()
                    self.close()

                #Capturamos error genérico
                except:
                    badFileDialog(self).exec()
                    db_connection.close()


        # No se han seleccionado un fichero y escrito un nombre
        else:
            # Aviso: se deben completar los campos
            badQueryDialog(self).exec()
            db_connection.close()
            return


    '''
        - Elimina por completo la tabla de históricos 
        del fondo introducido en el TextField
        y la reemplaza por la tabla en el fichero.csv
    '''
    def nuevaTabla(self):

        # Comprueba si han sido rellenados los parámetros (fichero y nombre)
        if self.ficheroFondoLleno():

            # Diálogo de confirmación
            if confirmSaveDialog(self).exec():

                # Conexión con la BD y creación de un cursor de consultas
                db_connection = sqlite3.connect('DemoData.db', isolation_level=None)

                # Captura la ruta escrita previamente en el TextField
                try:
                    path = self.tfFichero.text()
                    data = pd.read_csv(filepath_or_buffer=path, delimiter=';')

                # Captura del error por fichero corrupto
                except:
                    badFileDialog(self).exec()
                    db_connection.close()
                    return

                # Examina todas y cada una de las celdas de la columna Date
                # para comprobar si cumplen el formato adecuado
                try:
                    for (column, vals) in data.iteritems():
                        if column == 'Date':
                            for v in vals.values:
                                 datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")

                # Captura la excepción de formato no adecuado
                except:
                    badDateDialog(self).exec()
                    db_connection.close()
                    return

                # Escribe en DB el DataFrame generado previamente
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

        #Si no se han llenado los campos
        else:
            badQueryDialog(self).exec()
            db_connection.close()
