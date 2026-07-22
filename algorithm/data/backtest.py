import csv
import statistics
from marketSignals.indicator import calculate_ema, calculate_rsi

symbols = [
    "AAPL", "NVDA", "GOOGL",
    "MSFT", "META", "CRDO",
    "DELL", "INTC", "AMZN",
    "QQQ", "SPY", 
    "XLE", "GLD",
]

# -----------------------------
# SETTINGS
# -----------------------------
STARTING_CAPITAL = 1000
POSITION_PCT = 0.2
TP_PCT = 0.06
SL_PCT = 0.02
MAX_POSITIONS = 4

# -----------------------------
# LOAD CSV
# -----------------------------
def load_csv(filename):
    opens, highs, lows, closes = [], [], [], []

    with open(filename, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            opens.append(float(row["Open"]))
            highs.append(float(row["High"]))
            lows.append(float(row["Low"]))
            closes.append(float(row["Close"]))

    return opens, highs, lows, closes


# -----------------------------
# LOAD ALL DATA
# -----------------------------
data = {}
min_len = float("inf")

for symbol in symbols:
    try:
        o, h, l, c = load_csv(f"{symbol}_1h.csv")

        data[symbol] = {
            "open": o,
            "high": h,
            "low": l,
            "close": c,
            "ema50": calculate_ema(c, 50),
            "ema200": calculate_ema(c, 200),
            "rsi": calculate_rsi(c, 14)
        }

        min_len = min(min_len, len(c))

    except FileNotFoundError:
        print(f"{symbol} missing")


# -----------------------------
# PORTFOLIO STATE
# -----------------------------
capital = STARTING_CAPITAL
equity_curve = [capital]

positions = {}          # symbol -> position dict
trade_counts = {symbol: 0 for symbol in symbols} 
win_counts  = {symbol: 0 for symbol in symbols}   


# -----------------------------
# BACKTEST LOOP
# -----------------------------
for i in range(201, min_len):

    # 1. CLOSE POSITIONS
    for symbol in list(positions.keys()):

        pos = positions[symbol]
        low = data[symbol]["low"][i]
        high = data[symbol]["high"][i]

        # STOP LOSS
        if low <= pos["sl"]:
            pnl = (pos["sl"] - pos["entry"]) * pos["shares"]
            capital += pnl
            trade_counts[symbol] += 1  # ✅ count closed trade
            del positions[symbol]

        # TAKE PROFIT
        elif high >= pos["tp"]:
            pnl = (pos["tp"] - pos["entry"]) * pos["shares"]
            capital += pnl
            trade_counts[symbol] += 1  # ✅ count closed trade
            win_counts[symbol]    += 1  # ✅ count win
            del positions[symbol]

    # 2. ENTRY CHECK (WITH MAX POSITION LIMIT)
    for symbol in symbols:

        if symbol in positions:
            continue

        # ⛔ GLOBAL CAP
        if len(positions) >= MAX_POSITIONS:
            break

        o = data[symbol]["open"][i]
        c = data[symbol]["close"][i]

        ema50 = data[symbol]["ema50"][i - 1]
        ema200 = data[symbol]["ema200"][i - 1]
        rsi = data[symbol]["rsi"][i - 1]

        signal = (
            ema50 > ema200 and
            c > ema50 and
            rsi is not None and
            55 < rsi < 75
        )

        if signal:
            position_size = capital * POSITION_PCT
            shares = position_size / o

            positions[symbol] = {
                "entry": o,
                "shares": shares,
                "tp": o * (1 + TP_PCT),
                "sl": o * (1 - SL_PCT)
            }

    # 3. PORTFOLIO VALUE
    portfolio_value = capital

    for symbol, pos in positions.items():
        price = data[symbol]["close"][i]
        portfolio_value += (price - pos["entry"]) * pos["shares"]

    equity_curve.append(portfolio_value)


# -----------------------------
# METRICS
# -----------------------------
def max_drawdown(curve):
    peak = curve[0]
    mdd = 0

    for x in curve:
        peak = max(peak, x)
        mdd = max(mdd, (peak - x) / peak)

    return mdd * 100


def sharpe(curve, bars_per_day=6.5):
    daily = []
    step = int(bars_per_day)
    for i in range(step, len(curve), step):
        daily.append((curve[i] - curve[i - step]) / curve[i - step])
    return statistics.mean(daily) / statistics.stdev(daily) * (252 ** 0.5)


# -----------------------------
# RESULTS
# -----------------------------
ending = equity_curve[-1]

print("\n=== PORTFOLIO RESULTS ===")
print(f"Start:  {STARTING_CAPITAL:.2f}")
print(f"End:    {ending:.2f}")
print(f"Return: {(ending/STARTING_CAPITAL - 1)*100:.2f}%")
print(f"Sharpe: {sharpe(equity_curve):.2f}")
print(f"Max DD: {max_drawdown(equity_curve):.2f}%")

print("\n=== TRADES PER SYMBOL ===")
print(f"  {'SYMBOL':<8} {'TRADES':>7} {'WINS':>6} {'WIN RATE':>10}")
print(f"  {'-'*35}")
total_trades = 0
total_wins   = 0
for symbol, count in sorted(trade_counts.items(), key=lambda x: -x[1]):
    if count > 0:
        wins = win_counts[symbol]
        wr   = (wins / count) * 100
        print(f"  {symbol:<8} {count:>7} {wins:>6} {wr:>9.1f}%")
        total_trades += count
        total_wins   += wins
overall_wr = (total_wins / total_trades * 100) if total_trades > 0 else 0
print(f"  {'-'*35}")
print(f"  {'TOTAL':<8} {total_trades:>7} {total_wins:>6} {overall_wr:>9.1f}%")