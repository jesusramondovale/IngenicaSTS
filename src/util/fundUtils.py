import sqlite3

import investpy

from highstock import Highstock
from datetime import datetime

from src.util.dialogs import isinNotFoundDialog


def getFundINFO(isin):
    return investpy.funds.search_funds(by='isin', value=isin)


def nameToISIN(name):
    df = investpy.funds.search_funds(by='name', value=name)
    isin = df.at[0, 'isin']
    return isin


def ISINtoFund(isin):
    df = investpy.funds.search_funds(by='isin', value=isin)
    name = df.at[0, 'name']
    return name


def saveHistoricalFund(self, isin):
    db_connection = sqlite3.connect('DemoData.db', isolation_level=None)
    cursor = db_connection.cursor()

    try:
        # Comprobar existencia de tabla 'isin'
        cursor.execute("SELECT * FROM " + isin + " ")
        print('El fondo ' + isin + ' ya está grabado en BD. No se hace nada')
        cursor.close()

    except sqlite3.OperationalError:
        print('No existe, procedo a descargar y grabar')

        try:
            print('Descargando en investing.com ...')
            data = investpy.funds.get_fund_historical_data(
                fund=ISINtoFund(isin),
                country=getFundINFO(isin).at[0, 'country'],
                from_date='01/01/1970',
                to_date=datetime.today().strftime('%d/%m/%Y'),
                as_json=False
            )
            print('Grabando ...')
            data.to_sql(isin, con=db_connection)
            print('Completado con éxito!')
            cursor.close()

        except RuntimeError:
            print('El fondo no ha sido encontrado en investing.com!')
            dlg = isinNotFoundDialog(self)
            dlg.exec()
            cursor.close()


def graphHistoricalISIN(self, isins_selected, absolute):
    if len(isins_selected) != 0:

        names = []
        currency = getFundINFO(isins_selected[0]).at[0, 'currency']

        for a in range(0, len(isins_selected), 1):
            names.append(getFundINFO(isins_selected[a]).at[0, 'name'])

        db_connection = sqlite3.connect('DemoData.db', isolation_level=None)

        H = Highstock()

        for j in range(0, len(isins_selected), 1):
            cursor = db_connection.cursor()
            data = cursor.execute("SELECT * FROM " + isins_selected[j] + " ").fetchall()

            values = []
            for row in range(0, len(data), 1):
                date = data[row][0]
                stamp = datetime.strptime(date[:10], "%Y-%m-%d")
                dataTuple = (datetime.fromtimestamp(datetime.timestamp(stamp)), data[row][1])
                values.append(dataTuple)

            H.add_data_set(values, "line", names[j])
            cursor.close()

        if absolute:
            options = {
                # 'colors': ['#a0a0a0'],

                'chart': {
                    'zoomType': 'x',
                    'backgroundColor': '#a0a0a0',
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
        else:
            options = {
                # 'colors': ['#a0a0a0'],

                'chart': {
                    'zoomType': 'x',
                    'backgroundColor': '#a0a0a0',
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

                "plotOptions": {"series": {"compare": "percent"}},

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

        # Figure Method
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
