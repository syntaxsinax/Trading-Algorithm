from ib_insync import IB, Stock, Index
from .ibkr import connect_ibkr, get_bars
import time
from marketSignals.indicator import calculate_ema, calculate_rsi
from marketSignals.strategy import check_entry
# --------------------------
# SETTINGS
# --------------------------
symbols = ["AAPL", "NVDA", "GOOGL", 
           "MSFT", "META", "CRDO", 
           "DELL", "INTC", "AMZN", 
           "QQQ", "SPY", 
           "GLD",  "XLE" ]
poll_interval   = 60 * 60
TAKE_PROFIT_PCT = 0.06   
STOP_LOSS_PCT   = 0.02   
POSITION_PCT    = 0.02   
MAX_POSITIONS   = 4    
MAX_DAILY_TRADES = 3
daily_trade_count = 0

# --------------------------
# CONNECT TO IBKR
# --------------------------
ib = connect_ibkr(client_id=1)
print("Connected to IBKR")

# --------------------------
# FETCH ACCOUNT VALUE
# --------------------------
def get_account_value():
    account = ib.managedAccounts()[0]
    summary = ib.accountSummary(account)
    for item in summary:
        if item.tag == 'NetLiquidation' and item.currency == 'GBP':
            return float(item.value)
    return None


# --------------------------
# NO OVERTRADING!!!!!!1!!!!!
#---------------------------
from datetime import date
from datetime import datetime, time
import pytz # type: ignore
last_trade_date = None 
# --------------------------
# MAIN LOOP
# --------------------------
while True:
    today = date.today()
    if last_trade_date != today:
        daily_trade_count = 0
        last_trade_date = today
        print("Daily trade counter reset.")

    
    et = pytz.timezone('US/Eastern')
    now = datetime.now(et)
    market_open = now.weekday() < 5 and time(9, 30) <= now.time() <= time(16, 0)
    print(f"Time (UTC): {now.strftime('%H:%M')} | Market open: {market_open}")

    if not market_open:
        print("Market closed, sleeping 5 minutes...")
        ib.sleep(300)
        continue

    print("\n--- Checking market ---")

    # Current IBKR open positions
    ib_positions = {p.contract.symbol: p.position for p in ib.positions()}
    print("Current IBKR positions:", ib_positions)

    # ENFORCE MAX POSITION CAP
    open_count = sum(1 for v in ib_positions.values() if v > 0)
    if open_count >= MAX_POSITIONS:
        print(f"Max positions ({MAX_POSITIONS}) reached, skipping entries.")
        print(f"\nSleeping {poll_interval}s...\n")
        ib.sleep(poll_interval)
        continue

    # Fetch account value for position sizing
    account_value = get_account_value()
    if account_value is None:
        print("⚠️ Could not fetch account value, skipping cycle.")
        ib.sleep(poll_interval)
        continue
    print(f"Account value: ${account_value:,.2f}")

    for symbol in symbols:

        # ✅ re-check cap inside loop as positions fill
        open_count = sum(1 for v in ib_positions.values() if v > 0)
        if open_count >= MAX_POSITIONS:
            print(f"Max positions reached mid-loop, stopping entries.")
            break

        print(f"\nChecking {symbol}...")
        
        contract = Stock(symbol, 'SMART', 'USD')

        # ---------------- QUALIFY CONTRACT ----------------
        try:
            ib.qualifyContracts(contract)
        except Exception as e:
            print(f"Skipping {symbol}: {e}")
            continue

        # ---------------- FETCH DATA ----------------
        try:
            bars = get_bars(ib, symbol, duration='90 D', bar_size='1 hour')

        except Exception as e:
            print(f"Skipping {symbol}: {e}")
            continue

        if len(bars) < 200:
            print(f"Not enough data for {symbol}")
            continue

        closes = [b.close for b in bars]

        # ---------------- INDICATORS (for debug only) ----------------
        ema50  = calculate_ema(closes, 50)
        ema200 = calculate_ema(closes, 200)
        rsi    = calculate_rsi(closes, 14)

        print(f"""
{symbol} STATS:
  Close(prev):  {closes[-2]}
  EMA50(prev):  {ema50[-2]}
  EMA200(prev): {ema200[-2]}
  RSI(prev):    {rsi[-2]}
""")

        # ---------------- POSITION CHECK ----------------
        in_position = symbol in ib_positions and ib_positions[symbol] > 0
        print(f"In position: {in_position}")

        # ---------------- SIGNAL ----------------
        signal = check_entry(
            [b.open for b in bars],
            [b.high for b in bars],
            [b.low  for b in bars],
            closes
        )
        print(f"Signal: {signal}")


        # ---------------- ENTRY ----------------
        if signal and not in_position:
            if daily_trade_count >= MAX_DAILY_TRADES:
                print("Daily trade limit reached, skipping.")
                break

            print(f"ENTRY INITIATED FOR {symbol}")
            entry_price = round(closes[-1], 2)

            if entry_price is None or entry_price != entry_price:
                print("⚠️ No valid price, skipping.")
                continue

            # ✅ position sizing aligned with backtest
            position_size = account_value * POSITION_PCT
            shares        = int(position_size / entry_price)  # whole shares only

            if shares < 1:
                print(f"⚠️ Position size too small for {symbol}, skipping.")
                continue

            tp_price = round(entry_price * (1 + TAKE_PROFIT_PCT), 2)
            sl_price = round(entry_price * (1 - STOP_LOSS_PCT),   2)

            if not (tp_price > entry_price > sl_price):
                print("❌ Invalid bracket pricing")
                continue

            print(f"  Entry: {entry_price} | Shares: {shares} | TP: {tp_price} | SL: {sl_price}")

            # BRACKET ORDER
            bracket = ib.bracketOrder(
                action          = 'BUY',
                quantity        = shares,
                limitPrice      = entry_price,
                takeProfitPrice = tp_price,
                stopLossPrice   = sl_price,
                tif             = 'GTC'
            )

            for o in bracket:
                ib.placeOrder(contract, o)

            ib.sleep(1)

            # update local position count so cap is respected mid-loop
            ib_positions[symbol] = shares
            daily_trade_count += 1
            print(f"✅ ORDER PLACED FOR {symbol}")

    print(f"\nSleeping {poll_interval}s...\n")
    ib.sleep(poll_interval)