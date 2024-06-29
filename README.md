# Stock Data Realtime

Stock Data Realtime is a Python script that allows you to fetch real-time and historical market data from
<p align="center">
  <img src="https://github.com/jimmmmmmmmmmmy/stock-data-realtime/assets/143036559/34367166-8c5a-4519-b8ca-35b872d80635" alt="Stock Data Realtime" width="300"/>
</p>


## Features

- Fetch real-time and historical data for stocks, futures, forex, and more
- Support for multiple timeframes (from 5 seconds to monthly)
- Ability to search for symbols across different exchanges
- Optional authentication for extended data access
- Pandas DataFrame output for easy data manipulation and analysis

## Usage

The main script is `stock_data.py`. Here are some examples of how to use it:

### Basic Usage

```python
from stock_data import TvDatafeed, Interval

# Initialize the TvDatafeed (unauthorized access)
tv = TvDatafeed()

# Get historical data
data = tv.get_hist("AAPL", "NASDAQ", interval=Interval.in_daily, n_bars=100)
print(data)
```

### Fetching Data with Different Parameters

```python
# Get 5-second interval data for E-mini NASDAQ-100 futures
data = tv.get_hist("NQ1!", "CME_MINI", interval=Interval.in_5_seconds, n_bars=10)

# Get daily data for a stock:
data = tv.get_hist("AAPL!A", "NASDAQ", interval=Interval.in_daily, n_bars=1000)

# Get data with extended trading hours
data = tv.get_hist("MSFT", "NASDAQ", interval=Interval.in_1_hour, n_bars=500, extended_session=True)
```

### Authenticated Access

For extended data access, you can provide your TV session cookies. We use this instead of username and password authentication for a seemless data retrieval.

```python
tv = TvDatafeed(
    sessionid="your_session_id",
    sessionid_sign="your_session_id_sign"
)

data = tv.get_hist("NQ1!", "CME_MINI", interval=Interval.in_5_seconds,
                           n_bars=10)

print(data)
```

#### How to obtain your sessionid and sessionid_sign


https://github.com/jimmmmmmmmmmmy/stock-data-realtime/assets/143036559/29ccb8e3-e3bf-4018-ad1f-0440540482c9


