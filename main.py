from typing import Optional
from numpy.core.multiarray import array
import psycopg2, uvicorn, threading, addToDb, checkRSI
from fastapi import FastAPI
from decouple import config


started_checking = False # to check if already started checking signals
signals_created = [] # to hold created signals to add later
last_parity = "" # to keep check signal parity_symbol changes
postgres_pass = config('POSTGRES_PASS')
con = psycopg2.connect(database="postgres", user="postgres", password=postgres_pass, host="127.0.0.1", port="5432")

app = FastAPI()

@app.get("/")
def read_root():
    return {"works": "fine"}

# select all from database where parity_symbol matches
@app.get("/history/{parity_symbol}")
def read_parity_history(parity_symbol: str):
    global con
    cur = con.cursor()
    sql_command = f"SELECT pair_symbol, signal_date, rsi_2, rsi_1, previous_candle from RSI_SIGNAL where pair_symbol=\'{parity_symbol}\'"
    cur.execute(sql_command)
    parity_history = cur.fetchall()
    return {"parity_symbol": parity_symbol, "parity_history": parity_history}

# select all from database
@app.get("/history/")
def read_history():
    global con
    cur = con.cursor()
    sql_command = "SELECT pair_symbol, signal_date, rsi_2, rsi_1, previous_candle from RSI_SIGNAL"
    cur.execute(sql_command)
    history = cur.fetchall()
    return {"history": history}

# add all instances from singals_created to database where parity_symbols match
@app.put("/save_signals/{parity_symbol}")
def save_signal(parity_symbol: str):
    global signals_created
    done = False
    message = "no record to add"
    try:
        for signal in signals_created:
            if signal[0] == parity_symbol:
                addToDb.addRecord(signal[0], signal[1], signal[2], signal[3], signal[4])
                done = True
                signals_created.remove(signal)
    except Exception:
        message = "error occured"
    if done:
        message = "success"
    return {"parity_symbol": parity_symbol, "message": message}


@app.get("/check_signals/{parity_symbol}")
def check_signal(parity_symbol: str):
    global started_checking
    global signals_created
    global last_parity
    message = "started to checking signals"

    # first time start checking with given parity. used thread for concurrency
    if not started_checking:
        try:
            check_signals = threading.Thread(target=checkRSI.checkRSI, args=(parity_symbol, signals_created), daemon=True)
            check_signals.start()
            started_checking = True
            last_parity = parity_symbol
        except Exception:
            message = "an error occured"
            
    # not first time check last_parity if we are trying to check the same parity_symbol
    else:
        if not last_parity == parity_symbol:
            try:
                check_signals = threading.Thread(target=checkRSI.checkRSI, args=(parity_symbol, signals_created), daemon=True)
                check_signals.start()
                started_checking = True
                last_parity = parity_symbol
            except Exception:
                message = "an error occured"
        else:
            message = "already started to checking this parity. here is the results"
    return {"parity_symbol": parity_symbol, "message": message, "signals_created": signals_created}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)