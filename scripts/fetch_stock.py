import yfinance as yf
import pandas as pd
from scripts.competitors import COMPETITORS


def fetch_stock_data(company, period="1mo"):
    company_info = COMPETITORS.get(company)

    # 1️⃣ Company not found
    if not company_info:
        return pd.DataFrame(), None

    # 2️⃣ Not a public company
    if company_info.get("type") != "public":
        return pd.DataFrame(), None

    ticker_symbol = company_info.get("ticker")

    # 3️⃣ Missing or invalid ticker
    if not ticker_symbol:
        return pd.DataFrame(), None

    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period)
        recs = ticker.recommendations
        return hist, recs
    except Exception:
        # 4️⃣ Any API / network / data issue
        return pd.DataFrame(), None


def compute_sentiment(recommendations):
    if recommendations is None or recommendations.empty:
        return "Hold"

    summary = recommendations.iloc[-1]

    if summary.get("buy", 0) > summary.get("sell", 0):
        return "Buy"
    elif summary.get("sell", 0) > summary.get("buy", 0):
        return "Sell"
    else:
        return "Hold"


def compute_average_market_trend(stock_data_list):
    """
    Computes average closing price across multiple stocks
    """
    if not stock_data_list:
        return pd.Series(dtype=float)

    combined = pd.concat(
        [df["Close"].rename(f"c{i}") for i, df in enumerate(stock_data_list)],
        axis=1
    )

    return combined.mean(axis=1)

