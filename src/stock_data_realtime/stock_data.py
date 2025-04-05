import datetime
import enum
import json
import logging
import random
import re
import string
import os
import time
from typing import Optional

import pandas as pd
from websocket import create_connection
import requests

logger = logging.getLogger(__name__)


class Interval(enum.Enum):
    in_5_seconds = "5S"
    in_1_minute = "1"
    in_3_minute = "3"
    in_5_minute = "5"
    in_15_minute = "15"
    in_30_minute = "30"
    in_45_minute = "45"
    in_1_hour = "1H"
    in_2_hour = "2H"
    in_3_hour = "3H"
    in_4_hour = "4H"
    in_daily = "1D"
    in_weekly = "1W"
    in_monthly = "1M"


class TvDatafeed:
    __sign_in_url = "https://www.tradingview.com/accounts/signin/"
    __search_url = "https://symbol-search.tradingview.com/symbol_search/?text={}&hl=1&exchange={}&lang=en&type=&domain=production"
    __ws_headers = json.dumps({"Origin": "https://data.tradingview.com"})
    __signin_headers = {"Referer": "https://www.tradingview.com"}
    __ws_timeout = 5
    __token_file = "tv_token.json"

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        sessionid: Optional[str] = None,
        sessionid_sign: Optional[str] = None,
    ) -> None:
        self.username = username
        self.password = password
        self.sessionid = sessionid
        self.sessionid_sign = sessionid_sign
        self.ws_debug = False
        self.token = self.__load_token()
        if not self.token:
            self.token = self.__auth()
        self.ws = None
        self.session = self.__generate_session()
        self.chart_session = self.__generate_chart_session()

    def __auth(self):
        # Check if we have session cookies
        if self.sessionid and self.sessionid_sign:
            return self.__auth_with_session()
        # Fall back to username/password
        elif self.username and self.password:
            return self.__auth_with_credentials()
        else:
            logger.warning(
                "No valid credentials or session cookies provided. Using unauthorized access."
            )
            return "unauthorized_user_token"

    def __auth_with_session(self):
        headers = {
            "Referer": "https://www.tradingview.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Cookie": f"sessionid={self.sessionid}; sessionid_sign={self.sessionid_sign}",
        }

        try:
            response = requests.get(
                "https://www.tradingview.com/chart/",
                headers=headers,
                allow_redirects=False,
            )
            if response.status_code == 302:
                redirect_url = response.headers.get("Location")
                response = requests.get(
                    f"https://www.tradingview.com{redirect_url}", headers=headers
                )
            response.raise_for_status()

            match = re.search(r'"auth_token":"([^"]+)"', response.text)
            if match:
                token = match.group(1)
                self.__save_token(token)
                logger.info("Authentication successful with session cookies.")
                return token
            else:
                logger.error("Failed to extract auth token from response.")
                return "unauthorized_user_token"

        except requests.exceptions.RequestException as e:
            logger.error(f"Error during session authentication: {e}")
            return "unauthorized_user_token"

    def __auth_with_credentials(self):
        data = {"username": self.username, "password": self.password, "remember": "on"}
        try:
            response = requests.post(
                url=self.__sign_in_url, data=data, headers=self.__signin_headers
            )
            response.raise_for_status()

            try:
                json_response = response.json()
                if "user" in json_response and "auth_token" in json_response["user"]:
                    token = json_response["user"]["auth_token"]
                    self.__save_token(token)
                    logger.info("Authentication successful with credentials.")
                    return token
                else:
                    logger.error("Unexpected response format during authentication.")
                    return "unauthorized_user_token"
            except json.JSONDecodeError:
                logger.error("Failed to parse authentication response as JSON.")
                return "unauthorized_user_token"

        except requests.exceptions.RequestException as e:
            logger.error(f"Error during credentials authentication: {e}")
            return "unauthorized_user_token"

    def __save_token(self, token):
        data = {
            "token": token,
            "expiry": (
                datetime.datetime.now() + datetime.timedelta(days=30)
            ).isoformat(),
        }
        with open(self.__token_file, "w") as f:
            json.dump(data, f)
        logger.info("Token saved successfully.")

    def __load_token(self):
        if not os.path.exists(self.__token_file):
            return None

        with open(self.__token_file, "r") as f:
            data = json.load(f)

        expiry = datetime.datetime.fromisoformat(data["expiry"])
        if expiry > datetime.datetime.now():
            logger.info("Loaded saved token.")
            return data["token"]
        else:
            logger.info("Saved token has expired.")
            os.remove(self.__token_file)
            return None

    def __create_connection(self):
        for attempt in range(3):
            try:
                logging.debug(f"Creating websocket connection (attempt {attempt + 1})")
                self.ws = create_connection(
                    "wss://data.tradingview.com/socket.io/websocket",
                    headers=self.__ws_headers,
                    timeout=self.__ws_timeout,
                )
                logger.debug("WebSocket connection established successfully")
                return
            except Exception as e:
                logger.error(f"Failed to establish WebSocket connection: {e}")
                if attempt < 2:
                    time.sleep(2)
        raise ConnectionError(
            "Failed to establish WebSocket connection after 3 attempts"
        )

    @staticmethod
    def __filter_raw_message(text):
        try:
            found = re.search('"m":"(.+?)",', text).group(1)
            found2 = re.search('"p":(.+?"}"])}', text).group(1)
            return found, found2
        except AttributeError:
            logger.error("Error in filter_raw_message")

    @staticmethod
    def __generate_session():
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(stringLength))
        return "qs_" + random_string

    @staticmethod
    def __generate_chart_session():
        stringLength = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters) for i in range(stringLength))
        return "cs_" + random_string

    @staticmethod
    def __prepend_header(st):
        return "~m~" + str(len(st)) + "~m~" + st

    @staticmethod
    def __construct_message(func, param_list):
        return json.dumps({"m": func, "p": param_list}, separators=(",", ":"))

    def __create_message(self, func, paramList):
        return self.__prepend_header(self.__construct_message(func, paramList))

    def __send_message(self, func, args):
        m = self.__create_message(func, args)
        if self.ws_debug:
            print(m)
        self.ws.send(m)

    @staticmethod
    def __create_df(raw_data, symbol):
        try:
            out = re.search('"s":\[(.+?)\}\]', raw_data).group(1)
            x = out.split(',{"')
            data = list()
            volume_data = True

            for xi in x:
                xi = re.split("\[|:|,|\]", xi)
                timestamp = float(xi[4])
                dt = datetime.datetime.fromtimestamp(timestamp)
                date = dt.date()
                time = dt.time()

                row = [date, time]

                for i in range(5, 10):
                    # skip converting volume data if does not exist
                    if not volume_data and i == 9:
                        row.append(0.0)
                        continue
                    try:
                        row.append(float(xi[i]))
                    except ValueError:
                        volume_data = False
                        row.append(0.0)
                        logger.debug("No volume data")

                data.append(row)

            data = pd.DataFrame(
                data, columns=["Date", "Time", "Open", "High", "Low", "Close", "Volume"]
            )
            data["Date"] = pd.to_datetime(data["Date"])
            data["Time"] = pd.to_datetime(data["Time"], format="%H:%M:%S").dt.time
            data.set_index("Date", inplace=True)
            data.insert(0, "symbol", value=symbol)
            return data
        except AttributeError:
            logger.error("No data, please check the exchange and symbol")

    @staticmethod
    def __format_symbol(symbol, exchange, contract: int = None):
        if ":" in symbol:
            return symbol
        elif contract is None:
            return f"{exchange}:{symbol}"
        elif isinstance(contract, int):
            return f"{exchange}:{symbol}{contract}!"
        else:
            raise ValueError("Not a valid contract")

    def get_hist(
        self,
        symbol: str,
        exchange: str = "NSE",
        interval: Interval = Interval.in_daily,
        n_bars: int = 5000,
        fut_contract: int = None,
        extended_session: bool = False,
    ) -> pd.DataFrame:
        if self.token == "unauthorized_user_token":
            logger.warning("Using unauthorized access, data may be limited")

        backadjustment: bool = False
        if symbol.endswith("!A"):
            backadjustment = True
            symbol = symbol.replace("!A", "!")

        symbol = self.__format_symbol(
            symbol=symbol, exchange=exchange, contract=fut_contract
        )

        interval = interval.value

        self.__create_connection()

        self.__send_message("set_auth_token", [self.token])
        self.__send_message("chart_create_session", [self.chart_session, ""])
        self.__send_message("quote_create_session", [self.session])
        self.__send_message(
            "quote_set_fields",
            [
                self.session,
                "ch",
                "chp",
                "current_session",
                "description",
                "local_description",
                "language",
                "exchange",
                "fractional",
                "is_tradable",
                "lp",
                "lp_time",
                "minmov",
                "minmove2",
                "original_name",
                "pricescale",
                "pro_name",
                "short_name",
                "type",
                "update_mode",
                "volume",
                "currency_code",
                "rchp",
                "rtc",
            ],
        )

        self.__send_message(
            "quote_add_symbols", [self.session, symbol, {"flags": ["force_permission"]}]
        )
        self.__send_message("quote_fast_symbols", [self.session, symbol])

        self.__send_message(
            "resolve_symbol",
            [
                self.chart_session,
                "symbol_1",
                '={"symbol":"'
                + symbol
                + '","adjustment":"splits"'
                + ("" if not backadjustment else ',"backadjustment":"default"')
                + ',"session":'
                + ('"regular"' if not extended_session else '"extended"')
                + "}",
            ],
        )

        self.__send_message(
            "create_series",
            [self.chart_session, "s1", "s1", "symbol_1", interval, n_bars],
        )

        self.__send_message("switch_timezone", [self.chart_session, "exchange"])

        raw_data = ""

        logger.debug(f"Getting data for {symbol}...")
        while True:
            try:
                result = self.ws.recv()
                raw_data = raw_data + result + "\n"
            except Exception as e:
                logger.error(e)
                break

            if "series_completed" in result:
                break

        return self.__create_df(raw_data, symbol)

    def search_symbol(self, text: str, exchange: str = "", type: str = None):
        """
        Search for symbols on TradingView.
        
        Args:
            text (str): Search query
            exchange (str, optional): Exchange to filter by
            type (str, optional): Asset type (e.g., stock, futures, crypto)
        
        Returns:
            list: List of symbol dictionaries
        """
        url = "https://symbol-search.tradingview.com/symbol_search"
        params = {"text": text}
        if exchange:
            params["exchange"] = exchange
        if type:
            params["type"] = type
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.tradingview.com",
            "Origin": "https://www.tradingview.com",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}" if self.token else None
        }
        
        cookies = {"sessionid": self.sessionid, "sessionid_sign": self.sessionid_sign} if (self.sessionid and self.sessionid_sign) else {}
        resp = requests.get(url, params=params, headers=headers, cookies=cookies)  # Changed to GET
        
        symbols_list = []
        try:
            resp.raise_for_status()
            symbols_list = json.loads(resp.text.replace("</em>", "").replace("<em>", ""))
            logger.debug(f"Search successful for '{text}' on '{exchange}'")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error during symbol search: {e} - Response: {resp.text}")
        except Exception as e:
            logger.error(f"Error during symbol search: {e}")
        
        return symbols_list

if __name__ == "__main__":
    import json

    logging.basicConfig(level=logging.DEBUG)

    with open("config.json", "r") as f:
        config = json.load(f)

    # Example with session cookies
    tv_session = TvDatafeed(
        sessionid=config["sessionid"], sessionid_sign=config["sessionid_sign"]
    )

    # Example with username/password
    tv_credentials = TvDatafeed(username=config["username"], password=["password"])

    try:
        # Using session-based authentication
        data = tv_session.get_hist(
            "NQ1!", "CME_MINI", interval=Interval.in_5_seconds, n_bars=10
        )
        print("Session-based data:")
        print(data)

        # Using credentials-based authentication
        data = tv_credentials.get_hist(
            "NQ1!", "CME_MINI", interval=Interval.in_5_seconds, n_bars=10
        )
        print("Credentials-based data:")
        print(data)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
