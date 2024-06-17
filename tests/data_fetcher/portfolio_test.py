import unittest
from data_fetcher.asset import Asset
from data_fetcher.portfolio import Portfolio


class TestPortfolio(unittest.TestCase):
    def setUp(self):
        asset = Asset(Asset.Type.STOCK, 'AAPL')
        asset.fetch_data('2021-12-01', '2022-12-31')
        asset.convert_to_target_currency()
        self.portfolio = Portfolio({
            'AAPL': {
                'ratio': 0.7,
                'type': 'STOCK'
            },
            'GOOGL': {
                'ratio': 0.3,
                'type': 'STOCK'
            }
        })

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

    def test_get_data(self):
        self.portfolio.init_investments()
        self.portfolio.get_data()
        self.assertIsNotNone(self.portfolio.date_range)
        for investment in self.portfolio.investments:
            self.assertIsNotNone(investment.asset.data)
            self.assertIsNotNone(investment.asset.info['currency'])
            self.assertIsNotNone(investment.asset.exchange_rate)
            self.assertTrue(investment.asset.is_converted)
            # Check that the start and end dates of the asset data match the portfolio's date range
            self.assertEqual(self.portfolio.date_range[0], investment.asset.data.index.min())
            self.assertEqual(self.portfolio.date_range[1], investment.asset.data.index.max())


if __name__ == '__main__':
    unittest.main()
