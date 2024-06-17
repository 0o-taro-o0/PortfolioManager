import unittest
from data_fetcher.asset import Asset
from data_fetcher.investment import Investment
from data_fetcher.portfolio import Portfolio

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        asset = Asset(Asset.Type.STOCK, 'AAPL')
        asset.fetch_data('2021-12-01', '2022-12-31')
        asset.convert_to_target_currency()
        investment = Investment(asset)
        self.portfolio = Portfolio({'AAPL': {'ratio': 0.7}, 'GOOGL': {'ratio': 0.3}})

    def test_check_total_ratio(self):
        sample_investments = {
            'AAPL': {
                'ratio': 0.7,
                'type': 'STOCK'
            },
            'GOOGL': {
                'ratio': 0.3,
                'type': 'STOCK'
            }
        }
        self.assertTrue(self.portfolio.check_total_ratio(sample_investments))
        sample_investments['GOOGL']['ratio'] = 0.4
        self.assertFalse(self.portfolio.check_total_ratio(sample_investments))

if __name__ == '__main__':
    unittest.main()
