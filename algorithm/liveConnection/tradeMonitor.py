from .ibkr import connect_ibkr
from data.database.tradeRepo import getOpenTrades, closeTrade

ib = connect_ibkr(client_id=2)

print("Trade Monitor En Linea")

open_trades = getOpenTrades()
print(f"Open trades Found: {len(open_trades)}")
ib_trades = ib.trades()

for trade in open_trades:

    print(f"\nChecking {trade['symbol']}")

    tp_order = next(
        (
            t
            for t in ib_trades
            if t.order.orderId == trade["tp_order_id"]
        ),
        None
    )

    sl_order = next(
        (
            t
            for t in ib_trades
            if t.order.orderId == trade["sl_order_id"]
        ),
        None
    )

    if tp_order:
        print("TP:", tp_order.orderStatus.status)

    if sl_order:
        print("SL:", sl_order.orderStatus.status)


    if tp_order and tp_order.orderStatus.status == "Filled":

        closeTrade(
            trade["id"],
            1,
            tp_order.orderStatus.avgFillPrice,
            tp_order.log[-1].time
    )
    print(tp_order)
    print(tp_order.orderStatus)

    if sl_order and sl_order.orderStatus.status == "Filled":

        closeTrade(
            trade["id"],
            0,
            sl_order.orderStatus.avgFillPrice,
            sl_order.log[-1].time
    )