###################################################################################
#   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    ConsultasView  ##
###################################################################################

import sys, sqlite3
import pandas as pd
from PyQt5 import uic, QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.Qt import *
from src.util.dialogs import badParamsList

class DragLabel(QLabel):
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        else:
            drag = QDrag(self)

            mimedata = QMimeData()
            mimedata.setText(self.text())

            drag.setMimeData(mimedata)

            # createing the dragging effect
            pixmap = QPixmap(self.size())  # label size

            painter = QPainter(pixmap)
            painter.drawPixmap(self.rect(), self.grab())
            painter.end()

            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.CopyAction | Qt.MoveAction)


class DropListBox(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(300)

    def mimeTypes(self):
        mimeTypes = super().mimeTypes()
        mimeTypes.append('text/plain')
        return mimeTypes

    def dropMimeData(self, index, data, action):
        if data.hasText():

            items = []
            for index in range(self.count()):
                items.append(self.item(index))

            labels = [i.text() for i in items]

            if data.text() not in labels:
                self.addItem(data.text())

            return True
        else:
            return super().dropMimeData(index, data, action)




class ConsultasView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)

        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/ConsultasView.ui", view)


        labelZona = DragLabel('Zona', view)
        labelZona.move(40, 40)

        labelRV = DragLabel('RV', view)
        labelRV.move(40, 65)

        labelEstilo = DragLabel('Estilo', view)
        labelEstilo.move(40, 90)

        labelSector = DragLabel('Sector', view)
        labelSector.move(110, 40)

        labelTamano = DragLabel('Tamaño', view)
        labelTamano.move(110, 65)

        labelDivisa = DragLabel('Divisa', view)
        labelDivisa.move(110, 90)

        listCols = DropListBox(view)
        listCols.move(30, 170)

        listCols.setFixedHeight(190)
        listCols.setFixedWidth(73)

        view.buttonLimpiar.clicked.connect(
            lambda clicked, view=view: listCols.clear())


        view.buttonCrear.clicked.connect(
            lambda clicked, view=view: view.crearTablaAgregados(listCols))


    def crearTablaAgregados(self, listCols=None, fecha=None):

        if listCols.count() != 0:

            print('crearTablaAgregados()')

            # Captar el orden de agregación seleccionado
            cols = [str(listCols.item(i).text()) for i in range(listCols.count())]

            # Captar el estado de cartera
            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()

            if fecha and self.parent().currentCarteraReal is not None:
                # TODO
                pass

            if not fecha and self.parent().currentCarteraReal is not None:
                sql = pd.read_sql_query('select ISIN , c.Zona , c.RV , c.Estilo , c.Tamaño, c.Divisa, c.Sector , Participaciones , Importe '
                                        'from ( select t.*, row_number() over(partition by ISIN order by Fecha desc) rn '
                                        'from [' + str(self.parent().id_usuario[0]) + '_' + str(
                    self.parent().currentCarteraReal) +
                                        '] t) t inner join caracterizacion c using (ISIN) '
                                        'where rn = 1 order by ISIN', db_connection)

                tmp = db.execute('select ISIN , c.Zona , c.RV , c.Estilo , c.Tamaño, c.Divisa, c.Sector , Participaciones , Importe '
                                 'from ( select t.*, row_number() over(partition by ISIN order by Fecha desc) rn '
                                 'from [' + str(self.parent().id_usuario[0]) + '_' + str(self.parent().currentCarteraReal) +
                                 '] t) t inner join caracterizacion c using (ISIN) '
                                 'where rn = 1 order by ISIN').fetchall()

                data = pd.DataFrame(tmp, columns=['ISIN', 'Zona', 'RV', 'Estilo', 'Tamaño', 'Divisa' , 'Sector' , 'Participaciones', 'Importe'])

                params = [str(listCols.item(i).text()) for i in range(listCols.count())]

                data1 = (data.groupby(params)
                         .agg(
                    Participaciones=('Participaciones', 'sum'),
                    Importe=('Importe', 'sum'))
                         .reset_index()
                         .head())

                print(data1)

            return

        # No hay parámetros
        else:
            badParamsList(self).exec()

    def refreshButton(self , listCols):

        print('refreshButton()')

        if listCols.count() > 0:
            self.buttonCrear.setEnabled(True)
        else:
            self.buttonCrear.setEnabled(False)
