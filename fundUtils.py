import investpy

def getFundINFO(isin):
    return investpy.funds.search_funds( by='isin', value=isin)

def ISINtoFund(isin):
    df = investpy.funds.search_funds( by='isin', value=isin)
    name = df.at[0,'name']
    return name