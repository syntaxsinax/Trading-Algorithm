import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from data.database.db import engine
import joblib


query = """SELECT ema50, ema200, rsi, volume, sentiment, outcome
           FROM trades"""

df = pd.read_sql(query, engine)
df = pd.read_csv("training_dataset.csv")
df["Sentiment"] = df["Sentiment"].fillna(0.0)


X = df[["EMA50", "EMA200", "RSI", "Volume", "Sentiment"
]]

y = df["Outcome"]

X_train, X_test, y_train, y_test = train_test_split(
    X,y,
    test_size= 0.2,
    shuffle=False
)

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(
    X_train, y_train
)

predictions = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, predictions))
print(df.head())
print(df.shape)
print(X.head())
print()
print(y.head())
joblib.dump(model,"trade_model.pkl")
print("Model Saved!")