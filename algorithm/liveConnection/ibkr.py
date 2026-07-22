from ib_insync import *

def connect_ibkr(client_id=999):
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=client_id)
    return ib


def get_bars(ib, symbol, duration='5 D', bar_size='1 hour'):
    if symbol == "SPX":
        contract = Index(symbol, 'CBOE', 'USD')
    else:
       contract = Stock(symbol, 'SMART', 'USD')

    
    ib.qualifyContracts(contract)
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr=duration,
        barSizeSetting=bar_size,
        whatToShow='TRADES',
        useRTH=True
    )
    return bars