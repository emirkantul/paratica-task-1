import psycopg2, uvicorn, addToDb, checkRSI
from fastapi import FastAPI
from decouple import config

signals_created = [] # to hold created signals to add later

# saves all signals with given parity symbol to db
def saveSignals(parity_symbol):
    for signal in signals_created:
        if signal[0] == parity_symbol:
            addToDb.addRecord(signal[0], signal[1], signal[2], signal[3], signal[4])
            signals_created.remove(signal)

postgres_pass = config('POSTGRES_PASS')

con = psycopg2.connect(database="postgres", user="postgres", password=postgres_pass, host="127.0.0.1", port="5432")

app = FastAPI()

@app.get("/")
def read_root():
    return {"works": "fine"}

# select all from database where parity_symbol matches
@app.get("/history/{parity_symbol}")
def read_parity_history(parity_symbol: str):
    cur = con.cursor()
    sql_command = f"SELECT pair_symbol, signal_date, rsi_2, rsi_1, previous_candle from RSI_SIGNAL where pair_symbol=\'{parity_symbol}\'"
    cur.execute(sql_command)
    parity_history = cur.fetchall()
    return {"parity_symbol": parity_symbol, "parity_history": parity_history}

# select all from database
@app.get("/history/")
def read_history():
    cur = con.cursor()
    sql_command = "SELECT pair_symbol, signal_date, rsi_2, rsi_1, previous_candle from RSI_SIGNAL"
    cur.execute(sql_command)
    history = cur.fetchall()
    return {"history": history}

# add all instances from singals_created to database where parity_symbols match
@app.put("/save_signals/{parity_symbol}")
def save_signal(parity_symbol: str):
    message = "no record to add"
    if signals_created:
        try:
            saveSignals(parity_symbol)
            message = "success"
                    
        except Exception:
            message = "error occured"
        
    return {"parity_symbol": parity_symbol, "message": message}

# check if there is signals that can be represented to user
@app.get("/check_signals/{parity_symbol}")
def check_signal(parity_symbol: str):
    try:
        signals_created = checkRSI.checkRSI(parity_symbol=parity_symbol)

    except Exception:
        message = "an error occured while checking RSI"

    if signals_created:
        message = "catched a signal"
    else:
        message = "no signals to create"

    return {"parity_symbol": parity_symbol, "message": message, "signals_created": signals_created}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


