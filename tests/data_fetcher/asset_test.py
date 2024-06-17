import unittest

import yfinance as yf

from data_fetcher.asset import Asset


class TestAsset(unittest.TestCase):

    def test_initialization(self):
        """Tests whether an Asset object can be correctly initialized."""
        asset = Asset(Asset.Type.STOCK, 'AAPL')
        self.assertEqual(asset.ticker, 'AAPL')
        self.assertIsNone(asset.data)
        self.assertEqual(asset.info, {})
        self.assertEqual(asset.target_currency, 'JPY')

    def test_fetch_data(self):
        """Tests whether data can be fetched correctly for an Asset object."""
        asset = Asset(Asset.Type.STOCK, 'AAPL')
        asset.fetch_data('2022-01-01', '2022-12-31')
        self.assertIsNotNone(asset.data)
        self.assertIsNotNone(asset.info['currency'])

    def test_fetch_data_with_invalid_ticker(self):
        """Tests whether an exception is raised when an invalid ticker is provided to fetch data for an Asset object."""
        try:
            asset = Asset(Asset.Type.BOND, 'INVALID_TICKER')
            asset.fetch_data('2022-01-01', '2022-12-31')
        except Exception as e:
            self.assertIsInstance(e, Exception)

    def test_convert_to_target_currency(self):
        """Tests whether data can be correctly converted to the target currency for an Asset object."""
        asset = Asset(Asset.Type.STOCK, 'AAPL')
        asset.fetch_data('2022-01-01', '2022-12-31')
        if asset.info['currency'] != asset.target_currency:
            ticker_obj = yf.Ticker(asset.ticker)
            data_before_conversion = ticker_obj.history(start='2022-01-01', end='2022-12-31')
            asset.convert_to_target_currency()
            self.assertNotEqual(data_before_conversion['Close'].iloc[0], asset.data['Close'].iloc[0])
            self.assertNotEqual(data_before_conversion['Open'].iloc[0], asset.data['Open'].iloc[0])
            self.assertNotEqual(data_before_conversion['High'].iloc[0], asset.data['High'].iloc[0])
            self.assertNotEqual(data_before_conversion['Low'].iloc[0], asset.data['Low'].iloc[0])

    def test_convert_to_target_currency_with_invalid_exchange_rate(self):
        """Tests whether an exception is raised when an invalid exchange rate is provided to convert data to the
        target currency for an Asset object."""
        asset = Asset(Asset.Type.STOCK, 'AAPL')
        asset.fetch_data('2022-01-01', '2022-12-31')
        asset.exchange_rate = None
        try:
            asset.convert_to_target_currency()
        except Exception as e:
            self.assertIsInstance(e, Exception)


if __name__ == '__main__':
    unittest.main()
