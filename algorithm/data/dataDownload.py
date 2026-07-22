import yfinance as yf

tickers = ["NVDA", "AAPL", "GOOGL", "MSFT", "META", "CRDO", "AMZN", "DELL", "INTC", "QQQ", "SPY", "XLE", "GLD"]

for t in tickers:
    print(f"Downloading {t}...")
    data = yf.download(
        t,
        period="730d",     
        interval="1h",
        prepost=False
    )

    data.columns = data.columns.get_level_values(0)
    data.to_csv(f"{t}_1h.csv")

print("All files downloaded correctly.")