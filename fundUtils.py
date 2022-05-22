from datetime import datetime

import investpy
from dialogs import *
from highstock import Highstock


def getFundINFO(self, isin):
    return investpy.funds.search_funds(by='isin', value=isin)


def ISINtoFund(isin):
    df = investpy.funds.search_funds(by='isin', value=isin)
    name = df.at[0, 'name']
    return name


def graphHistoricalISIN(self, isins_selected):
    if len(isins_selected) != 0:
        hoy = datetime.today().strftime('%d/%m/%Y')
        names = []
        countrys = []
        try:
            currency = getFundINFO(self, isins_selected[0]).at[0, 'currency']
        except:
            pass

        for e in isins_selected:
            try:
                names.append(getFundINFO(self, e).at[0, 'name'])
                countrys.append(getFundINFO(self, e).at[0, 'country'])
            except:
                isins_selected.remove(e)

                dlg = isinNotFoundDialog(self)
                dlg.exec()
                pass

        try:
            H = Highstock()
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
                        'align': 'middle'
                    },
                    'labels': {
                        'align': 'left'
                    },

                    "plotLines": [{"value": 0, "width": 2, "color": "silver"}],
                },

                "plotOptions": {"series": {"compare": "percent"}},

                "tooltip": {
                    "pointFormat": '<span style="color:{series.color}">{series.name}</span>: <b>{point.y}</b> ',
                    "valueDecimals": 2,
                },
            }
            H.set_dict_options(options)
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

            self.browser.setHtml(H.htmlcontent)
            self.layout.addWidget(self.browser)

            self.browser.show()
            self.labelNoIsin.hide()

        except:
            pass

    else:
        self.browser.hide()
        self.labelNoIsin.show()
        self.labelNoIsin.setText('Seleccione primero un ISIN de la lista!')
