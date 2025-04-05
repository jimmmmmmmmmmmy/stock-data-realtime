import unittest
from unittest.mock import Mock, patch, mock_open
import pandas as pd
import json
import datetime
from src.stock_data_realtime.stock_data import TvDatafeed, Interval

class TestTvDatafeed(unittest.TestCase):
    def setUp(self):
        self.tv_datafeed = TvDatafeed(
            username="test_user",
            password="test_pass",
            sessionid="test_session",
            sessionid_sign="test_session_sign"
        )
        self.mock_config = {
            "username": "test_user",
            "password": "test_pass",
            "sessionid": "test_session",
            "sessionid_sign": "test_session_sign"
        }

    # Test initialization
    def test_init_with_credentials(self):
        """Confirm TvDatafeed class does basic object initialization."""
        self.assertEqual(self.tv_datafeed.username, "test_user")
        self.assertEqual(self.tv_datafeed.password, "test_pass")
        self.assertEqual(self.tv_datafeed.sessionid, "test_session")
        self.assertEqual(self.tv_datafeed.sessionid_sign, "test_session_sign")

    # Test token management
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, 
           read_data='{"token": "test_token", "expiry": "2025-12-31T00:00:00"}')
    def test_load_token_valid(self, mock_file, mock_exists):
        """Mocks a file with working token and verifies load token works."""
        token = self.tv_datafeed._TvDatafeed__load_token()
        self.assertEqual(token, "test_token")

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, 
           read_data='{"token": "test_token", "expiry": "2020-01-01T00:00:00"}')
    @patch('os.remove')
    def test_load_token_expired(self, mock_remove, mock_file, mock_exists):
        """Mocks a file with expired token and tests if token is removed."""
        token = self.tv_datafeed._TvDatafeed__load_token()
        self.assertIsNone(token)
        mock_remove.assert_called_once_with("tv_token.json")

    # Test session generation
    def test_generate_session(self):
        """Tests if generated session string is valid."""
        session = TvDatafeed._TvDatafeed__generate_session()
        self.assertTrue(session.startswith("qs_"))
        self.assertEqual(len(session), 15)  # "qs_" + 12 random chars

    def test_generate_chart_session(self):
        """Tests if chart session string is valid."""
        chart_session = TvDatafeed._TvDatafeed__generate_chart_session()
        self.assertTrue(chart_session.startswith("cs_"))
        self.assertEqual(len(chart_session), 15)

    # Test symbol formatting
    def test_format_symbol_basic(self):
        """Tests if format symbol works."""
        result = TvDatafeed._TvDatafeed__format_symbol("AAPL", "NASDAQ")
        self.assertEqual(result, "NASDAQ:AAPL")

    def test_format_symbol_with_contract(self):
        """Tests symbol formatting for futures contract."""
        result = TvDatafeed._TvDatafeed__format_symbol("ES", "CME", 1)
        self.assertEqual(result, "CME:ES1!")

    def test_format_symbol_already_formatted(self):
        """Tests preformatted symbols."""
        result = TvDatafeed._TvDatafeed__format_symbol("NASDAQ:AAPL", "NASDAQ")
        self.assertEqual(result, "NASDAQ:AAPL")

    # Test message construction
    def test_construct_message(self):
        """Validate websocket message construction."""
        func = "test_func"
        param_list = ["param1", 2]
        result = TvDatafeed._TvDatafeed__construct_message(func, param_list)
        expected = '{"m":"test_func","p":["param1",2]}'
        self.assertEqual(result, expected)

    def test_prepend_header(self):
        """Tests if message header is framed correctly for websocket."""
        message = "test_message"
        result = TvDatafeed._TvDatafeed__prepend_header(message)
        expected = f"~m~{len(message)}~m~{message}"
        self.assertEqual(result, expected)

    # Test data frame creation
    def test_create_df(self):
        """Test if raw data is converting into pandas DF."""
        raw_data = '''
        "s":[{"s":"ok","v":[1625097600,100.0,101.0,99.0,100.5,1000]}]
        '''
        result = TvDatafeed._TvDatafeed__create_df(raw_data, "TEST:SYMBOL")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(list(result.columns), 
                        ["symbol", "Time", "Open", "High", "Low", "Close", "Volume"])
        self.assertEqual(result["symbol"].iloc[0], "TEST:SYMBOL")
        self.assertEqual(result["Open"].iloc[0], 100.0)

    # Test get_hist (mocking WebSocket)
    @patch('stock_data.create_connection')
    def test_get_hist(self, mock_create_conn):
        """Tests if historical data retriveval is working, this is mocked.
            1. Mocks websocket connection and response
            2. Verifies the method returns a dataframe
            3. Checks the websocket send is called
            
            Basically confirms data is retrieved without network calls."""
        mock_ws = Mock()
        mock_create_conn.return_value = mock_ws
        mock_ws.recv.side_effect = [
            'some_data',
            '"series_completed"',
        ]
        
        with patch.object(self.tv_datafeed, '_TvDatafeed__create_df', 
                         return_value=pd.DataFrame()):
            df = self.tv_datafeed.get_hist(
                symbol="AAPL",
                exchange="NASDAQ",
                interval=Interval.in_daily,
                n_bars=10
            )
            self.assertIsInstance(df, pd.DataFrame)
            mock_ws.send.assert_called()

if __name__ == '__main__':
    unittest.main(verbosity=9001)