import pandas as pd
from data_collector import request_data_yfinance
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from scipy.signal import find_peaks
import matplotlib.dates as mdates


def fourrier_transformation(df):
    df.index = pd.to_datetime(df.index)
    df["Days"] = (df.index - df.index.min()) / pd.Timedelta(days=1)

    fft_values = np.fft.fft(df["Close"])
    freq = np.fft.fftfreq(len(fft_values), d=1)
    power = np.abs(fft_values)

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(df['Days'], df['Close'], label='Original Signal')
    plt.title('Original Time Series Signal')
    plt.xlabel('Days')
    plt.ylabel('Value')
    plt.legend()
    plt.grid()

    # Plot Power Spectrum
    plt.subplot(2, 1, 2)
    plt.plot(freq[:len(freq)//2], power[:len(power)//2], label='Power Spectrum', color='red')
    plt.title('Fourier Transform - Power Spectrum')
    plt.xlabel('Frequency (1/Days)')
    plt.ylabel('Power')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.savefig("fft_analysis.png")


def linear_regression_analysis(df):
    df.index = pd.to_datetime(df.index)
    df["Days"] = (df.index - df.index.min()) / pd.Timedelta(days=1)
    X = df["Days"].values.reshape(-1, 1)
    y = df["Close"]

    model = LinearRegression()
    model.fit(X, y)

    df["trend"] = model.predict(X)
    df[["Close", "trend"]].plot(legend=True)
    plt.savefig("linear_reg_analysis.png")


def rolling_mean_analysis(df, window_size=30):
    df["rolling_mean"] = df["Close"].rolling(window=window_size).mean()
    df.plot(legend=True)
    plt.savefig("rolling_mean.png")


def exchange_viability(df):
    three_year_mean = df["Close"][-750:].mean()
    if df["Close"].iloc[-1] < three_year_mean:
        print("Time to go all-in on dollar")
    else:
        print("Stay put solider")
    peaks, _ = find_peaks(df["Close"])
    print(peaks)
    df.plot()
    plt.axhline(y=three_year_mean, color='red', linestyle='--', label='Three Year Average')
    plt.savefig("exchange_viability_graph.png")


def analyze_exchange_rate(df, window_size=70):
    df["rolling_mean"] = df["Close"].rolling(window=window_size).mean()
    df = df[-750:]
    df["good_period"] = np.where(df["rolling_mean"] > df["Close"], True, False)
    df["mean2close_ratio"] = df["rolling_mean"] / df["Close"]

    plt.figure(figsize=(16, 9))
    plt.plot(df.index, df["Close"], label="USD/CHF=X")
    plt.plot(df.index, df["rolling_mean"], label=f"Rolling Mean {window_size}")
    plt.plot(df.index, df["mean2close_ratio"], label="mean2close_ratio")
    plt.axhline(y=1, color='red', linestyle='--', label='mean2close_standard')


    prev, start, end = False, None, None
    for index, info in df.iterrows():
        if info["good_period"]:
            if not prev:
                start = index
            else:
                continue
        else:
            if not prev:
                continue
            else:
                end = index
        if prev and not info["good_period"]:
            plt.axvspan(start, end, color="grey", alpha=0.3)
        prev = info["good_period"]
    plt.legend()
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1))
    plt.xticks(rotation=45)
    plt.savefig("ex_rate.png")

def main():
    target = "USDCHF=X"
    period = "5y"
    interval = "1d"
    filenames = os.listdir(".")
    target = f"{target}_{period}_{interval}_closing_prices.csv"
    if target not in filenames:
        request_data_yfinance()

    df = pd.read_csv(target, index_col="Date")
    # exchange_viability(df)
    analyze_exchange_rate(df)

if __name__ == "__main__":
    main()