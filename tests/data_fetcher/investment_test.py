import unittest

from data_fetcher.asset import Asset
from data_fetcher.investment import TradeType
from data_fetcher.investment import Investment
from pandas import Timestamp


class TestInvestment(unittest.TestCase):
    def setUp(self):
        self.asset = Asset('AAPL')
        self.asset.fetch_data('2021-12-01', '2022-12-31')
        self.asset.convert_to_target_currency()
        self.investment = Investment(self.asset)

    def test_record_trade(self):
        self.investment.record_trade('2021-12-10', TradeType.BUY, 100000)
        self.assertEqual(len(self.investment.trades), 1)
        self.assertEqual(self.investment.trades[0].trade_type, TradeType.BUY)
        self.assertEqual(self.investment.trades[0].amount, 100000)

    def test_get_state_at(self):
        self.investment.record_trade('2021-12-01', TradeType.BUY, 100000)
        date = '2021-12-15'
        average_share_price, shares, principal, valuation = self.investment.get_state_at(date)
        self.assertEqual(average_share_price, 100000 / shares)
        self.assertEqual(principal, 100000)
        self.assertEqual(valuation,
                         self.asset.data.loc[Timestamp(date).tz_localize('America/New_York'), 'Close'] * shares)


if __name__ == '__main__':
    unittest.main()
