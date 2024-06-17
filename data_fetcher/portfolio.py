# assetクラスを使い、ポートフォリオを作成する。Portfolioクラスを使い、ポートフォリオの運用シミュレーションを行う。

from data_fetcher.investment import Investment
from data_fetcher.asset import Asset

example_plan = {
    'AAPL': {
        'ratio': 0.7,
        'type': 'STOCK'
    },
    'GOOGL': {
        'ratio': 0.3,
        'type': 'STOCK'
    }
}


class Portfolio:
    def __init__(self, plan: dict):
        if not self.check_total_ratio(plan):
            raise ValueError('Total ratio of investments must be 1')
        self.plan = plan
        self.investments = []
        self.date_range = None
        # self.investments = investments
        # self.portfolio = pd.DataFrame()
        # self.portfolio['cash'] = 0
        # for investment in investments.values():
        #     self.portfolio[investment.asset.asset_id] = 0

    @staticmethod
    def check_total_ratio(plan: dict):
        ratios = [plan[asset]['ratio'] for asset in plan.keys()]
        return sum(ratios) == 1

    def init_investments(self):
        for ticker in self.plan.keys():
            asset = Asset(Asset.Type[self.plan[ticker]['type']], ticker)
            investment = Investment(asset)
            self.investments.append(investment)

    def get_data(self):
        for investment in self.investments:
            if self.date_range is None:
                investment.asset.fetch_data(entirely=True)
                self.date_range = (investment.asset.data.index.min(), investment.asset.data.index.max())
            else:
                investment.asset.fetch_data(self.date_range[0].strftime('%Y-%m-%d'),
                                            self.date_range[1].strftime('%Y-%m-%d'))
                date_range = (investment.asset.data.index.min(), investment.asset.data.index.max())
                self.date_range = (max(self.date_range[0], date_range[0]), min(self.date_range[1], date_range[1]))
        for investment in self.investments:
            investment.asset.data = investment.asset.data.loc[self.date_range[0]:self.date_range[1]].copy()
            # If the first date is not in the index, add a new record with the data of the oldest date
            if self.date_range[0] not in investment.asset.data.index:
                oldest_date = investment.asset.data.index.min()
                oldest_data = investment.asset.data.loc[oldest_date]
                investment.asset.data.loc[self.date_range[0]] = oldest_data

            # If the last date is not in the index, add a new record with the data of the newest date
            if self.date_range[1] not in investment.asset.data.index:
                newest_date = investment.asset.data.index.max()
                newest_data = investment.asset.data.loc[newest_date]
                investment.asset.data.loc[self.date_range[1]] = newest_data
            investment.asset.convert_to_target_currency()

    # def rebalance(self, date):
    #     # Implement rebalancing logic here
    #     pass
    #
    # def invest(self, date, investment_id, amount):
    #     # Add the investment amount to the specified investment
    #     self.investments[investment_id].record_trade(date, TradeType.BUY, amount)
    #
    # def simulate(self, start_date, end_date):
    #     # Implement simulation logic here
    #     pass
    #
    # def plot(self):
    #     self.portfolio.plot()
    #     plt.show()
