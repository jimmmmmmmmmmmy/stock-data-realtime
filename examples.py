import json
import logging
from stock_data import TvDatafeed, Interval

try:
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}
    print(
        "Warning: config.json not found, some examples may fail if authentication is required"
    )


def search():
    """Simple example showing symbol search with authentication"""
    try:
        tv_session = TvDatafeed(
            sessionid=config.get("sessionid"),
            sessionid_sign=config.get("sessionid_sign"),
        )
        symbol = input("Search for symbol: ")
        results = tv_session.search_symbol(symbol)
        print(f"Search results for {symbol}")
        print(json.dumps(results[:1], indent=2))
    except Exception as e:
        print(f"An error occurred while searching: {e}")


def data():
    """Basic example getting daily data (uses saved token or credentials)"""
    try:
        tv_session = TvDatafeed(
            username=config.get("username"), password=config.get("password")
        )
        symbol = input("Enter symbol: ")
        exchange = input("Enter exchange: ")
        df = tv_session.get_hist(
            symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=5
        )
        print(f"Daily data for {exchange}:{symbol}")
        print(df)
    except Exception as e:
        print(f"An error occurred while fetching data: {e}")


if __name__ == "__main__":

    search()

    data()
