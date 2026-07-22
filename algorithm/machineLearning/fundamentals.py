import requests
import csv
import os
from datetime import datetime

LOGFILE = "trade_log.csv"
APIKEY = "your_free_key_here"

symbols = ["AAPL", "NVDA", "GOOGL", 
           "MSFT", "META", "CRDO", 
           "DELL", "INTC", "AMZN", 
           "QQQ", "SPY", 
           "GLD",  "XLE" ]

def get_tickerSentiment():
    url ="https://www.alphavantage.co/query"
    params ={
        "function": "NEWS_SENTIMENT",
        "tickers": {symbols},
        "apikey": APIKEY
    }
    data = requests.get(url, params=params).json()
    articles = data.get("feed", [])
    return [
        {"headline": a["title"], "sentiment": float(a["overall_sentiment_score"])}
        for a in articles
    ]


def log_sentiment(ticker, avg_sentiment):
    file_exists = os.path.isfile(LOGFILE)
    with open(LOGFILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "ticker", "avg_sentiment", "trade_result"])
        writer.writerow([datetime.now(), ticker, avg_sentiment, ""])


sentiment_data = get_tickerSentiment({symbols})
avg_sentiment = sum(a["sentiment"] for a in sentiment_data) / len(sentiment_data)
log_sentiment({symbols}, avg_sentiment)