import investpy

from highstock import Highstock
from datetime import datetime


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


def graphHistoricalISIN(self, isins_selected):
    if len(isins_selected) != 0:
        hoy = datetime.today().strftime('%d/%m/%Y')
        names = []
        countrys = []

        currency = getFundINFO(isins_selected[0]).at[0, 'currency']

        for e in isins_selected:

            names.append(getFundINFO(e).at[0, 'name'])
            countrys.append(getFundINFO(e).at[0, 'country'])

            H = Highstock()

            for i in range(0, len(names), 1):

                data = investpy.funds.get_fund_historical_data(
                    fund=names[i],
                    country=countrys[i],
                    from_date='01/01/1970',
                    to_date=hoy,
                    as_json=False
                )
                values = []
                for x in range(0, len(data.index), 1):
                    dataTuple = (data.index[x], data['Open'][x])
                    values.append(dataTuple)

                H.add_data_set(values, "line", names[i])

            if len(isins_selected) == 1:
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

            self.browser.show()
            self.labelNoIsin.hide()

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
