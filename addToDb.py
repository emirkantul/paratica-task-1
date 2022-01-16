import psycopg2
from decouple import config

postgres_pass = config('POSTGRES_PASS')

def addRecord(pair_symbol, signal_date, rsi_2, rsi_1, previous_candle):
    con = psycopg2.connect(database="postgres", user="postgres", password=postgres_pass, host="127.0.0.1", port="5432")
    cur = con.cursor()
    sql_command = f"INSERT INTO RSI_SIGNAL (pair_symbol,signal_date,rsi_2,rsi_1,previous_candle) VALUES (\'{pair_symbol}\', \'{signal_date}\', {str(rsi_2)}, {str(rsi_1)}, {str(previous_candle)})"
    cur.execute(sql_command)
    con.commit()
    print("Record added successfully")

    con.close()