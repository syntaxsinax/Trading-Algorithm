import pandas as pd
from pathlib import Path
from marketSignals.indicator import calculate_ema, calculate_rsi
from data.database.tradeRepo import insertTrade

# ----------------------------------
# SETTINGS
# ----------------------------------

symbols = [
    "AAPL", "NVDA", "GOOGL",
    "MSFT", "META", "CRDO",
    "DELL", "INTC", "AMZN",
    "QQQ", "SPY",
    "XLE", "GLD"
]

TP_PCT = 0.06
SL_PCT = 0.02
BASE_DIR = Path(__file__).resolve().parent.parent
total_samples = 0
wins = 0
losses = 0


# ----------------------------------
# LOAD CSV
# ----------------------------------

def load_csv(filename):
    return pd.read_csv(filename)


# ----------------------------------
# ADD INDICATORS
# ----------------------------------

def add_indicators(df):

    closes = df["Close"].tolist()

    ema50 = calculate_ema(closes, 50)
    ema200 = calculate_ema(closes, 200)
    rsi = calculate_rsi(closes, 14)

    df["EMA50"] = ema50
    df["EMA200"] = ema200

    # Pad RSI to match dataframe length
    if len(rsi) < len(df):
        rsi = [None] * (len(df) - len(rsi)) + rsi

    df["RSI"] = rsi

    return df


# ----------------------------------
# BUILD DATASET
# ----------------------------------


for symbol in symbols:

    print(f"Processing {symbol}...")
    csv_file = BASE_DIR / f"{symbol}_1h.csv"

    try:
        df = load_csv(csv_file)
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        raise

    df = add_indicators(df)

    for i in range(201, len(df)):

        signal = (
            df["EMA50"][i - 1] > df["EMA200"][i - 1]
            and df["Close"][i - 1] > df["EMA50"][i - 1]
            and df["RSI"][i - 1] is not None
            and 55 < df["RSI"][i - 1] < 75
        )

        if not signal:
            continue

        entry = df["Open"][i]

        tp = entry * (1 + TP_PCT)
        sl = entry * (1 - SL_PCT)

        outcome = None
        exit_price = None
        exit_date = None

        # Simulate the trade exactly like the backtest
        for j in range(i + 1, len(df)):

            if df["Low"][j] <= sl:
                outcome = 0
                exit_price = sl
                exit_date = df["Datetime"][j]
                break

            if df["High"][j] >= tp:
                outcome = 1
                exit_price = tp
                exit_date = df["Datetime"][j]
                break

        # Ignore unfinished trades
        if outcome is None:
            continue

        insertTrade({
            "symbol": symbol,
            "entry_date": pd.to_datetime(df["Datetime"][i]).to_pydatetime(),
            "ema50": float(df["EMA50"][i]),
            "ema200": float(df["EMA200"][i]),
            "rsi": float(df["RSI"][i]),
            "volume": int(df["Volume"][i]),
            "sentiment": None,
            "entry_price": float(entry),
            "outcome": int(outcome)
        })
        total_samples += 1

        if outcome == 1:
            wins += 1
        else:
            losses += 1


# ----------------------------------
# SAVE DATASET
# ----------------------------------
print("\nDataset imported successfully!")
print(f"Total trades inserted: {total_samples}")
print(f"Wins: {wins}")
print(f"Losses: {losses}")