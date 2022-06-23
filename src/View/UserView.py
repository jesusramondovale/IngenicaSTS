###############################################################################
#   GUI  Y  LÓGICA   DE    PROGRAMACIÓN    DE     LA     VISTA    UserView  ##
###############################################################################
import sqlite3, time, datetime
import PySide2
import sys,os
import pandas as pd

# Importamos las librerías de carga y Widgets de Python QT v5
# para graficar el contenido de los ficheros GUI
from PyQt5 import uic, QtWebEngineWidgets
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import ctypes

myappid = u'IngenicaSTS.Software.GestorETF.v7'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# Importamos la lógica de otras vistas
from highstock import Highstock
from highcharts import Highchart
from PyQt5.uic.uiparser import QtWidgets

from src.View.AddCarterasView import AddCarterasView
from src.View.AddISINView import AddISINView
from src.View.ConfigView import ConfigView
from src.View.cargandoView import cargandoView
from src.View.TraspasosView import TraspasosView
from src.View.OperacionesView import OperacionesView
from src.View.OperacionesVentaView import OperacionesVentaView

from src.View.AddCarterasRealesView import AddCarterasRealesView
from src.View.AddISINViewReal import AddISINViewReal

from src.util import fundUtils
from src.util.dialogs import *


'''
    - Ventana de Operaciones General para el Usuario 
    - En ella se podrán añadir Carteras, Fondos a Cada Una de ellas,
     así como graficar los Fondos seleccionados.
     
     @parent: MainView
     @children: AddAny | MainView
'''


# Vista PrincipalUsuario.ui
class UserView(QMainWindow):

    def __init__(view, parent=QMainWindow):
        super().__init__(parent)

        # Carga de la interfaz gráfica
        uic.loadUi("src/GUI/PrincipalUsuario.ui", view)

        # Selector de Fecha
        view.selectorFecha = QDateEdit(calendarPopup=True)
        view.selectorFecha.setStyleSheet('font: 25 9pt "Yu Gothic UI Light";')
        view.selectorFecha.setFixedHeight(40)
        view.selectorFecha.setFixedWidth(140)
        view.selectorFecha.setDate(QDate.currentDate())
        view.selectorFecha.setMaximumDate(QDate.currentDate())
        view.layoutFecha = QVBoxLayout(view.frameFecha)
        view.layoutFecha.addWidget(view.selectorFecha)
        view.frameFecha.setLayout(view.layoutFecha)
        view.selectorFecha.dateTimeChanged.connect(
            lambda dateTimeChanged, fecha=None: view.refreshFecha(
                view.selectorFecha.dateTime().toString('yyyyMMdd 999999999999')))

        # Esconde los submenús de Actualización hasta que se necesiten
        view.frameRefreshModes.hide()

        # Conexión con la BD y creación de un cursor de consultas
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()

        # Almacenamiento del tema seleccionado
        view.theme = 'Light'

        # Captura del Nombre Usuario a través de la vista parent (MainView - LoginView)
        usuario = parent.textFieldUser.text()

        # Captura del ID de usuario actual a través de BD
        view.id_usuario = db.execute("SELECT id FROM users WHERE nombre = ?", [usuario]).fetchone()

        # Captura del monedero
        view.monedero = db.execute("SELECT monedero FROM users WHERE nombre = ?", [usuario]).fetchone()[0]
        view.labelMonederoTotal.setText(str(view.monedero) + '€')

        # Captura de la Cartera Actual (la primera de todas las del Usuario)
        view.currentCartera = db.execute(
            "SELECT nombre_cartera FROM carteras WHERE id_usuario = ? ORDER BY (nombre_cartera)",
            ([view.id_usuario[0]])).fetchone()

        # Captura de la Cartera Actual (la primera de todas las del Usuario)
        view.currentCarteraReal = db.execute(
            "SELECT nombre_cartera FROM carteras_real WHERE id_usuario = ? ORDER BY (nombre_cartera)",
            ([view.id_usuario[0]])).fetchone()
        if view.currentCarteraReal is not None:
            view.currentCarteraReal = view.currentCarteraReal[0]

        # Estructura de almacenamiento para los fondos seleccionados para graficar
        view.isins_selected = []
        view.allChecked = False
        view.isin_list = []
        view.ISINS = []

        # Conexión de los eventos de botones clickados a la lógica de los controladores
        view.buttonLogout.clicked.connect(view.logout)
        view.buttonAddISIN.clicked.connect(view.showAddIsin)
        view.buttonAddCarteras.clicked.connect(view.showAddCarteras)
        view.buttonBorrarCartera.clicked.connect(view.borrarCartera)
        view.buttonAddISINReal.clicked.connect(view.showAddIsinReal)
        view.buttonAddCarteraReal.clicked.connect(view.showAddCarterasReales)
        view.buttonBorrarCarteraReal.clicked.connect(view.borrarCarteraReal)
        view.buttonRefreshFake.clicked.connect(view.showRefreshModes)
        view.buttonBorrarFondo.clicked.connect(view.borrarFondo)
        view.listIsins.itemPressed.connect(view.addIsinsChecked)
        view.buttonCheckAll.clicked.connect(view.checkAll)
        view.buttonConfig.clicked.connect(view.showConfigView)
        view.buttonOpBasica.clicked.connect(view.showCompraventas)
        view.buttonOpBasicaVenta.clicked.connect(view.showVentas)
        view.buttonOpTraspaso.clicked.connect(view.showTraspasos)
        view.buttonCartReal.clicked.connect(view.showVistaReal)
        view.buttonCartVirt.clicked.connect(view.showVistaVirtual)
        view.buttonSaveOperaciones.clicked.connect(view.saveOperaciones)

        view.buttonCartReal.setAutoExclusive(True)
        view.buttonCartVirt.setAutoExclusive(True)
        view.frameVirt.hide()

        # Gráfico de carteras virtuales
        view.H = Highstock()

        # Desactivación de los botones de borrar Cartera y Añadir Nuevo Fondo (Cartera Virtual)
        view.buttonBorrarCartera.setEnabled(False)
        view.buttonAddISIN.setEnabled(False)

        # Desactivación de los botones de borrar Cartera y Añadir Nuevo Fondo (Cartera Real)
        view.buttonBorrarCarteraReal.setEnabled(False)
        view.buttonAddISINReal.setEnabled(False)

        # Instancia del Widget WebEngine para la creación de Gráficos
        view.browser = QtWebEngineWidgets.QWebEngineView(view)
        view.browserPie = QtWebEngineWidgets.QWebEngineView(view)

        # Carga del Combobox de selección de modo de graficación
        view.cbModo.addItems(['Absoluto', 'Evolución'])

        # Carga de la etiqueta con el Nombre de usuario actual
        view.labelUsuario.setText(usuario)
        view.labelUsuarioReal.setText(usuario)

        # Carga de la etiqueta con el e-mail de usuario actual
        email = db.execute("SELECT email FROM users WHERE nombre = ?", [usuario]).fetchone()
        view.labelEmail.setText(email[0])
        view.labelEmailReal.setText(email[0])

        # Carga de todas las Carteras Virtuales de las que dispone el Usuario
        view.carteras_usuario = db.execute(
            "SELECT num_cartera , nombre_cartera FROM carteras WHERE id_usuario = ? ORDER BY (nombre_cartera)",
            ([view.id_usuario[0]])).fetchall()

        # Carga de todas las Carteras Reales de las que dispone el Usuario
        view.carteras_usuario_real = db.execute(
            "SELECT num_cartera , nombre_cartera FROM carteras_real WHERE id_usuario = ? ORDER BY (nombre_cartera)",
            ([view.id_usuario[0]])).fetchall()

        # Nombres de cada cartera
        view.nombres_carteras = []
        for e in view.carteras_usuario:
            view.nombres_carteras.append(e[1])

        # Nombres de cada cartera real
        view.nombres_carteras_real = []
        for e in view.carteras_usuario_real:
            view.nombres_carteras_real.append(e[1])

        if len(view.nombres_carteras_real) > 0:
            view.labelCarteraActual.setText(view.nombres_carteras_real[0])
            view.UpdateTableOperaciones(nombre_cartera=view.nombres_carteras_real[0])

        if len(view.nombres_carteras) > 0:
            view.labelCartera.setText('Fondos en ' + view.nombres_carteras[0])
        else:
            view.labelCartera.setText('No existen Carteras')

        # Adición de las Carteras al ComboBox de Selección de Carteras
        view.cbCarteras.addItems(view.nombres_carteras)

        # Creación de los botones del submenú. Un nuevo botón por cada Cartera Real existente
        for nombre in view.nombres_carteras_real:
            # Generación del Botón
            view.button = QPushButton(nombre, view)

            # Enlace a los controladores de pulsación sobre cada botón
            view.button.clicked.connect(
                lambda clicked, nombre_cartera=view.button.text(): view.updatePieChart(nombre_cartera))
            view.button.clicked.connect(
                lambda clicked, nombre_cartera=view.button.text(): view.refreshLabelCartera(nombre_cartera))
            view.button.clicked.connect(
                lambda clicked, nombre_cartera=view.button.text(): view.UpdateTableOperaciones(nombre_cartera))
            view.layoutButtonsCarteras.addWidget(view.button)

            view.button.clicked.connect(
                lambda clicked, nombre_cartera=view.button.text(): view.refreshIsinsEnCartera(nombre_cartera))

            view.button.clicked.connect(
                lambda clicked, v=view: view.refreshButtons())


        view.frameButtonsCarteras.setLayout(view.layoutButtonsCarteras)
        view.frameRefreshModes.setLayout(view.layoutRefreshModes)

        # Activación del botón añadir Fondo si hay alguna cartera
        if view.cbCarteras.count() > 0:
            view.buttonAddISIN.setEnabled(True)

        # Activación del botón añadir Fondo Real si hay alguno
        if len(view.nombres_carteras_real) > 0:
            view.buttonAddISINReal.setEnabled(True)

        # Si hay una cartera actual (si existen carteras) para el usuario actual
        if view.currentCartera is not None and view.currentCarteraReal is not None:

            # Carga todos los ISIN/Symbol de los fondos para la cartera actual (Virtual)
            view.ISINS = db.execute(
                "SELECT cu.ISIN FROM carteras c INNER JOIN carteras_usuario cu "
                "USING (nombre_cartera)"
                "WHERE c.nombre_cartera = ? AND cu.id_usuario = ? ",
                ([view.currentCartera[0], view.id_usuario[0]])).fetchall()

            # Carga todos los ISIN/Symbol de los fondos para la cartera actual (Real)
            view.ISINS_real = db.execute(
                "SELECT cu.ISIN FROM carteras_real c INNER JOIN carteras_usuario_real cu "
                "USING (nombre_cartera)"
                "WHERE c.nombre_cartera = ? AND cu.id_usuario = ? ",
                ([view.currentCartera[0], view.id_usuario[0]])).fetchall()

            for ISIN in view.ISINS:
                view.isin_list.append(ISIN[0])

            # Carga los nombres de los fondos en cartera añadiendo su ISIN/Symbol al final
            isin_list_view = []
            for ISIN in view.ISINS:
                isin_list_view.append(str(fundUtils.ISINtoFundOffline(ISIN[0])) + "  (" + ISIN[0] + ")")

            # Carga el Widget de Selección de Fondos para graficar con los nombres de los Fondos en cartera
            for x in isin_list_view:
                item = QListWidgetItem(str(x))
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable | ~QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Unchecked)
                view.listIsins.addItem(item)

            # Comprueba si existe el Fondo en BD y lo descarga en caso negativo
            for e in view.isin_list:
                fundUtils.saveHistoricalFund(view, e)

            # Actualiza el gráfico con los Fondos seleccionados
            fundUtils.graphHistoricalISIN(view, view.isins_selected, False)

            # Actualiza las Tablas de Fondos
            if len(view.nombres_carteras_real) > 0:
                view.UpdateTableOperaciones(view.nombres_carteras_real[0])



        # Activa el botón de borrar Carteras si hay alguna Cartera
        if len(view.nombres_carteras) > 0:
            view.buttonBorrarCartera.setEnabled(True)

        # Activa el botón de borrar Carteras si hay alguna Cartera
        if len(view.nombres_carteras_real) > 0:
            view.buttonBorrarCarteraReal.setEnabled(True)

        # Conexión de las señales de eventos en los selectores de Selección de Cartera y Modo de Graficación
        view.cbCarteras.currentIndexChanged.connect(view.updateQList)
        view.cbModo.currentIndexChanged.connect(
            lambda clicked, isins_selected=view.isins_selected: view.updateGraph(None, view.isins_selected))
        view.buttonRefresh.clicked.connect(
            lambda clicked, view=view: fundUtils.refreshHistorics(view))

        if len(view.ISINS) != 0:
            view.checkAll()

        # Actualiza el gráfico y las etiquetas de cartera
        view.updateGraph(None, view.isins_selected)
        view.refreshIsinsEnCartera()

        # Instancia del Widget WebEngine para la creación de Gráficos
        view.Pie = Highchart(width=700, height=640)

        # Propiedades del Gráfico
        options = {
            'chart': {
                'plotBackgroundColor': '#979797',
                'backgroundColor': '#979797',
                'plotBorderWidth': None,
                'plotShadow': False
            },
            'title': {
                'text': str(view.currentCarteraReal)
            },
            'tooltip': {
                'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
        }
        view.Pie.set_dict_options(options)

        # Si hay al menos una cartera real en la cuenta de usuario...
        if not view.currentCarteraReal == None:
            # Captura de DB del estado actual de la cartera actual
            data = db.execute("select ISIN , Porcentaje "
                              "from ( select t.*, row_number() over(partition by ISIN "
                              "order by Fecha desc) rn "
                              "from [" + str(view.id_usuario[0]) + "_" +
                              str(view.currentCarteraReal) + "] t) t "
                                                             "where rn = 1 order by ISIN", ([])).fetchall()

            dataList = list()

            for i in range(0, len(data), 1):
                dataList.insert(i, [fundUtils.ISINtoFundOffline(data[i][0]), data[i][1]])

            # Añade los datos de cartera al gráfico
            view.Pie.add_data_set(dataList, 'pie', 'Peso en Cartera', allowPointSelect=True,
                                  cursor='pointer',
                                  showInLegend=True,
                                  dataLabels={
                                      'enabled': False,
                                      'format': '<b>{point.name}</b>: {point.percentage:.1f} %',
                                      'style': {
                                          'color': "(Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'"
                                      }
                                  }
                                  )

            view.updatePieChart(view.nombres_carteras_real[0])
        else:
            view.updatePieChart()


        # Actualiza el estado de los botones y las etiquetas

        view.refreshButtons()
        view.refreshRendimientoTotal()
        view.labelValorTotal.setText("{:.2f}".format(view.importeTotalCartera(None)) + '€')
        view.browserPie.setHtml(view.Pie.htmlcontent)
        view.layoutPieChart.addWidget(view.browserPie)
        fundUtils.refreshHistoricsNoConfirm(view)
        view.refreshIsinsEnCartera()
        view.browserPie.show()



    def saveOperaciones(self):

        if confirmSaveDialog(self).exec():
            completado = True
            columna = self.tableOperaciones.currentColumn()
            fila  = self.tableOperaciones.currentRow()

            # Conexión a base de Datos
            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()

            if columna == 2:
                sql = 'UPDATE operaciones SET Estado = ? WHERE id_usuario == ? AND ID == ? '
                db.execute(sql,[self.tableOperaciones.item(fila,columna).text() ,
                                self.id_usuario[0],
                                self.tableOperaciones.item(fila,0).text()])

            if columna == 3:
                sql = 'UPDATE operaciones SET Titular = ? WHERE id_usuario == ? AND ID == ? '
                db.execute(sql, [self.tableOperaciones.item(fila, columna).text(),
                                 self.id_usuario[0],
                                 self.tableOperaciones.item(fila, 0).text()])
                db.execute('UPDATE operaciones SET Estado = ? WHERE id_usuario == ? AND ID == ? ',
                           ['EJECUTADA',
                            self.id_usuario[0],
                            self.tableOperaciones.item(fila, 0).text()])
            if columna == 4:
                sql = 'UPDATE operaciones SET Incidencias = ? WHERE id_usuario == ? AND ID == ? '
                db.execute(sql, [self.tableOperaciones.item(fila, columna).text(),
                                 self.id_usuario[0],
                                 self.tableOperaciones.item(fila, 0).text()])
                db.execute('UPDATE operaciones SET Estado = ? WHERE id_usuario == ? AND ID == ? ',
                           ['EJECUTADA',
                            self.id_usuario[0],
                            self.tableOperaciones.item(fila, 0).text()])
            if columna == 5:
                sql = 'UPDATE operaciones SET Origen = ? WHERE id_usuario == ? AND ID == ? '
                db.execute(sql, [self.tableOperaciones.item(fila, columna).text(),
                                 self.id_usuario[0],
                                 self.tableOperaciones.item(fila, 0).text()])
                db.execute('UPDATE operaciones SET Estado = ? WHERE id_usuario == ? AND ID == ? ',
                           ['EJECUTADA',
                            self.id_usuario[0],
                            self.tableOperaciones.item(fila, 0).text()])
            if columna == 6:
                sql = 'UPDATE operaciones SET Destino = ? WHERE id_usuario == ? AND ID == ? '
                db.execute(sql, [self.tableOperaciones.item(fila, columna).text(),
                                 self.id_usuario[0],
                                 self.tableOperaciones.item(fila, 0).text()])
                db.execute('UPDATE operaciones SET Estado = ? WHERE id_usuario == ? AND ID == ? ',
                           ['EJECUTADA',
                            self.id_usuario[0],
                            self.tableOperaciones.item(fila, 0).text()])
            if columna == 7:
                sql = 'UPDATE operaciones SET Participaciones = ? WHERE id_usuario == ? AND ID == ? '
                db.execute(sql, [self.tableOperaciones.item(fila, columna).text(),
                                 self.id_usuario[0],
                                 self.tableOperaciones.item(fila, 0).text()])
                completado = self.refreshDesfaseOperacion(
                    ID=self.tableOperaciones.item(fila, 0).text(),
                    tipo='Participaciones',
                    fecha=self.tableOperaciones.item(fila, 1).text(),
                    D=self.tableOperaciones.item(fila, 9).text(),
                    fondo=self.tableOperaciones.item(fila, 6).text())

                db.execute('UPDATE operaciones SET Estado = ? WHERE id_usuario == ? AND ID == ? ',
                           ['EJECUTADA',
                            self.id_usuario[0],
                            self.tableOperaciones.item(fila, 0).text()])


            if columna == 8:
                sql = 'UPDATE operaciones SET Importe = ? WHERE id_usuario == ? AND ID == ? '
                db.execute(sql, [self.tableOperaciones.item(fila, columna).text(),
                                 self.id_usuario[0],
                                 self.tableOperaciones.item(fila, 0).text()])

                db.execute('UPDATE operaciones SET Estado = ? WHERE id_usuario == ? AND ID == ? ',
                           ['EJECUTADA',
                            self.id_usuario[0],
                            self.tableOperaciones.item(fila, 0).text()])

            if columna == 9:

                if self.tableOperaciones.item(fila, 5).text() == 'Monedero':
                    completado = self.refreshDesfaseOperacion(
                                            ID = self.tableOperaciones.item(fila, 0).text(),
                                            tipo='Compra',
                                            fecha=self.tableOperaciones.item(fila, 1).text(),
                                            D=self.tableOperaciones.item(fila, 9).text(),
                                            fondo=self.tableOperaciones.item(fila, 6).text())

                if self.tableOperaciones.item(fila, 6).text() == 'Monedero':
                    completado = self.refreshDesfaseOperacion(
                                            ID=self.tableOperaciones.item(fila, 0).text(),
                                            tipo='Venta',
                                            fecha=self.tableOperaciones.item(fila, 1).text(),
                                            D=self.tableOperaciones.item(fila, 9).text(),
                                            fondo=self.tableOperaciones.item(fila, 5).text())
                if completado:
                    sql = 'UPDATE operaciones SET valorOrigen = ? WHERE id_usuario == ? AND ID == ? '
                    db.execute(sql, [self.tableOperaciones.item(fila, columna).text(),
                                     self.id_usuario[0],
                                     self.tableOperaciones.item(fila, 0).text()])
                    db.execute('UPDATE operaciones SET Estado = ? WHERE id_usuario == ? AND ID == ? ',
                               ['EJECUTADA',
                                self.id_usuario[0],
                                self.tableOperaciones.item(fila, 0).text()])
            if columna == 10:
                sql = 'UPDATE operaciones SET valorDestino = ? WHERE id_usuario == ? AND ID == ? '
                db.execute(sql, [self.tableOperaciones.item(fila, columna).text(),
                                 self.id_usuario[0],
                                 self.tableOperaciones.item(fila, 0).text()])

                completado = self.refreshDesfaseOperacion(
                        ID=self.tableOperaciones.item(fila, 0).text(),
                        tipo='Traspaso',
                        fecha=self.tableOperaciones.item(fila, 1).text(),
                        D=self.tableOperaciones.item(fila, 10).text(),
                        fondo=self.tableOperaciones.item(fila, 6).text())

                if completado:
                    db.execute('UPDATE operaciones SET Estado = ? WHERE id_usuario == ? AND ID == ? ',
                               ['EJECUTADA',
                                self.id_usuario[0],
                                self.tableOperaciones.item(fila, 0).text()])


            else:
                pass

            if completado:
                operationCompleteDialog(self).exec()
                self.UpdateTableOperaciones(self.currentCarteraReal)

        else:
            print('Cancelada operación guardado operaciones')
            pass


    def refreshDesfaseOperacion(self , ID , tipo , fecha, D, fondo):

            print('refreshDesfaseOperacion()' + str(fecha))
            completado = True
            dateFecha = datetime.datetime.strptime(str(fecha), '%d/%m/%Y')

            # Conexión con la BD y creación de un cursor de consultas
            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()

            #Buscar y calcular el valor de fondo a fecha
            closeFecha = db.execute('SELECT Close FROM [' + fondo + '] WHERE Date <= ? ORDER BY Date Desc LIMIT 1', [dateFecha]).fetchone()[0]


            #Buscar y calcular el valor de fondo a fecha +/- D
            D = D[1:]
            if len(D) > 1:
                D = int(D)
            else:
                D=0

            dateFecha = dateFecha + datetime.timedelta(days=D)
            closeFechaDesf = db.execute('SELECT Close FROM [' + fondo + '] WHERE Date >= ? LIMIT 1', [dateFecha]).fetchone()

            if closeFechaDesf is not None:
                closeFechaDesf = closeFechaDesf[0]
            else:
                closeFechaDesf = closeFecha
                avisoOperacionDialog(self).exec()
                completado = False

            # Calcular la diferencia y añadírselo/restárselo al monedero de usuario
            dif = closeFecha-closeFechaDesf
            if tipo == 'Compra':
                monedero = db.execute('SELECT monedero FROM users WHERE id == ?' , [self.id_usuario[0]]).fetchone()

                p = db.execute('SELECT Participaciones FROM operaciones WHERE id_usuario == ? AND ID == ? ' ,
                               [self.id_usuario[0] , ID]).fetchone()[0]

                db.execute('UPDATE operaciones SET Importe = ? WHERE id_usuario == ? AND ID == ? ' ,
                           [(p*closeFechaDesf) , self.id_usuario[0] , ID])

                db.execute('UPDATE users SET monedero = ? WHERE id == ? ' , [(monedero[0] + dif*p) , self.id_usuario[0]])
                self.monedero = monedero[0] + dif*p
                self.refreshLabelCartera(self.currentCarteraReal)

            if tipo == 'Venta':
                monedero = db.execute('SELECT monedero FROM users WHERE id == ?', [self.id_usuario[0]]).fetchone()


                p = db.execute('SELECT Participaciones FROM operaciones WHERE id_usuario == ? AND ID == ? ' ,
                               [self.id_usuario[0], ID]).fetchone()[0]

                db.execute('UPDATE operaciones SET Importe = ? WHERE id_usuario == ? AND ID == ? ',
                           [(p * closeFechaDesf), self.id_usuario[0], ID])

                db.execute('UPDATE users SET monedero = ? WHERE id == ? ' , [(monedero[0] - dif*p), self.id_usuario[0]])
                self.monedero = monedero[0] - dif*p
                self.refreshLabelCartera(self.currentCarteraReal)

            if tipo == 'Traspaso':


                p = db.execute('SELECT Participaciones FROM operaciones WHERE id_usuario == ? AND ID == ? ' ,
                               [self.id_usuario[0], ID]).fetchone()[0]

                db.execute('UPDATE operaciones SET Importe = ? WHERE id_usuario == ? AND ID == ? ',
                           [(p * closeFechaDesf), self.id_usuario[0], ID])

            if tipo == 'Participaciones':


                p = db.execute('SELECT Participaciones FROM operaciones WHERE id_usuario == ? AND ID == ? ' ,
                               [self.id_usuario[0], ID]).fetchone()[0]

                db.execute('UPDATE operaciones SET Importe = ? WHERE id_usuario == ? AND ID == ? ',
                           [(p * closeFechaDesf), self.id_usuario[0], ID])


            return completado



    def refreshRendimientoTotal(self, fechaIni=None, fechaFin=None):

        if self.currentCarteraReal is None:
            self.labelRendimientoTotal.setText('')

        else:
            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()

            if not fechaIni:
                # Fecha Inicial -> Creacion de cartera
                strFechaIni = \
                    db.execute('SELECT fecha_creacion FROM carteras_real WHERE id_usuario = ? AND nombre_cartera = ?',
                               ([self.id_usuario[0], self.currentCarteraReal])).fetchone()[0]
                dateIni = datetime.datetime.strptime(strFechaIni, "%d/%m/%Y").date()
                fechaIni = dateIni.strftime('%Y%m%d 999999999999')

            if not fechaFin:
                # Fecha Final -> Ho
                fechaFin = datetime.datetime.today().strftime('%Y%m%d 999999999999')

            importeIni = self.importeTotalCartera(fechaIni)
            importeFin = self.importeTotalCartera(fechaFin)
            if importeIni == 0:
                rend = 'Incalculable'
                self.labelRendimientoTotal.setText(rend)

            else:
                ratio = importeFin / importeIni
                rend = (ratio - 1) * 100
                if len(str(rend)) > 10:
                    self.labelRendimientoTotal.setText("{:.2f}".format(rend) + ' %')
                else:
                    self.labelRendimientoTotal.setText("{:.2f}".format(rend) + ' %')

            if rend == 'Incalculable':
                self.labelRendimientoTotal.setStyleSheet('color: rgb(255, 255, 255);')
            if rend != 'Incalculable' and rend >= 0:
                self.labelRendimientoTotal.setStyleSheet('color: rgb(0, 255, 0);')
            if rend != 'Incalculable' and rend < 0:
                self.labelRendimientoTotal.setStyleSheet('color: rgb(255, 0, 0);')


    def refreshFecha(self, fecha):
        print('refreshFecha() ' + str(fecha))

        # Capturar de tabla de estados de cartera todos aquellos que sean anteriores a fecha
        # para quedarnos con el último
        # Refrescar el PieChart con el nuevo Data de la fecha seleccionada
        self.updatePieChart(self.currentCarteraReal, fecha)

        # Refrescar label de Importe Total
        self.labelValorTotal.setText("{:.2f}".format(self.importeTotalCartera(fecha)) + ' €')

        # Refrescar rendimiento total
        self.refreshRendimientoTotal(fechaIni=None, fechaFin=fecha)
    '''
    - Muestra y oculta los botones del submenú 
    de actualización de históricos
    
    @params: None
    '''

    def showRefreshModes(self):
        if self.buttonRefreshFake.isChecked():
            self.frameRefreshModes.show()
        else:
            self.frameRefreshModes.hide()

    '''
        - Activa/desactiva los botones de operaciones 
        de cartera en caso de que haya alguna cartera o no

        @params: None
    '''

    def refreshButtons(self):
        if self.currentCarteraReal is None:
            self.buttonAddISINReal.setEnabled(False)
            self.buttonOpBasica.setEnabled(False)
            self.buttonOpBasicaVenta.setEnabled(False)
            self.buttonOpTraspaso.setEnabled(False)
            self.buttonBorrarCarteraReal.setEnabled(False)
            self.labelSinCarteras.show()
            self.labelSinCarteras2.show()

        else:
            self.buttonAddISINReal.setEnabled(True)
            self.buttonOpBasica.setEnabled(True)
            self.buttonOpTraspaso.setEnabled(True)
            self.buttonOpBasicaVenta.setEnabled(True)
            self.buttonBorrarCarteraReal.setEnabled(True)
            self.labelSinCarteras.hide()
            self.labelSinCarteras2.hide()


    def refreshIsinsEnCartera(self , cart=None):

        print('RefreshIsinsEnCartera()')
        # Conexión con la BD y creación de un cursor de consultas
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()

        if cart:
            sql = (
                'SELECT ca.Nombre , ca.ISIN , f.Participaciones , f.Importe '
                'FROM carteras_usuario_real cr INNER JOIN caracterizacion ca USING(ISIN) LEFT JOIN '
                '(SELECT * from ( select t.*, row_number() over(partition by ISIN order by Fecha desc) rn '
                'from [' + str(self.id_usuario[0]) + "_" + str(cart) + '] t) t where rn = 1 order by ISIN) '
                'f USING(ISIN) WHERE cr.id_usuario == ? AND cr.nombre_cartera == ? '
                 )
            try:
                funds = db.execute(sql, [self.id_usuario[0], str(cart)]).fetchall()
                self.tableFondosCartera.clear()
                self.tableFondosCartera.setHorizontalHeaderItem(0, QTableWidgetItem('Fondo'))
                self.tableFondosCartera.setHorizontalHeaderItem(1, QTableWidgetItem('ISIN'))
                self.tableFondosCartera.setHorizontalHeaderItem(2, QTableWidgetItem('Partic.'))
                self.tableFondosCartera.setHorizontalHeaderItem(3, QTableWidgetItem('Importe'))
                self.tableFondosCartera.setColumnWidth(0, 200)
                self.tableFondosCartera.setColumnWidth(1, 140)
                self.tableFondosCartera.setColumnWidth(2, 60)
                self.tableFondosCartera.setColumnWidth(3, 100)
                self.tableFondosCartera.setEditTriggers(QAbstractItemView.NoEditTriggers)

                self.tableFondosCartera.setRowCount(len(funds))

                f = 0

                filas = db.execute(sql, ([self.id_usuario[0] , str(cart)]))

                for fila in filas:
                    self.tableFondosCartera.setItem(f, 0, QTableWidgetItem(str(fila[0])))
                    self.tableFondosCartera.setItem(f, 1, QTableWidgetItem(str(fila[1])))
                    self.tableFondosCartera.setItem(f, 2, QTableWidgetItem(str(fila[2])))
                    self.tableFondosCartera.setItem(f, 3, QTableWidgetItem(str(fila[3])))

                    f += 1

            except sqlite3.OperationalError:
                self.tableFondosCartera.clear()
                self.tableFondosCartera.setHorizontalHeaderItem(0, QTableWidgetItem('Fondo'))
                self.tableFondosCartera.setHorizontalHeaderItem(1, QTableWidgetItem('ISIN'))
                self.tableFondosCartera.setHorizontalHeaderItem(2, QTableWidgetItem('Partic.'))
                self.tableFondosCartera.setHorizontalHeaderItem(3, QTableWidgetItem('Importe'))
                self.tableFondosCartera.setColumnWidth(0, 200)
                self.tableFondosCartera.setColumnWidth(1, 140)
                self.tableFondosCartera.setColumnWidth(2, 60)
                self.tableFondosCartera.setColumnWidth(3, 100)

            db.close()

        else :
            sql = (
                    'SELECT ca.Nombre , ca.ISIN , f.Participaciones , f.Importe '
                    'FROM carteras_usuario_real cr INNER JOIN caracterizacion ca USING(ISIN) LEFT JOIN '
                    '(SELECT * from ( select t.*, row_number() over(partition by ISIN order by Fecha desc) rn '
                    'from [' + str(self.id_usuario[0]) + "_" + str(self.currentCarteraReal) + '] t) t where rn = 1 order by ISIN) '
                     'f USING(ISIN) WHERE cr.id_usuario == ? AND cr.nombre_cartera == ? '
            )
            try:
                funds = db.execute(sql, [self.id_usuario[0], self.currentCarteraReal ]).fetchall()
                self.tableFondosCartera.clear()
                self.tableFondosCartera.setHorizontalHeaderItem(0, QTableWidgetItem('Fondo'))
                self.tableFondosCartera.setHorizontalHeaderItem(1, QTableWidgetItem('ISIN'))
                self.tableFondosCartera.setHorizontalHeaderItem(2, QTableWidgetItem('Partic.'))
                self.tableFondosCartera.setHorizontalHeaderItem(3, QTableWidgetItem('Importe'))
                self.tableFondosCartera.setColumnWidth(0, 200)
                self.tableFondosCartera.setColumnWidth(1, 140)
                self.tableFondosCartera.setColumnWidth(2, 60)
                self.tableFondosCartera.setColumnWidth(3, 100)
                self.tableFondosCartera.setEditTriggers(QAbstractItemView.NoEditTriggers)

                self.tableFondosCartera.setRowCount(len(funds))

                f = 0

                filas = db.execute(sql, ([self.id_usuario[0] , self.currentCarteraReal]))

                for fila in filas:
                    self.tableFondosCartera.setItem(f, 0, QTableWidgetItem(str(fila[0])))
                    self.tableFondosCartera.setItem(f, 1, QTableWidgetItem(str(fila[1])))
                    self.tableFondosCartera.setItem(f, 2, QTableWidgetItem(str(fila[2])))
                    self.tableFondosCartera.setItem(f, 3, QTableWidgetItem(str(fila[3])))

                    f += 1

            except sqlite3.OperationalError:
                self.tableFondosCartera.clear()
                self.tableFondosCartera.setHorizontalHeaderItem(0, QTableWidgetItem('Fondo'))
                self.tableFondosCartera.setHorizontalHeaderItem(1, QTableWidgetItem('ISIN'))
                self.tableFondosCartera.setHorizontalHeaderItem(2, QTableWidgetItem('Partic.'))
                self.tableFondosCartera.setHorizontalHeaderItem(3, QTableWidgetItem('Importe'))
                self.tableFondosCartera.setColumnWidth(0, 200)
                self.tableFondosCartera.setColumnWidth(1, 140)
                self.tableFondosCartera.setColumnWidth(2, 60)
                self.tableFondosCartera.setColumnWidth(3, 100)

            db.close()


    '''
        - Actualiza el label indicador de Cartera Actual en la Vista (Real)
    '''

    def refreshLabelCartera(self, cart=None):
        if cart:
            self.selectorFecha.setDate(datetime.datetime.today())
            self.labelCarteraActual.setText(cart)
            self.labelValorTotal.setText("{:.2f}".format(self.importeTotalCartera(None)) + '€')
            self.labelMonederoTotal.setText(str(self.monedero) + '€')
            self.refreshRendimientoTotal()
        else:
            self.selectorFecha.setDate(datetime.datetime.today())
            self.labelCarteraActual.setText('Ninguna')
            self.labelValorTotal.setText('0 €')
            self.labelMonederoTotal.setText(str(self.monedero) + '€')
            self.labelRendimientoTotal.setText('')
    '''
        - Borra el fondo seleccionado del ComboBox de la vista
        y elimina el registro de usuario para la cartera actual. 
        
        @params: view (UserView) 
        @returns: None
    '''

    def borrarFondo(view):

        try:
            name = view.listIsins.item(view.listIsins.currentRow()).text()

            dlg = confirmDeleteFundDialog(view)
            if dlg.exec():

                db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
                db = db_connection.cursor()
                index = view.cbCarteras.currentIndex()
                cartera = str(view.cbCarteras.itemText(index))

                ISIN = name[name.rfind("(") + 1: name.rfind(")")]
                db.execute("DELETE FROM carteras_usuario WHERE id_usuario = ? AND nombre_cartera = ? AND ISIN = ?",
                           ([view.id_usuario[0], cartera, ISIN]))

                temp = db.execute("SELECT * FROM carteras_usuario WHERE ISIN = ? ",
                                  ([ISIN])).fetchone()
                if temp is None:
                    db.execute("DROP TABLE " + ISIN)

                view.listIsins.takeItem(view.listIsins.currentRow())
                if ISIN in view.isins_selected:
                    view.isins_selected.remove(ISIN)
                view.updateGraph(isin=None, isins_selected=[])

            else:
                print('Cancelada la operación de borrar Fondo')
                pass

        except:
            dlg = selectAnyDialog(view)
            dlg.exec()

    '''
        - Borra la cartera seleccionada del ComboBox de la vista
        y elimina el registro de usuario para la cartera actual.

        @params: view (UserView)
        @returns: None
    '''

    def borrarCartera(view):

        if confirmDeleteCarteraDialog(view).exec():

            index = view.cbCarteras.currentIndex()

            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()
            cartera = str(view.cbCarteras.itemText(index))

            db.execute("DELETE FROM carteras WHERE id_usuario = ? AND nombre_cartera = ?",
                       ([view.id_usuario[0], cartera]))
            db.execute("DELETE FROM carteras_usuario WHERE id_usuario = ? AND nombre_cartera = ?",
                       ([view.id_usuario[0], cartera]))

            view.cbCarteras.removeItem(view.cbCarteras.currentIndex())

            if view.cbCarteras.count() > 0:
                view.buttonBorrarCartera.setEnabled(True)
            else:
                view.buttonBorrarCartera.setEnabled(False)

        else:
            print('Cancelada la operación de borrado de cartera')
            pass

    '''
        - Actualiza la lista de selector con los fondos de la cartera actual

         @params: view (UserView)
         @returns: None
    '''

    def updateQList(view):

        try:
            view.listIsins.clear()
            view.isins_selected = []
            view.labelCartera.setText('Fondos en ' + view.cbCarteras.currentText())
            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()
            ISINS = db.execute(
                "SELECT cu.ISIN FROM carteras c INNER JOIN carteras_usuario cu "
                "USING (nombre_cartera)"
                "WHERE c.nombre_cartera = ? AND cu.id_usuario = ?   ",
                ([str(view.cbCarteras.currentText()), view.id_usuario[0]])).fetchall()

            isin_list = []
            for ISIN in ISINS:
                isin_list.append(ISIN[0])

            isin_list_view = []
            for ISIN in ISINS:
                isin_list_view.append(str(fundUtils.ISINtoFundOffline(ISIN[0])) + "  (" + ISIN[0] + ")")

            for x in isin_list_view:
                item = QListWidgetItem(str(x))
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Unchecked)
                view.listIsins.addItem(item)

            for e in isin_list:
                fundUtils.saveHistoricalFund(view, e)

            fundUtils.graphHistoricalISIN(view, view.isins_selected, True)

        except:
            # Avisa al Usuario de que el fondo está descargándose
            dlg = downloadingIsinDialog(view)
            dlg.exec()

    '''
        - Añade todos los fondos a la lista de graficación
        y los inserta en el gráfico.

            @params: self (UserView)
            @returns: None
    '''

    def checkAll(view):

        if not view.allChecked:
            for i in range(view.listIsins.count()):
                view.listIsins.item(i).setCheckState(True)

            view.updateGraph(None, view.isin_list)
            view.isins_selected = []
            for e in view.ISINS:
                view.isins_selected.append(e[0])
            view.allChecked = True
            print('All Checked: ' + str(view.isins_selected))
        else:
            for i in range(view.listIsins.count()):
                view.listIsins.item(i).setCheckState(False)

            view.updateGraph(None, isins_selected=[])
            view.isins_selected = []
            view.allChecked = False
            print('All Unchecked: ' + str(view.isins_selected))

    '''
        - Añade el Fondo seleccionado a la lista de graficación
        y lo inserta en el gráfico.

         @params: self (UserView)
         @returns: None
    '''

    def addIsinsChecked(self):
        print("Captada la pulsación")

        # Captura del ISIN del Fondo seleccionado en la vista
        name = self.listIsins.item(self.listIsins.currentRow()).text()
        ISIN = name[name.rfind("(") + 1: name.rfind(")")]
        # Comprueba si ISIN es el ISIN del fondo (si existe en investing.com)
        # lanzando RuntimeError en caso negativo
        fundUtils.ISINtoFundOffline(ISIN)

        # Añade o elimina el fondo seleccionado a la lista de graficación
        if ISIN in self.isins_selected:
            self.isins_selected.remove(ISIN)
            self.listIsins.currentItem().setCheckState(False)
            self.updateGraph(None, self.isins_selected)

        else:
            self.isins_selected.append(ISIN)
            self.listIsins.currentItem().setCheckState(True)
            # Actualiza el gráfico
            self.updateGraph(ISIN, self.isins_selected)

        print('FONDOS EN GRÁFICO: ')
        print(self.isins_selected)

    '''
        - Muestra la Interfaz Gráfica de Configuración
        
         @params: self (UserView)
         @returns: None
    '''

    def showConfigView(self):
        conf = ConfigView(self)
        conf.show()

    ''' 
        - Muestra el apartado de la vista corrrespondiente a las carteras
        reales del usuario
        
        @parent: UserView
        @params: UserView
        @returns: None
    '''

    def showVistaReal(self):
        self.frameVirt.hide()
        self.frameButtonsCarteras.show()
        self.frameReal.show()

    ''' 
        - Muestra el apartado de la vista corrrespondiente a las carteras
        virtuales del usuario

        @parent: UserView
        @params: UserView
        @returns: None
    '''

    def showVistaVirtual(self):
        self.frameReal.hide()
        self.frameButtonsCarteras.hide()
        self.frameVirt.show()

    '''
            - Muestra la Interfaz Gráfica de Ajustes

             @params: self (UserView)
             @returns: None
        '''

    def showAddCarteras(self):
        cart = AddCarterasView(self)
        cart.show()

    '''
        - Muestra la Interfaz para añadir Carteras Reales

        @params: self (UserView)
        @returns: None
    '''

    def showAddCarterasReales(self):
        cart = AddCarterasRealesView(self)
        cart.show()

    ''' 
        - Borra la cartera (real) actual, eliminando su registro de 
        las tablas CARTERAS_REAL y CARTERAS_REAL_USUARIO y elimina de DB
        la tabla de estados de cartera -> [id_NombreCartera]
        
        @params: self (UserView)
        @returns: None
    '''

    def borrarCarteraReal(self):
        # print('Borrar Cartera Real()')
        dlg = confirmDeleteCarteraDialog(self)
        if dlg.exec():

            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()
            db.execute("DELETE FROM carteras_real WHERE id_usuario = ? AND nombre_cartera = ?",
                       ([self.id_usuario[0], self.currentCarteraReal]))
            db.execute("DELETE FROM carteras_usuario_real WHERE id_usuario = ? AND nombre_cartera = ?",
                       ([self.id_usuario[0], self.currentCarteraReal]))

            db.execute("DELETE FROM operaciones WHERE id_usuario = ? AND nombre_cartera = ?",
                       ([self.id_usuario[0], self.currentCarteraReal]))

            db.execute("DROP TABLE [" + str(self.id_usuario[0]) + "_" + self.currentCarteraReal + "]", ([]))
            db.execute("DELETE FROM operaciones WHERE id_usuario = ? AND nombre_cartera = ? ",
                       ([self.id_usuario[0], self.currentCarteraReal]))

            self.carteras_usuario = db.execute(
                "SELECT num_cartera , nombre_cartera FROM carteras_real WHERE id_usuario = ? ORDER BY (nombre_cartera)",
                ([self.id_usuario[0]])).fetchall()

            for i in reversed(range(self.layoutButtonsCarteras.count())):
                if not i == 0:
                    self.layoutButtonsCarteras.itemAt(i).widget().setParent(None)

            for nombre in self.carteras_usuario:
                self.button = QPushButton(nombre[1], self)
                self.button.clicked.connect(
                    lambda clicked, nombre_cartera=self.button.text(): self.updatePieChart(nombre_cartera))
                self.button.clicked.connect(
                    lambda clicked, nombre_cartera=self.button.text(): self.refreshLabelCartera(nombre_cartera))
                self.button.clicked.connect(
                    lambda clicked, nombre_cartera=self.button.text(): self.UpdateTableOperaciones(nombre_cartera))

                self.layoutButtonsCarteras.addWidget(self.button)

                self.button.clicked.connect(
                    lambda clicked, nombre_cartera=self.button.text(): self.refreshIsinsEnCartera(nombre_cartera))

                self.button.clicked.connect(
                    lambda clicked, v=self: self.refreshButtons())


            self.frameButtonsCarteras.setLayout(self.layoutButtonsCarteras)

            if len(self.carteras_usuario) > 0:
                self.currentCarteraReal = self.carteras_usuario[0][1]
                self.updatePieChart(self.currentCarteraReal)
                self.UpdateTableOperaciones(self.currentCarteraReal)
                self.refreshIsinsEnCartera()
            else:
                self.currentCarteraReal = ''
                self.refreshIsinsEnCartera()
                self.refreshLabelCartera()
                self.updatePieChart()
                self.UpdateTableOperaciones()

            self.refreshButtons()
            self.labelValorTotal.setText("{:.2f}".format(self.importeTotalCartera(None)) + '€')


        else:
            print('Cancelada la operación de borrado de cartera real')
            pass

    '''
        - Muestra la Interfaz Gráfica para Añadir Fondos

         @params: self (UserView)
         @returns: None
    '''

    def showAddIsin(self):
        merc = AddISINView(self)
        merc.show()

    '''
        - Muestra la Interfaz Gráfica para Añadir Fondos (reales)

         @params: self (UserView)
         @returns: None
    '''

    def showAddIsinReal(self):
        merc = AddISINViewReal(self)
        merc.show()

    '''
           - Muestra la Interfaz Gráfica de Traspasos (reales)

            @params: self (UserView)
            @returns: None
    '''

    def showTraspasos(self):
        ops = TraspasosView(self)
        ops.show()

    '''
            - Muestra la Interfaz Gráfica de Ventas (reales)

            @params: self (UserView)
            @returns: None
    '''

    def showVentas(self):
        ops = OperacionesVentaView(self)
        ops.show()

    '''
            - Muestra la Interfaz Gráfica de Compras (reales)

            @params: self (UserView)
            @returns: None
    '''

    def showCompraventas(self):

        ops = OperacionesView(self)
        ops.show()

    '''
        - Sale de la ventana actual (UserView) y 
        muestra de nuevo la Interfaz Gráfica de LogIn (MainView)

         @params: self (UserView)
         @returns: None
    '''

    def logout(self):
        dlg = confirmLogoutDialog(self)
        if dlg.exec():
            self.hide()
            self.parent().setWindowState(Qt.WindowActive)
        else:
            print('Cancelada operación de LogOut')
            pass

    '''
        - Actualiza el gráfico del layout en UserView con la lista de 
        fondos seleccionados para graficar

         @params: self (UserView) 
                : lista de fondos seleccionados (isins_list)
         @returns: None
    '''

    def updateGraph(self, isin, isins_selected):

        if self.cbModo.currentIndex() == 0:
            fundUtils.UpdateGraph(self, isin, isins_selected, True)
        else:
            fundUtils.UpdateGraph(self, isin, isins_selected, False)

    '''
        - Actualiza la tabla de Fondos en Cartera Real
        
        @params: self(UserView)
        @returns: None
    '''

    def UpdateTableOperaciones(view, nombre_cartera=None):
        # print('Update Table Operaciones()')
        view.currentCarteraReal = nombre_cartera

        if nombre_cartera:

            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()

            sql = 'SELECT ID , Fecha , Estado , Titular , Incidencias , Origen, Destino, Participaciones , Importe , valorOrigen , valorDestino ' \
                  'FROM operaciones ' \
                  'WHERE id_usuario == ? AND nombre_cartera == ? ORDER BY Fecha Desc '

            try:
                funds = db.execute(sql, ([view.id_usuario[0], nombre_cartera])).fetchall()

                view.tableOperaciones.clear()
                view.tableOperaciones.setHorizontalHeaderItem(0, QTableWidgetItem('#ID'))
                view.tableOperaciones.setHorizontalHeaderItem(1, QTableWidgetItem('Fecha'))
                view.tableOperaciones.setHorizontalHeaderItem(2, QTableWidgetItem('Estado'))
                view.tableOperaciones.setHorizontalHeaderItem(3, QTableWidgetItem('Titular'))
                view.tableOperaciones.setHorizontalHeaderItem(4, QTableWidgetItem('Incidencias'))
                view.tableOperaciones.setHorizontalHeaderItem(5, QTableWidgetItem('Origen'))
                view.tableOperaciones.setHorizontalHeaderItem(6, QTableWidgetItem('Destino'))
                view.tableOperaciones.setHorizontalHeaderItem(7, QTableWidgetItem('Particip.'))
                view.tableOperaciones.setHorizontalHeaderItem(8, QTableWidgetItem('Importe'))
                view.tableOperaciones.setHorizontalHeaderItem(9, QTableWidgetItem('V Orig.'))
                view.tableOperaciones.setHorizontalHeaderItem(10, QTableWidgetItem('V Dest.'))

                view.tableOperaciones.setColumnWidth(0, 0)
                view.tableOperaciones.setColumnWidth(1, 120)
                view.tableOperaciones.setColumnWidth(2, 110)
                view.tableOperaciones.setColumnWidth(3, 150)
                view.tableOperaciones.setColumnWidth(4, 110)
                view.tableOperaciones.setColumnWidth(5, 140)
                view.tableOperaciones.setColumnWidth(6, 140)
                view.tableOperaciones.setColumnWidth(7, 110)
                view.tableOperaciones.setColumnWidth(8, 90)
                view.tableOperaciones.setColumnWidth(9, 90)
                view.tableOperaciones.setColumnWidth(10, 90)


                view.tableOperaciones.setRowCount(len(funds))

                f = 0

                for fila in db.execute(sql, ([view.id_usuario[0], nombre_cartera])):
                    view.tableOperaciones.setItem(f, 0, QTableWidgetItem(str(fila[0])))
                    view.tableOperaciones.setItem(f, 1, QTableWidgetItem(str(fila[1])))
                    view.tableOperaciones.setItem(f, 2, QTableWidgetItem(str(fila[2])))
                    view.tableOperaciones.setItem(f, 3, QTableWidgetItem(str(fila[3])))
                    view.tableOperaciones.setItem(f, 4, QTableWidgetItem(str(fila[4])))
                    view.tableOperaciones.setItem(f, 5, QTableWidgetItem(str(fila[5])))
                    view.tableOperaciones.setItem(f, 6, QTableWidgetItem(str(fila[6])))
                    view.tableOperaciones.setItem(f, 7, QTableWidgetItem(str(fila[7])))
                    view.tableOperaciones.setItem(f, 8, QTableWidgetItem(str(fila[8])))
                    view.tableOperaciones.setItem(f, 9, QTableWidgetItem(str(fila[9])))
                    view.tableOperaciones.setItem(f, 10, QTableWidgetItem(str(fila[10])))


                    f += 1

            except sqlite3.InterfaceError:

                funds = db.execute(sql, ([view.id_usuario[0], view.nombres_carteras_real[0]])).fetchall()

                view.tableOperaciones.clear()
                view.tableOperaciones.setHorizontalHeaderItem(0, QTableWidgetItem('#ID'))
                view.tableOperaciones.setHorizontalHeaderItem(1, QTableWidgetItem('Fecha'))
                view.tableOperaciones.setHorizontalHeaderItem(2, QTableWidgetItem('Estado'))
                view.tableOperaciones.setHorizontalHeaderItem(3, QTableWidgetItem('Titular'))
                view.tableOperaciones.setHorizontalHeaderItem(4, QTableWidgetItem('Incidencias'))
                view.tableOperaciones.setHorizontalHeaderItem(5, QTableWidgetItem('Origen'))
                view.tableOperaciones.setHorizontalHeaderItem(6, QTableWidgetItem('Destino'))
                view.tableOperaciones.setHorizontalHeaderItem(7, QTableWidgetItem('Particip.'))
                view.tableOperaciones.setHorizontalHeaderItem(8, QTableWidgetItem('Importe'))
                view.tableOperaciones.setHorizontalHeaderItem(9, QTableWidgetItem('V Orig.'))
                view.tableOperaciones.setHorizontalHeaderItem(10, QTableWidgetItem('V Dest.'))

                view.tableOperaciones.setColumnWidth(0, 0)
                view.tableOperaciones.setColumnWidth(1, 120)
                view.tableOperaciones.setColumnWidth(2, 110)
                view.tableOperaciones.setColumnWidth(3, 150)
                view.tableOperaciones.setColumnWidth(4, 110)
                view.tableOperaciones.setColumnWidth(5, 140)
                view.tableOperaciones.setColumnWidth(6, 140)
                view.tableOperaciones.setColumnWidth(7, 110)
                view.tableOperaciones.setColumnWidth(8, 90)
                view.tableOperaciones.setColumnWidth(9, 90)
                view.tableOperaciones.setColumnWidth(10, 90)

                f = 0

                for fila in db.execute(sql, ([view.id_usuario[0], view.nombres_carteras_real[0]])):
                    view.tableOperaciones.setItem(f, 0, QTableWidgetItem(str(fila[0])))
                    view.tableOperaciones.setItem(f, 1, QTableWidgetItem(str(fila[1])))
                    view.tableOperaciones.setItem(f, 2, QTableWidgetItem(str(fila[2])))
                    view.tableOperaciones.setItem(f, 3, QTableWidgetItem(str(fila[3])))
                    view.tableOperaciones.setItem(f, 4, QTableWidgetItem(str(fila[4])))
                    view.tableOperaciones.setItem(f, 5, QTableWidgetItem(str(fila[5])))
                    view.tableOperaciones.setItem(f, 6, QTableWidgetItem(str(fila[6])))
                    view.tableOperaciones.setItem(f, 7, QTableWidgetItem(str(fila[7])))
                    view.tableOperaciones.setItem(f, 8, QTableWidgetItem(str(fila[8])))
                    view.tableOperaciones.setItem(f, 9, QTableWidgetItem(str(fila[9])))
                    view.tableOperaciones.setItem(f, 10, QTableWidgetItem(str(fila[10])))

                    f += 1

            db.close()

    '''
        - Actualiza el gráfico (tarta) de Fondos en Cartera Real

        @params: self(UserView)
        @returns: None
    '''

    def updatePieChart(self, nombre_cartera=None, fecha=None):

        if not fecha:
            print('updatePieChart(sin fecha) en Cartera --> ' + str(nombre_cartera))
            self.Pie = Highchart(width=440, height=440)
            self.currentCarteraReal = nombre_cartera
            if self.theme == 'Light':
                options = {
                    'chart': {
                        'plotBackgroundColor': '#979797',
                        'backgroundColor': '#979797',
                        'plotBorderWidth': None,
                        'plotShadow': False
                    },
                    'title': {
                        'text': nombre_cartera
                    },
                    'tooltip': {
                        'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'
                    },
                }
            if self.theme == 'Dark':
                options = {
                    'chart': {
                        'plotBackgroundColor': '#222222',
                        'backgroundColor': '#222222',
                        'plotBorderWidth': None,
                        'plotShadow': False
                    },
                    'title': {
                        'text': nombre_cartera
                    },
                    'tooltip': {
                        'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'
                    },
                }
            self.Pie.set_dict_options(options)

            # Conexión con la BD y creación de un cursor de consultas
            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()

            if nombre_cartera:

                data = db.execute("select ISIN , Porcentaje "
                                  "from ( select t.*, row_number() over(partition by ISIN "
                                  "order by Fecha desc) rn "
                                  "from [" + str(self.id_usuario[0]) + "_" +
                                  str(nombre_cartera) + "] t) t "
                                                        "where rn = 1 order by ISIN", ([])).fetchall()
                dataList = list()

                for i in range(0, len(data), 1):
                    dataList.insert(i, [fundUtils.ISINtoFundOffline(data[i][0]), data[i][1]])

                self.Pie.add_data_set(dataList, 'pie', 'Peso en Cartera', allowPointSelect=True,
                                      cursor='pointer',
                                      showInLegend=True,
                                      dataLabels={
                                          'enabled': False,
                                          'format': '<b>{point.name}</b>: {point.percentage:.1f} %',
                                          'style': {
                                              'color': "('black'"
                                          }
                                      }
                                      )

            else:
                pass

            self.browserPie.setHtml(self.Pie.htmlcontent)
            self.layoutPieChart.addWidget(self.browserPie)
            self.browserPie.show()

        # Hay fecha
        else:
            print('updatePieChart(con fecha)' + str(fecha) + 'en Cartera --> ' + str(nombre_cartera))
            self.Pie = Highchart(width=440, height=440)
            self.currentCarteraReal = nombre_cartera
            if self.theme == 'Light':
                options = {
                    'chart': {
                        'plotBackgroundColor': '#979797',
                        'backgroundColor': '#979797',
                        'plotBorderWidth': None,
                        'plotShadow': False
                    },
                    'title': {
                        'text': nombre_cartera
                    },
                    'tooltip': {
                        'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'
                    },
                }
            if self.theme == 'Dark':
                options = {
                    'chart': {
                        'plotBackgroundColor': '#222222',
                        'backgroundColor': '#222222',
                        'plotBorderWidth': None,
                        'plotShadow': False
                    },
                    'title': {
                        'text': nombre_cartera
                    },
                    'tooltip': {
                        'pointFormat': '{series.name}: <b>{point.percentage:.1f}%</b>'
                    },
                }
            self.Pie.set_dict_options(options)

            # Conexión con la BD y creación de un cursor de consultas
            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()

            if nombre_cartera:

                data = db.execute("select ISIN , Porcentaje "
                                  "from ( select t.*, row_number() over(partition by ISIN "
                                  "order by Fecha desc) rn "
                                  "from "
                                  "(select * from [" + str(self.id_usuario[0]) + "_" +
                                  str(nombre_cartera) + "] where Fecha < ? ) t) t "
                                                        "where rn = 1 order by ISIN", ([str(fecha)])).fetchall()
                dataList = list()

                for i in range(0, len(data), 1):
                    dataList.insert(i, [fundUtils.ISINtoFundOffline(data[i][0]), data[i][1]])

                self.Pie.add_data_set(dataList, 'pie', 'Peso en Cartera', allowPointSelect=True,
                                      cursor='pointer',
                                      showInLegend=True,
                                      dataLabels={
                                          'enabled': False,
                                          'format': '<b>{point.name}</b>: {point.percentage:.1f} %',
                                          'style': {
                                              'color': "('black'"
                                          }
                                      }
                                      )

            else:
                pass

            self.browserPie.setHtml(self.Pie.htmlcontent)
            self.layoutPieChart.addWidget(self.browserPie)
            self.browserPie.show()

            pass

    ''' 
        - Calcula el valor total de Cartera actual a fecha X
    
        @params: Fecha a calcular el importe | if None: importe actual
        @returns: int (importe total de cartera)
    '''

    def importeTotalCartera(self, fecha=None):
        importeTotal = 0

        # Cartera Actual
        if fecha is None and self.currentCarteraReal is not None:

            # Conexión con la BD y creación de un cursor de consultas
            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()
            ISINS_cartera = db.execute("select Importe "
                                       "from ( select t.*, row_number() over(partition by ISIN "
                                       "order by Fecha desc) rn "
                                       "from [" + str(self.id_usuario[0]) + "_" +
                                       str(self.currentCarteraReal) + "] t) t "
                                                                      "where rn = 1 order by ISIN",
                                       ([])).fetchall()

            # Recorre los ISINS en Cartera
            for isins in ISINS_cartera:
                importeTotal = importeTotal + isins[0]

        if not fecha is None and self.currentCarteraReal is not None:
            # Conexión con la BD y creación de un cursor de consultas
            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            db = db_connection.cursor()
            ISINS_cartera = db.execute("select Importe "
                                       "from ( select t.*, row_number() over(partition by ISIN "
                                       "order by Fecha desc) rn "
                                       "from "
                                       "(select * from [" + str(self.id_usuario[0]) + "_" +
                                       str(self.currentCarteraReal) + "] where Fecha < ? ) t) t "
                                                                      "where rn = 1 order by ISIN",
                                       ([str(fecha)])).fetchall()

            # Recorre los ISINS en Cartera
            for isins in ISINS_cartera:
                importeTotal = importeTotal + isins[0]

        return importeTotal


# --------------------------------------------------- IGNORE ---------------------------------------------------
# --------------------------------------------------- IGNORE ---------------------------------------------------
# --------------------------------------------------- IGNORE ---------------------------------------------------
'''
    def updateTable(view):
        # print('Update Table()')
        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        db = db_connection.cursor()

        sql = "SELECT ca.* FROM caracterizacion ca INNER JOIN carteras_usuario_real cu USING(ISIN) WHERE cu.nombre_cartera == ?"
        funds = db.execute(sql, ([view.cbCarterasReal.currentText()])).fetchall()

        view.tableFondos.clear()
        view.tableFondos.setHorizontalHeaderItem(0, QTableWidgetItem('Alta'))
        view.tableFondos.setHorizontalHeaderItem(1, QTableWidgetItem('ISIN'))
        view.tableFondos.setHorizontalHeaderItem(2, QTableWidgetItem('Nombre'))
        view.tableFondos.setHorizontalHeaderItem(3, QTableWidgetItem('Gestora'))
        view.tableFondos.setHorizontalHeaderItem(4, QTableWidgetItem('Tipo Act.'))
        view.tableFondos.setHorizontalHeaderItem(5, QTableWidgetItem('R.V'))
        view.tableFondos.setHorizontalHeaderItem(6, QTableWidgetItem('Zona'))
        view.tableFondos.setHorizontalHeaderItem(7, QTableWidgetItem('Estilo'))
        view.tableFondos.setHorizontalHeaderItem(8, QTableWidgetItem('Sector'))
        view.tableFondos.setHorizontalHeaderItem(9, QTableWidgetItem('Tamaño'))
        view.tableFondos.setHorizontalHeaderItem(10, QTableWidgetItem('Divisa'))
        view.tableFondos.setHorizontalHeaderItem(11, QTableWidgetItem('Cubierta'))
        view.tableFondos.setHorizontalHeaderItem(12, QTableWidgetItem('Duración'))

        view.tableFondos.setColumnWidth(2, 350)
        view.tableFondos.setRowCount(len(funds))

        f = 0

        for fila in db.execute(sql, ([view.cbCarterasReal.currentText()])):
            view.tableFondos.setItem(f, 0, QTableWidgetItem(str(fila[0])))
            view.tableFondos.setItem(f, 1, QTableWidgetItem(str(fila[1])))
            view.tableFondos.setItem(f, 2, QTableWidgetItem(str(fila[2])))
            view.tableFondos.setItem(f, 3, QTableWidgetItem(str(fila[3])))
            view.tableFondos.setItem(f, 4, QTableWidgetItem(str(fila[4])))
            view.tableFondos.setItem(f, 5, QTableWidgetItem(str(fila[5])))
            view.tableFondos.setItem(f, 6, QTableWidgetItem(str(fila[6])))
            view.tableFondos.setItem(f, 7, QTableWidgetItem(str(fila[7])))
            view.tableFondos.setItem(f, 8, QTableWidgetItem(str(fila[8])))
            view.tableFondos.setItem(f, 9, QTableWidgetItem(str(fila[9])))
            view.tableFondos.setItem(f, 10, QTableWidgetItem(str(fila[10])))
            view.tableFondos.setItem(f, 11, QTableWidgetItem(str(fila[11])))
            f += 1

        db.close()
    '''
