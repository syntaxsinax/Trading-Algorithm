import requests
import time

API_KEY = "YOUR_API_KEY"

symbols = ["AAPL", "NVDA", "GOOGL", 
           "MSFT", "META", "CRDO", 
           "DELL", "INTC", "AMZN", 
           "QQQ", "SPY", 
           "GLD",  "XLE" ]

def get_sentiment(symbol):

    url = (
        f"https://www.alphavantage.co/query?"
        f"function=NEWS_SENTIMENT"
        f"&tickers={symbol}"
        f"&apikey={API_KEY}"
    )

    response = requests.get(url)
    data = response.json()

    if "Information" in data:
        print(f"Rate limit reached for {symbol}")
        return None

    feed = data.get("feed", [])

    if not feed:
        return None

    scores = []

    for article in feed:

        for ticker in article.get("ticker_sentiment", []):

            if ticker["ticker"] == symbol:

                scores.append(
                    float(ticker["ticker_sentiment_score"])
                )

    if not scores:
        return None

    return sum(scores) / len(scores)


if __name__ == "__main__":
    for symbol in symbols:
        Sentiment = get_sentiment(symbol)
        print(f"Ticker: {symbol}, Sentiment: {Sentiment}")
        time.sleep(10)