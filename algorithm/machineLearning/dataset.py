import pandas as pd
from marketSignals.indicator import calculate_ema, calculate_rsi

# ----------------------------------
# SETTINGS
# ----------------------------------

symbols = [
    "AAPL", "NVDA", "GOOGL",
    "MSFT", "META", "CRDO",
    "DELL", "INTC", "AMZN",
    "^GSPC", "QQQ", "SPY",
    "XLE", "GLD"
]

TP_PCT = 0.06
SL_PCT = 0.02


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

    df["EMA50"] = calculate_ema(closes, 50)
    df["EMA200"] = calculate_ema(closes, 200)
    df["RSI"] = calculate_rsi(closes, 14)

    return df


# ----------------------------------
# BUILD DATASET
# ----------------------------------

dataset = []

for symbol in symbols:

    print(f"Processing {symbol}...")

    try:
        df = load_csv(f"{symbol}_1h.csv")
    except FileNotFoundError:
        print(f"{symbol}_1h.csv not found")
        continue

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

        dataset.append({
            "Symbol": symbol,
            "Entry_Date": df["Datetime"][i],
            "Exit_Date": exit_date,
            "Entry": entry,
            "Exit": exit_price,
            "EMA50": df["EMA50"][i],
            "EMA200": df["EMA200"][i],
            "RSI": df["RSI"][i],
            "Volume": df["Volume"][i],
            "Outcome": outcome
        })


# ----------------------------------
# SAVE DATASET
# ----------------------------------

dataset = pd.DataFrame(dataset)

dataset.to_csv("training_dataset.csv", index=False)

print("\nDataset created successfully!")
print(dataset.head())
print(f"\nTotal samples: {len(dataset)}")