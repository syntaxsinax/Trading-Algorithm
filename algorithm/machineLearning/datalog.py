import sqlite3


def create_database():
    conn = sqlite3.connect("trades.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trades (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        symbol TEXT,

        entry_time TEXT,
        exit_time TEXT,

        entry_price REAL,
        exit_price REAL,

        take_profit REAL,
        stop_loss REAL,

        quantity REAL,

        ema50 REAL,
        ema200 REAL,
        rsi REAL,

        sentiment REAL,

        profit REAL,

        outcome INTEGER
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    print("✅ trades.db created successfully")

def log_trade(
    symbol,
    entry_time,
    exit_time,
    entry_price,
    exit_price,
    take_profit,
    stop_loss,
    quantity,
    ema50,
    ema200,
    rsi,
    sentiment,
    profit,
    outcome
):

    conn = sqlite3.connect("trades.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO trades(
        symbol,
        entry_time,
        exit_time,
        entry_price,
        exit_price,
        take_profit,
        stop_loss,
        quantity,
        ema50,
        ema200,
        rsi,
        sentiment,
        profit,
        outcome
    )
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        symbol,
        entry_time,
        exit_time,
        entry_price,
        exit_price,
        take_profit,
        stop_loss,
        quantity,
        ema50,
        ema200,
        rsi,
        sentiment,
        profit,
        outcome
    ))

    conn.commit()
    conn.close()