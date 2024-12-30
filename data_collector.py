import yfinance as yf
import pandas as pd

def request_data_yfinance(target, period, interval):
    print("Collecting Data...")
    try:
        ticker = yf.Ticker(target)
        closing_prices = ticker.history(period=period, interval=interval)[["Close"]]
        print(closing_prices.head())
        closing_prices.index = pd.to_datetime(closing_prices.index.strftime("%Y-%m-%d"))

        print("Data Received")
        print("\n-------------------------------------\n")
        print(closing_prices.head())
        print("\n-------------------------------------\n")

        closing_prices.to_csv(f"{target}_{period}_{interval}_closing_prices.csv")
    except Exception as e:
        print(f"An error found: {e}")

# request_data_yfinance("USDCHF=X", "5y", "1d")


