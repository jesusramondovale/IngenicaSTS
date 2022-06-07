######################################################################
#   LIBRERÍA DE ÚTILES PARA CONSULTA DE DATOS SOBRE INVESTING.COM  ##
#          EMPAQUETANDO LLAMADAS A LA API investpy                 ##
######################################################################
import sqlite3
import investpy
import threading

# Librería de Gráficos Útiles especializados en
# la visualización de índices bursátiles
from highstock import Highstock
from highcharts import Highchart

from PyQt5 import QtWebEngineWidgets
from datetime import datetime, timedelta
from src.util.dialogs import isinNotFoundDialog, errorInesperado, refreshCompleteDialog




'''
- Descarga de investing.com  y actualiza en DB los históricos presentes en carteras 
del  Usuario desde la última fecha presente del registro hasta hoy

@params: None
@:returns: None

'''


def refreshHistorics(view):

    db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
    db = db_connection.cursor()
    ISINs = db.execute("SELECT ISIN FROM carteras_usuario WHERE id_usuario = ? ",
                       view.id_usuario).fetchall()
    for ISIN in ISINs:
        try:
            lastRow = db.execute("SELECT Open , Date FROM " + ISIN[0] + " ORDER BY Date DESC ").fetchone()
            lastValue = lastRow[0]
            lastDate = lastRow[1]
            lastDateTime = datetime.strptime(lastDate, '%Y-%m-%d %H:%M:%S')
            print(str(ISIN[0]) + ' -> ' + str(lastValue) + ' @ (' + str(lastDate) + ')')

        except sqlite3.OperationalError:
            lastRow = db.execute("SELECT Open , Date FROM [" + ISIN[0] + "] ORDER BY Date DESC ").fetchone()
            lastValue = lastRow[0]
            lastDate = lastRow[1]
            lastDateTime = datetime.strptime(lastDate, '%Y-%m-%d %H:%M:%S')
            print(str(ISIN[0]) + ' -> ' + str(lastValue) + ' @ (' + str(lastDate) + ')')

        try:
            lastDateTime += timedelta(days=1)
            data = investpy.funds.get_fund_historical_data(
                fund=ISINtoFund(ISIN[0]),
                country=getFundINFO(view, ISIN[0]).at[0, 'country'],
                from_date=lastDateTime.strftime('%d/%m/%Y'),
                to_date=datetime.today().strftime('%d/%m/%Y'),
                as_json=False
            )
            print('Actualizando ... ' + str(ISIN[0]))
            data.to_sql(ISIN[0], con=db_connection, if_exists='append')

        except ValueError:
            pass

        try:
            lastRow = db.execute("SELECT Open , Date FROM " + ISIN[0] + " ORDER BY Date DESC ").fetchone()
            lastValue = lastRow[0]
            lastDate = lastRow[1]
            print('NUEVO: ' + str(ISIN[0]) + ' -> ' + str(lastValue) + ' @ (' + str(lastDate) + ')')

        except sqlite3.OperationalError:
            lastRow = db.execute("SELECT Open , Date FROM [" + ISIN[0] + "] ORDER BY Date DESC ").fetchone()
            lastValue = lastRow[0]
            lastDate = lastRow[1]
            print('NUEVO:' + str(ISIN[0]) + ' -> ' + str(lastValue) + ' @ (' + str(lastDate) + ')')

    if view.cbModo.currentIndex() == 0:
        UpdateGraph(view, None , view.isins_selected , True )
    else:
        UpdateGraph(view, None , view.isins_selected , False )

    refreshCompleteDialog(view).exec()
    return None

'''
    - Obtiene la Información existente en investing.com 
    del Fondo introducido como parámetro de manera indiferente 
    entre ISINs o Symbols. 
    
    @params: ISIN del Fondo | Symbol del Fondo
    @returns: DataFrame con la Información proporcionada
    por investing.com del Fondo (nombre, país, isin, moneda..)
    
'''


def getFundINFO(self, isin):
    try:
        return investpy.funds.search_funds(by='isin', value=isin)

    except:
        return investpy.funds.search_funds(by='symbol', value=isin)


'''
    - Convierte el ISIN/Symbol de un fondo
    en su nombre completo.
    
    @params: ISIN | Symbol
    @returns: Nombre (str) del Fondo     
'''


def ISINtoFund(isin):
    try:
        df = investpy.funds.search_funds(by='isin', value=isin)
        name = df.at[0, 'name']
        return name
    except RuntimeError:
        df = investpy.funds.search_funds(by='symbol', value=isin)
        name = df.at[0, 'name']
        return name


'''
    - Descarga de investing.com y graba en BD
    todos los valores históricos del fondo introducido
    como parámetro (en caso de no existir previamente)
    - Crea una nueva tabla (si no existe) en BD con 
    nombre = ISIN/Symbol y carga todos sus datos.
    
    @params: ISIN | Symbol 
    @returns: None
'''


def saveHistoricalFund(self, isin):
    db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
    cursor = db_connection.cursor()
    try:
        try:
            # Comprobar existencia de tabla 'isin'
            cursor.execute("SELECT * FROM " + isin)
            print('El fondo ' + isin + ' ya está grabado en BD. No se hace nada')
            cursor.close()
            return

        except sqlite3.OperationalError:
            # Comprobar existencia de tabla 'symbol'
            try:
                cursor.execute("SELECT * FROM " + "[" + isin + "]")
                print('El fondo ' + isin + ' ya está grabado en BD. No se hace nada')
                cursor.close()
                return
            except:
                cursor.close()
                raise ValueError
                return

    except ValueError:
        print('No existe, procedo a descargar y grabar')

        try:
            print('Descargando en investing.com ...')
            data = investpy.funds.get_fund_historical_data(
                fund=ISINtoFund(isin),
                country=getFundINFO(self, isin).at[0, 'country'],
                from_date='01/01/1970',
                to_date=datetime.today().strftime('%d/%m/%Y'),
                as_json=False
            )
            print('Grabando ...')
            data.to_sql(isin, con=db_connection)
            print('Completado con éxito!')
            cursor.close()
            return


        except RuntimeError:
            print('El fondo no ha sido encontrado en investing.com!')
            dlg = isinNotFoundDialog(self)
            dlg.exec()
            cursor.close()
            return


'''
    - Grafica la lista de ISINS/Symbols seleccionados 
    por el usuario en el layout de la vista UserView. 
    
    @params: self (UserView)
           : list -> Lista de ISINS/Symbols a graficar (isins_selected)
           : bool -> Modo de graficación (absolute=True o evolución=False)
    @returns: None
'''


def graphHistoricalISIN(self, isins_selected, absolute):

    if len(isins_selected) != 0:

        names = []
        fundNames = []

        currency = getFundINFO(self, isins_selected[0]).at[0, 'currency']

        for a in range(0, len(isins_selected), 1):
            names.append(isins_selected[a])
            fundNames.append(ISINtoFund(isins_selected[a]))

        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
        cursor = db_connection.cursor()
        H = Highstock()

        for j in range(0, len(isins_selected), 1):

            try:
                data = cursor.execute("SELECT * FROM " + isins_selected[j] + " ").fetchall()
            except sqlite3.OperationalError:
                data = cursor.execute("SELECT * FROM " + "[" + isins_selected[j] + "]" + " ").fetchall()

            values = []
            for row in range(0, len(data), 1):
                date = data[row][0]
                stamp = datetime.strptime(date[:10], "%Y-%m-%d")
                dataTuple = (datetime.fromtimestamp(datetime.timestamp(stamp)), data[row][1])
                values.append(dataTuple)

            H.add_data_set(values, "line", fundNames[j])

        if absolute:
            options = {
                # 'colors': ['#a0a0a0'],
                'legend': {
                    'enabled': True
                },
                'chart': {
                    'zoomType': 'x',
                    'backgroundColor': '#979797',
                    'animation': {
                        'duration': 2000
                    },
                },
                'title': {
                    'text': names
                },

                "rangeSelector": {"selected": 6},

                "yAxis": {
                    'opposite': True,
                    'title': {
                        'text': currency,
                        'align': 'middle',
                        'style': {
                            'fontSize': '18px'
                        }
                    },
                    'labels': {
                        'align': 'left'
                    },

                    "plotLines": [{"value": 0, "width": 2, "color": "white"}],
                },

                "tooltip": {
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ',
                    "valueDecimals": 2,
                },

            }
            H.set_dict_options(options)
            cursor.close()
        else:
            options = {
                # 'colors': ['#a0a0a0'],
                'legend': {
                    'enabled': True
                },
                'chart': {
                    'zoomType': 'x',
                    'backgroundColor': '#979797',
                    'animation': {
                        'duration': 2000
                    },
                },
                'title': {
                    'text': names
                },

                "rangeSelector": {"selected": 6},

                "yAxis": {
                    'opposite': True,
                    'title': {
                        'text': '%',
                        'align': 'middle',
                        'style': {
                            'fontSize': '18px'
                        }

                    },
                    'labels': {
                        'align': 'left'
                    },

                    "plotLines": [{"value": 0, "width": 3, "color": "white"}],
                },

                "plotOptions": {
                    "series": {
                        "compare": "percent"
                    }
                },

                "tooltip": {
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ',
                    "valueDecimals": 2,
                },
            }
            H.set_dict_options(options)

        self.browser.setHtml(H.htmlcontent)
        self.layout.addWidget(self.browser)
        self.labelNoIsin.hide()
        self.browser.show()

        cursor.close()
    else:
        self.browser.hide()
        self.labelNoIsin.show()
        self.labelNoIsin.setText('Seleccione primero un ISIN de la lista!')





'''
    - Actualiza el gráfico de la Vista con los Isins a graficar
    
    @params: UserView (self), 
             ISIN pulsado actual (ISIN)  
             Lista de Isins seleccionados (isins_selected)
             Modo de Graficación: Aboluste (True)
    @returns: None
'''


def UpdateGraph(self, isin, isins_selected, absolute):
    if isin is None:
        print('ISIN is None')
        names = []
        fundNames = []
        for elem in isins_selected:
            names.append(elem)
            fundNames.append((ISINtoFund(elem)))

        if len(isins_selected) != 0:
            currency = getFundINFO(self, isins_selected[0]).at[0, 'currency']

            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            cursor = db_connection.cursor()
            self.H = Highstock()

            for j in range(0, len(isins_selected), 1):

                try:
                    data = cursor.execute("SELECT * FROM " + isins_selected[j] + " ").fetchall()
                    values = []
                    for row in range(0, len(data), 1):
                        date = data[row][0]
                        stamp = datetime.strptime(date[:10], "%Y-%m-%d")
                        dataTuple = (datetime.fromtimestamp(datetime.timestamp(stamp)), data[row][1])
                        values.append(dataTuple)

                    self.H.add_data_set(values, "line", fundNames[j])
                except sqlite3.OperationalError:
                    try:
                        data = cursor.execute("SELECT * FROM " + "[" + isins_selected[j] + "]" + " ").fetchall()

                        values = []
                        for row in range(0, len(data), 1):
                            date = data[row][0]
                            stamp = datetime.strptime(date[:10], "%Y-%m-%d")
                            dataTuple = (datetime.fromtimestamp(datetime.timestamp(stamp)), data[row][1])
                            values.append(dataTuple)

                        self.H.add_data_set(values, "line", fundNames[j])

                    except:
                        dlg = errorInesperado(self)
                        dlg.exec()

            if absolute and self.theme == 'Light':
                print('Mode: Absolute (Light)')
                options = {
                    # 'colors': ['#a0a0a0'],
                    'legend': {
                        'enabled': True
                    },
                    'chart': {
                        'zoomType': 'x',
                        'backgroundColor': '#979797',
                        'animation': {
                            'duration': 2000
                        },
                    },
                    'title': {
                        'text': names
                    },

                    "rangeSelector": {"selected": 6},

                    "yAxis": {
                        'opposite': True,
                        'title': {
                            'text': currency,
                            'align': 'middle',
                            'style': {
                                'fontSize': '18px'
                            }
                        },
                        'labels': {
                            'align': 'left'
                        },

                        "plotLines": [{"value": 0, "width": 2, "color": "white"}],
                    },

                    "tooltip": {
                        "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ',
                        "valueDecimals": 2,
                    },

                }
                self.H.set_dict_options(options)

            if not absolute and self.theme == 'Light':
                print('Mode: Evolution (Light)')
                options = {
                    # 'colors': ['#a0a0a0'],
                    'legend': {
                        'enabled': True
                    },

                    'chart': {
                        'zoomType': 'x',
                        'backgroundColor': '#979797',
                        'animation': {
                            'duration': 2000
                        },
                    },
                    'title': {
                        'text': names
                    },

                    "rangeSelector": {"selected": 6},

                    "yAxis": {
                        'opposite': True,
                        'title': {
                            'text': '%',
                            'rotation': 90,
                            'align': 'middle',
                            'style': {
                                'fontSize': '18px'
                            }

                        },
                        'labels': {
                            'align': 'left'
                        },

                        "plotLines": [{"value": 0, "width": 3, "color": "white"}],
                    },

                    "plotOptions": {
                        "series": {
                            "compare": "percent"
                        }
                    },

                    "tooltip": {
                        "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ',
                        "valueDecimals": 2,
                    },
                }
                self.H.set_dict_options(options)

            if absolute and self.theme == 'Dark':
                print('Mode: Absolute (Dark)')
                options = {
                    # 'colors': ['#a0a0a0'],
                    'legend': {
                        'enabled': True
                    },

                    'chart': {
                        'zoomType': 'x',
                        'backgroundColor': '#222222',
                        'animation': {
                            'duration': 2000
                        },
                    },
                    'title': {
                        'text': names
                    },

                    "rangeSelector": {"selected": 6},

                    "yAxis": {
                        'opposite': True,
                        'title': {
                            'text': currency,
                            'rotation': 90,
                            'align': 'middle',
                            'style': {
                                'fontSize': '18px'
                            }

                        },
                        'labels': {
                            'align': 'left'
                        },

                        "plotLines": [{"value": 0, "width": 3, "color": "white"}],
                    },



                    "tooltip": {
                        "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ',
                        "valueDecimals": 2,
                    },
                }
                self.H.set_dict_options(options)

            if not absolute and self.theme == 'Dark':
                print('Mode: Evolution (Dark)')
                options = {
                    # 'colors': ['#a0a0a0'],
                    'legend': {
                        'enabled': True
                    },

                    'chart': {
                        'zoomType': 'x',
                        'backgroundColor': '#222222',
                        'animation': {
                            'duration': 2000
                        },
                    },
                    'title': {
                        'text': names
                    },

                    "rangeSelector": {"selected": 6},

                    "yAxis": {
                        'opposite': True,
                        'title': {
                            'text': '%',
                            'rotation': 90,
                            'align': 'middle',
                            'style': {
                                'fontSize': '18px'
                            }

                        },
                        'labels': {
                            'align': 'left'
                        },

                        "plotLines": [{"value": 0, "width": 3, "color": "white"}],
                    },

                    "plotOptions": {
                        "series": {
                            "compare": "percent"
                        }
                    },

                    "tooltip": {
                        "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ',
                        "valueDecimals": 2,
                    },
                }
                self.H.set_dict_options(options)

            self.browser.setHtml(self.H.htmlcontent)
            self.layout.addWidget(self.browser)
            self.labelNoIsin.hide()
            self.browser.show()

        else:
            self.browser.hide()
            self.labelNoIsin.show()


    else:
        if len(isins_selected) != 0:
            if len(isins_selected) == 1:
                self.H = Highstock()

            names = []
            for elem in isins_selected:
                names.append(elem)

            currency = getFundINFO(self, isins_selected[0]).at[0, 'currency']

            db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
            cursor = db_connection.cursor()

            try:
                data = cursor.execute("SELECT * FROM " + isin + " ").fetchall()
            except sqlite3.OperationalError:
                data = cursor.execute("SELECT * FROM " + "[" + isin + "]" + " ").fetchall()
            values = []

            for row in range(0, len(data), 1):
                date = data[row][0]
                stamp = datetime.strptime(date[:10], "%Y-%m-%d")
                dataTuple = (datetime.fromtimestamp(datetime.timestamp(stamp)), data[row][1])
                values.append(dataTuple)

            self.H.add_data_set(values, "line", ISINtoFund(isin))

            if absolute:
                options = {
                    # 'colors': ['#a0a0a0'],
                    'legend': {
                        'enabled': True
                    },
                    'chart': {
                        'zoomType': 'x',
                        'backgroundColor': '#979797',
                        'animation': {
                            'duration': 2000
                        },
                    },
                    'title': {
                        'text': names
                    },

                    "rangeSelector": {"selected": 6},

                    "yAxis": {
                        'opposite': True,
                        'title': {
                            'text': currency,
                            'align': 'middle',
                            'style': {
                                'fontSize': '18px'
                            }
                        },
                        'labels': {
                            'align': 'left'
                        },

                        "plotLines": [{"value": 0, "width": 2, "color": "white"}],
                    },

                    "tooltip": {
                        "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ',
                        "valueDecimals": 2,
                    },

                }
                self.H.set_dict_options(options)
                cursor.close()
            else:
                options = {
                    # 'colors': ['#a0a0a0'],
                    'legend': {
                        'enabled': True
                    },
                    'chart': {
                        'zoomType': 'x',
                        'backgroundColor': '#979797',
                        'animation': {
                            'duration': 2000
                        },
                    },
                    'title': {
                        'text': names
                    },

                    "rangeSelector": {"selected": 6},

                    "yAxis": {
                        'opposite': True,
                        'title': {
                            'text': '%',
                            'rotation': 90,
                            'align': 'middle',
                            'style': {
                                'fontSize': '18px'
                            }

                        },
                        'labels': {
                            'align': 'left'
                        },

                        "plotLines": [{"value": 0, "width": 3, "color": "white"}],
                    },

                    "plotOptions": {
                        "series": {
                            "compare": "percent"
                        }
                    },

                    "tooltip": {
                        "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ',
                        "valueDecimals": 2,
                    },
                }
                self.H.set_dict_options(options)
                cursor.close()

            self.browser.setHtml(self.H.htmlcontent)
            self.layout.addWidget(self.browser)
            self.labelNoIsin.hide()
            self.browser.show()

            cursor.close()

        else:
            self.browser.hide()
            self.labelNoIsin.show()
            self.labelNoIsin.setText('Seleccione primero un ISIN de la lista!')



#####################     A P É N D I C E        ###############################

# Grafico Figure Method
        '''
        VÍA FIGURE
        fig = go.Figure()

        fig.add_trace(go.Candlestick(x=data.index,
                                     open=data['Open'],
                                     high=data['High'],
                                     low=data['Low'],
                                     close=data['Close'],
                                     name='Valor de mercado'))

        fig.update_layout(
            title=name,
            yaxis_title=currency

        )

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=15, label='15 M', step='minute', stepmode='backward'),
                    dict(count=45, label='45 M', step='minute', stepmode='backward'),
                    dict(count=1, label='1 H', step='hour', stepmode='todate'),
                    dict(count=2, label='2 H', step='hour', stepmode='backward'),
                    dict(step='all')

                ])
            )
        )

        view.browser = QtWebEngineWidgets.QWebEngineView(view)
        view.layout.addWidget(view.browser)
        view.browser.setHtml(fig.to_html(include_plotlyjs='cdn'))
        '''

# Grafico HTML Method
        ''' Vía llamada HTML 
        view.browser = QtWebEngineWidgets.QWebEngineView(view)
        url = 'https://funds.ddns.net/h.php?isin=' + ISINS[0][0]
        q_url = QUrl(url)

        view.browser.load(q_url)
        view.layout.addWidget(view.browser)
        '''
