import psycopg2
from decouple import config

postgres_pass = config('POSTGRES_PASS')
con = psycopg2.connect(database="postgres", user="postgres", password=postgres_pass, host="127.0.0.1", port="5432")
print("Database opened successfully")

cur = con.cursor()
cur.execute('''CREATE TABLE RSI_SIGNAL
      (id               SERIAL      PRIMARY KEY,
      pair_symbol       CHAR(50)    NOT NULL,
      signal_date       TIMESTAMP   NOT NULL,
      rsi_2             real        NOT NULL,
      rsi_1             real        NOT NULL,
      previous_candle   real        NOT NULL);''')
print("Table created successfully")

con.commit()
con.close()