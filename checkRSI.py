import json, os, datetime, talib, numpy
from binance import ThreadedWebsocketManager, client
from functools import partial
from decouple import config

closes_at = []
rsi = []
w_length = 14

api_key = config('BINANCE_API')
api_secret = config('BINANCE_SECRET')

# handle incoming messages
def handle_message(creatable_signals, msg):    
    candle = msg['k']
    is_candle_closed = candle['x']

    if is_candle_closed:
        close_time_pair = []
        signal = []
        close_time_pair.append(float(candle['c']))
        close_time_pair.append(candle['t'])

        closes_at.pop(0) # remove first element (oldest) and append new one
        closes_at.append(close_time_pair)

        np_closes = numpy.array([item[0] for item in closes_at])
        rsi = talib.RSI(np_closes, w_length)
        
        # catch signal
        if rsi[-3] != None:
            if rsi[-3] < 40 and rsi[-2] > 40:
                signal.append(msg['s'])
                signal.append(datetime.utcfromtimestamp(candle['t']).strftime('%Y-%m-%d %H:%M:%S'))
                signal.append(rsi[-3])
                signal.append(rsi[-2])
                signal.append(closes_at[-2][0])
                creatable_signals.append(signal)
                
                



def checkRSI(parity_symbol, creatable_signals, time_interval = '4h', window_length = 14):
    closes_at = []
    w_length = window_length

    # get last [window_length] element and append to closes_at to populate list for rsi calculation
    current_utc = datetime.datetime.utcnow()
    start_utc = current_utc - datetime.timedelta(days = 30)

    client_ = client.Client(api_key=api_key, api_secret=api_secret)
    klines = client_.get_historical_klines(symbol=parity_symbol, interval=time_interval, start_str=str(start_utc))

    last_w = klines[-(window_length + 2):]
    for candle in last_w:
        pair = []
        pair.append(float(candle[4]))
        pair.append(candle[0])
        closes_at.append(pair)

    np_closes = numpy.array([item[0] for item in closes_at])
    rsi = talib.RSI(np_closes, w_length)
    print("here is the last two days RSI to check if next candle can make a signal")
    print(rsi)

    twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    twm.start()

    f = partial(handle_message, creatable_signals)
    twm.start_kline_socket(callback=f, symbol=parity_symbol, interval=time_interval)

    twm.join()

if __name__ == "__main__":
   checkRSI("FTMUSDT", [])
