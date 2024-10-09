import time
from pybit.unified_trading import HTTP
import pandas as pd
from datetime import datetime, timedelta, timezone
import sqlite3
import logging
import os
import pytz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
DB_PATH = '../../data/database.sqlite3'
session = HTTP(testnet=False)

def ensure_table_exists():
    """Check if the 'candles' table exists and create it if it doesn't."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Check if the table exists
    cur.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='candles';
    """)
    table_exists = cur.fetchone()
    if not table_exists:
        # Create the table if it doesn't exist
        create_table_query = """
        CREATE TABLE candles (
            symbol TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            PRIMARY KEY (symbol, timestamp)
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        logging.info("Created 'candles' table.")
    else:
        logging.info("'candles' table already exists.")
    cur.close()
    conn.close()

def connect_to_db():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    return conn

def fetch_data(symbol, start_date, end_date):
    """Fetch candle data from the database for a given symbol and date range."""
    conn = connect_to_db()
    query = """
    SELECT timestamp AS date, open, high, low, close, volume
    FROM candles
    WHERE symbol = ? AND
          timestamp BETWEEN ? AND ?
    ORDER BY timestamp;
    """
    params = (symbol, int(start_date.timestamp() * 1000), int(end_date.timestamp() * 1000))
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    df['date'] = pd.to_datetime(df['date'], unit='ms', utc=True)
    return df

def insert_data(df, symbol):
    """Insert fetched data into the database, handling upserts."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            records = df.to_dict('records')
            values = [
                (
                    symbol,
                    int(record['timestamp'].timestamp() * 1000),
                    record['open'],
                    record['high'],
                    record['low'],
                    record['close'],
                    record['volume']
                )
                for record in records
            ]

            insert_query = """
            INSERT INTO candles (symbol, timestamp, open, high, low, close, volume) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol, timestamp) DO UPDATE SET
                open=excluded.open,
                high=excluded.high,
                low=excluded.low,
                close=excluded.close,
                volume=excluded.volume;
            """

            cur.executemany(insert_query, values)
            conn.commit()
            logging.debug(f"Data for {symbol} inserted successfully")
    except Exception as e:
        logging.error(f"Error inserting data for {symbol}: {e}")

def get_last_timestamp(symbol):
    """Retrieve the last timestamp for a given symbol from the database."""
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT MAX(timestamp) FROM candles WHERE symbol = ?;", (symbol,))
        result = cur.fetchone()
        last_timestamp_ms = result[0] if result and result[0] else None
        last_timestamp = pd.to_datetime(last_timestamp_ms, unit='ms', utc=True) if last_timestamp_ms else None
        cur.close()
        conn.close()
        return last_timestamp
    except Exception as e:
        logging.error(f"Error fetching last timestamp for {symbol}: {e}")
        return None

def get_candles(symbol, timeframe, start_date, end_date):
    """Fetch candle data from the API for a given symbol and date range."""
    logging.debug(f"Fetching candles for {symbol} from {start_date} to {end_date}")
    candles_data = []
    limit_bars = 1000
    while start_date < end_date:
        candles = session.get_kline(symbol=symbol, interval=timeframe, start=int(start_date.timestamp() * 1000),
                                    limit=limit_bars)
        # print("Loading")
        candles_list = candles['result']['list']
        start_date = pd.to_datetime(int(candles_list[0][0]), unit='ms', utc=True)
        candles_data += candles_list[::-1]  # .extend(candles_list.reverse())
        if len(candles_list) < limit_bars:
            break

    df = pd.DataFrame(candles_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
    df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp']), unit='ms', utc=True)
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric,
                                                                                                          errors='coerce')

    df = df.drop_duplicates(subset='timestamp', keep='first')
    logging.info(f"Candles fetched and processed successfully for symbol - {symbol}")
    return df

def prepare_data(symbol, days):
    """Prepare data by fetching new candles and returning a DataFrame."""
    last_timestamp = get_last_timestamp(symbol)
    start_date = pd.Timestamp.now(tz=timezone.utc) - timedelta(days=days)
    end_date = pd.Timestamp.now(tz=timezone.utc) - timedelta(minutes=1)
    logging.info(f"Loading new data for {symbol} from {start_date} to {end_date}")
    if last_timestamp:
        df = get_candles(symbol, 1, last_timestamp, end_date)
        return df
    else:
        df = get_candles(symbol, 1, start_date, end_date)
        return df

def get_symbols_by_turnover(turnover):
    """Retrieve symbols with a 24h turnover greater than the specified amount."""
    response = session.get_tickers(category="linear")
    if response['retCode'] != 0:
        logging.error("Failed to get tickers info")
        exit()
    filtered_symbols = [
        ticker['symbol'] for ticker in response['result']['list']
        if float(ticker['turnover24h']) > turnover
    ]
    logging.info(
        f"Symbols with turnover greater than {turnover}$: {filtered_symbols}, Total number: {len(filtered_symbols)}"
    )
    return filtered_symbols

def update_symbol(symbol, num_days):
    """Update data for a single symbol."""
    try:
        df = prepare_data(symbol, num_days)
        if not df.empty:
            insert_data(df, symbol)
    except Exception as e:
        logging.error(f"Error updating data for {symbol}: {e}")

def update_all_symbols(symbols, num_days):
    """Update data for all symbols sequentially."""
    for symbol in symbols:
        update_symbol(symbol, num_days)


def update_symbols_continuously(symbols):
    """Continuously update data for all symbols."""
    while True:
        logging.debug("Updating symbols continuously")
        for symbol in symbols:
            update_symbol(symbol, 0.0021)  # Fetch data for the last ~3 minutes
        time.sleep(5)  # Wait for 3 minutes before the next update

def main():
    ensure_table_exists()
    turnover_threshold = 300_000_000
    update_data_continously = True
    symbols = get_symbols_by_turnover(turnover_threshold)
    num_days = 10  # Number of past days to fetch data for
    update_all_symbols(symbols, num_days)
    if update_data_continously:
        update_symbols_continuously(symbols)

if __name__ == '__main__':
    main()
