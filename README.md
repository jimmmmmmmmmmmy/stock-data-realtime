# Stock Data Realtime

Stock Data Realtime is a Python script that allows you to fetch real-time and historical market data from
<p align="center">
  <img src="https://github.com/jimmmmmmmmmmmy/stock-data-realtime/assets/143036559/34367166-8c5a-4519-b8ca-35b872d80635" alt="Stock Data Realtime" width="300"/>
</p>


## Features

- Fetch near real-time and historical market data
- Support for multiple timeframes (from 5 seconds to monthly)
- Ability to search for symbols across different exchanges
- Optional authentication for their paid data features
- Pandas DataFrame output for easy data manipulation and analysis

## Required Libraries
This script relies on the following Python libraries

- pandas: For data manipulation and analysis
- websocket-client: For WebSocket connections
- requests: For making HTTP requests

## Usage

The main script is `stock_data.py`. Here are some examples of how to use it:

### Basic Usage

```python
from stock_data import TvDatafeed, Interval

# Initialize the TvDatafeed (unauthorized access)
tv = TvDatafeed()

# Get historical data
data = tv.get_hist("NQ1!", "CME_MINI", interval=Interval.in_5_seconds,
                           n_bars=10)
print(data)

# Returns: ["Date", "Time", "Open", "High", "Low", "Close", "Volume"]
```

<img width="637" alt="Screenshot 2024-06-29 at 10 02 04 AM" src="https://github.com/jimmmmmmmmmmmy/stock-data-realtime/assets/143036559/af642f31-de80-4273-915f-479c3496318d">

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

# print(data) or display(data)
```

#### How to obtain your sessionid and sessionid_sign


https://github.com/jimmmmmmmmmmmy/stock-data-realtime/assets/143036559/29ccb8e3-e3bf-4018-ad1f-0440540482c9


#### Token Management

The script manages authentication tokens automatically, saving them to a file (`tv_token.json`) and reusing them when possible. You can inspect this file to see the current token and its expiry date.

The `tv_token.json` file contains two key items:
1. `token`: The current authentication token.
2. `expiry`: The expiration date and time of the token.

Example structure of `tv_token.json`:
```json
{
    "token": "ABCDEFGHUIDFH(*#HR(OHN#IUOHF*&(#F@HIULFHSELIUFHDFJIUYH#*(O&FYGHILEDFufghsdiufg2o387f...",
    "expiry": "2024-07-27T22:45:36.629250"
}
```

By storing the token in a json file, we're able to reduce the number of authentication requests. The script will automatically refresh the token when it expires.

#

# Debugging:

The TvDatafeed class includes several debugging features to help you troubleshoot issues and gain insights into the data retrieval process:

### Logging

The script uses Python's built-in `logging` module to provide detailed information about its operations. By default, logging is set to the DEBUG level when the script is run directly. This gives you visibility into:

- Authentication processes
- WebSocket connection attempts
- Data retrieval progress
- Any errors or warnings that occur during execution

You can adjust the logging level as needed in your own scripts:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Or INFO, WARNING, ERROR, etc.
```

### WebSocket Debugging

The TvDatafeed class includes a `ws_debug` attribute that you can set to `True` to print out all WebSocket messages sent to TradingView:

```python
tv = TvDatafeed(sessionid="your_session_id", sessionid_sign="your_session_id_sign")
tv.ws_debug = True
```

This can be particularly useful when you need to inspect the raw communication between the script and TradingView's servers.

### Error Handling

The script includes robust error handling and logging. If an error occurs during data retrieval, it will be caught and logged. For example:

```python
try:
    data = tv.get_hist("NQ1!", "CME_MINI", interval=Interval.in_5_seconds, n_bars=10)
    display(data)
except Exception as e:
    logger.error(f"An error occurred: {e}")
```

This structure allows you to catch and handle any exceptions that might occur during the data retrieval process.

