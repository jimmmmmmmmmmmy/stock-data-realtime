# Stock Data Realtime

A way to scrape data from TradingView since they don't provide an official API and I'm already paying for market data from the CME, NYSE, and Nasdaq exchange

## Features

- Fetch near real-time and historical market data
- Support for multiple timeframes (from 5 seconds to monthly)
- Ability to search for symbols across different exchanges
- Pandas DataFrame output

## Required Libraries
This script relies on the following Python libraries

- pandas: For data manipulation and analysis
- websocket-client: For WebSocket connections
- requests: For making HTTP requests


## Installation
- **Poetry**: Run `poetry install` to install the package and dependencies
  
- **Pip**: Run `pip install .` to install the package and dependencies via `pyproject.toml`.

## Usage

The main script is `stock_data.py`. Here are some examples of how to use it:

### Basic Usage

```python
from stock_data_realtime import TvDatafeed, Interval

# Initialize the TvDatafeed (unauthorized access)
tv = TvDatafeed()

# Get historical data
data = tv.get_hist("NQ1!", "CME_MINI", interval=Interval.in_daily,
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
data = tv.get_hist("AAPL", "NASDAQ", interval=Interval.in_daily, n_bars=1000)

# Get data with extended trading hours
data = tv.get_hist("MSFT", "NASDAQ", interval=Interval.in_1_hour, n_bars=500, extended_session=True)
```

### Authenticated Access

For extended data access, you can provide your TV session cookies. You can also use your username and password, but it won't be as for seemless data retrieval and you may run into captcha issues.

```python
tv = TvDatafeed(
    sessionid="your_session_id",
    sessionid_sign="your_session_id_sign"
    
)

data = tv.get_hist("NQ1!", "CME_MINI", interval=Interval.in_5_seconds,
                           n_bars=10)

print(data) 
```

### config.json

Locally you'll need to create a file called config.json and in it store either your sessionid & sessionid_sign or username & password:

```
{
    "username": "your username here", 
    "password": "your password here",
    "sessionid": "your sessionid here",
    "sessionid_sign": "your sessionid_sign here"
}

```

Both username and password are the same login used for the main site while sessionid and sessionid need to be retrieved separately.

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

### Python's built-in 'Logging'

The script uses Python's `logging` module. By default, logging is set to the DEBUG level when the script is run directly. This should provide debugging info on:

- Authentication processes
- WebSocket connection attempts
- Data retrieval progress
- Any errors or warnings that occur during execution

The logging level can be adjusted in this part of the script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Or INFO, WARNING, ERROR, CRITICAL
```

### WebSocket Debugging

The TvDatafeed class includes a `ws_debug` attribute. By default is it set to false, but can be set to `True` to print out all WebSocket messages sent to TradingView:

```python
tv = TvDatafeed(sessionid="your_session_id", sessionid_sign="your_session_id_sign")
tv.ws_debug = True
```

This should be used to inspect raw communication between the script and TradingView's servers.

### Error Handling

If an error occurs during data retrieval, it can be caught and logged this way:

```python
try:
    data = tv.get_hist("NQ1!", "CME_MINI", interval=Interval.in_5_seconds, n_bars=10)
    display(data)
except Exception as e:
    logger.error(f"An error occurred: {e}")
```

