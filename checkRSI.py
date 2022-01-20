import datetime, talib, numpy
from signal import signal
from binance import client
from decouple import config

closes_at = []
rsi = []
w_length = 14

api_key = config('BINANCE_API')
api_secret = config('BINANCE_SECRET')

def checkRSI(parity_symbol, time_interval = '4h', window_length = 14):
    creatable_signals = []
    closes_at = []
    w_length = window_length

    # get last [window_length] element and append to closes_at to populate list for rsi calculation
    current_utc = datetime.datetime.utcnow()
    start_utc = current_utc - datetime.timedelta(days = 30)

    client_ = client.Client(api_key=api_key, api_secret=api_secret)
    klines = client_.get_historical_klines(symbol=parity_symbol, interval=time_interval, start_str=str(start_utc))

    # get last window_length + 3 (to check rsi[-2] and rsi[-3] values and to create a signal on current last closed candle)
    last_w = klines[-(window_length + 3):]
    for candle in last_w:
        pair = []
        pair.append(float(candle[4]))
        pair.append(candle[0])
        closes_at.append(pair)

    # calculate rsi
    np_closes = numpy.array([item[0] for item in closes_at])
    rsi = talib.RSI(np_closes, w_length)
    print("here is the last two days RSI to check if next candle can make a signal")
    print(rsi)

    signal = []
    
    # catch signal
    if rsi[-3] < 40 and rsi[-2] > 40:
        signal.append(parity_symbol)
        signal.append(datetime.utcfromtimestamp(candle['t']).strftime('%Y-%m-%d %H:%M:%S'))
        signal.append(rsi[-3])
        signal.append(rsi[-2])
        signal.append(closes_at[-2][0])
        creatable_signals.append(signal)
        print("catched signal:", signal)
    
    return creatable_signals
            
if __name__ == "__main__":
   checkRSI("FTMUSDT", [])
