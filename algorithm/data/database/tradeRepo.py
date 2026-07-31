from sqlalchemy import text
from .db import engine

def insertTrade(trade):

    print("Inserting:", trade["symbol"], trade["entry_date"])
    query = text("""INSERT INTO trades
                 ( symbol, entry_date, ema50, ema200, rsi, volume, sentiment,
                   entry_price, outcome, parent_order_id, tp_order_id, sl_order_id )

                   VALUES(:symbol, :entry_date, :ema50, :ema200, :rsi, :volume, :sentiment,
                   :entry_price, :outcome, :parent_order_id, :tp_order_id, :sl_order_id )""")
    

    with engine.begin() as conn:
        conn.execute(query, trade)

    
    print("Inserted!")

def updateTrade(symbol, outcome):
    query = text(""" UPDATE trades 
    SET outcome = :outcome,
    status = 'CLOSED'
    WHERE id = (SELECT id FROM trades
    WHERE symbol = :symbol AND status = 'OPEN'
    ORDER BY entry_date LIMIT 1)""")

    with engine.begin() as count:
        conn.execute(query, {"symbol": symbol, "outcome": outcome})


def getOpenTrades():

    query = text("""
        SELECT *
        FROM trades
        WHERE status = 'OPEN'
    """)

    with engine.begin() as conn:

        return conn.execute(query).mappings().all()


def closeTrade(trade_id, outcome, exit_price, exit_date):

    query = text("""
        UPDATE trades
        SET
            outcome = :outcome,
            exit_price = :exit_price,
            exit_date = :exit_date,
            status = 'CLOSED'
        WHERE id = :trade_id
    """)

    with engine.begin() as conn:
        conn.execute(query, {
            "trade_id": trade_id,
            "outcome": outcome,
            "exit_price": exit_price,
            "exit_date": exit_date
        })