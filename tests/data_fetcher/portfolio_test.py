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
                'ratio': 0.2,
                'type': 'STOCK'
            },
            'CASH': {
                'ratio': 0.1,
                'type': 'CASH'
            }
        })

    def test_check_total_ratio(self):
        sample_investments = {
            'AAPL': {
                'ratio': 0.75,
                'type': 'STOCK'
            },
            'GOOGL': {
                'ratio': 0.25,
                'type': 'STOCK'
            }
        }
        self.assertTrue(self.portfolio.check_total_ratio(sample_investments))
        sample_investments['GOOGL']['ratio'] = 0.4
        self.assertFalse(self.portfolio.check_total_ratio(sample_investments))

    def test_init_investments(self):
        self.portfolio.init_investments()
        self.assertEqual(len(self.portfolio.investments), 2)
        self.assertEqual(self.portfolio.cash_ratio, 0.1)
        self.assertEqual(self.portfolio.cash, 0)

    def test_get_data(self):
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

    def test_invest_all(self):
        self.portfolio.invest_all('2021-12-01', 100000)
        self.assertEqual(self.portfolio.principal, 100000)
        self.assertEqual(self.portfolio.cash, 10000)
        for investment in self.portfolio.investments:
            self.assertEqual(investment.trades[0].trade_type.name, 'BUY')
            self.assertEqual(investment.trades[0].amount,
                             100000 * self.portfolio.plan[investment.asset.ticker]['ratio'])

    def test_invest_to(self):
        self.portfolio.invest_to('AAPL', '2021-12-01', 100000)
        self.assertEqual(self.portfolio.principal, 100000)
        self.assertEqual(self.portfolio.investments[0].trades[0].trade_type.name, 'BUY')
        self.assertEqual(self.portfolio.investments[0].trades[0].amount, 100000)

    def test_transfer(self):
        self.portfolio.invest_all('2021-12-01', 100000)
        self.portfolio.transfer('AAPL', 'GOOGL', '2021-12-05', 50000)
        self.assertEqual(self.portfolio.principal, 100000)
        self.assertEqual(self.portfolio.cash, 10000)
        self.assertEqual(self.portfolio.investments[0].trades[1].trade_type.name, 'SELL')
        self.assertEqual(self.portfolio.investments[1].trades[0].trade_type.name, 'BUY')
        self.assertEqual(self.portfolio.investments[0].trades[1].amount, 50000)
        self.assertEqual(self.portfolio.investments[1].trades[1].amount, 50000)


    def test_get_valuation(self):
        self.portfolio.invest_all('2021-12-01', 100000)
        self.portfolio.invest_to('AAPL', '2021-12-05', 100000)
        valuation = self.portfolio.get_valuation('2021-12-10')
        self.assertGreaterEqual(valuation, 200000)
    def test_rebalance(self):
        self.portfolio.invest_all('2021-12-01', 100000)
        self.portfolio.invest_to('AAPL', '2021-12-05', 100000)
        self.portfolio.rebalance('2021-12-10')
        self.assertEqual(self.portfolio.principal, 200000)
        self.assertGreaterEqual(self.portfolio.cash, 20000)
        self.assertEqual(self.portfolio.investments[0].trades[2].trade_type.name, 'SELL')
        self.assertEqual(self.portfolio.investments[1].trades[1].trade_type.name, 'BUY')
        self.assertGreaterEqual(self.portfolio.investments[0].trades[2].amount, 30000)
        self.assertGreaterEqual(self.portfolio.investments[1].trades[1].amount, 20000)

    def test_get_profit(self):
        self.portfolio.invest_all('2021-12-01', 100000)
        self.portfolio.invest_to('AAPL', '2021-12-05', 100000)
        profit = self.portfolio.get_profit('2021-12-10')
        self.assertGreaterEqual(profit, 0)

    def test_get_profit_rate(self):
        self.portfolio.invest_all('2021-12-01', 100000)
        self.portfolio.invest_to('AAPL', '2021-12-05', 100000)
        profit_rate = self.portfolio.get_profit_rate('2021-12-10')
        self.assertGreaterEqual(profit_rate, 0)

    def test_reset(self):
        self.portfolio.invest_all('2021-12-01', 100000)
        self.portfolio.invest_to('AAPL', '2021-12-05', 100000)
        self.portfolio.reset()
        self.assertEqual(self.portfolio.principal, 0)
        self.assertEqual(self.portfolio.cash, 0)
        self.assertGreater(self.portfolio.cash_ratio, 0)
        for investment in self.portfolio.investments:
            self.assertEqual(len(investment.trades), 0)
            self.assertGreater(len(investment.asset.data['Close']), 0)
            self.assertNotEqual(investment.asset.info, {})
            self.assertGreater(len(investment.asset.exchange_rate), 0)
            self.assertNotEqual(investment.asset.is_converted, False)
            self.assertNotEqual(investment.asset.date_range, None)

if __name__ == '__main__':
    unittest.main()
