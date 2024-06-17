# assetクラスを使い、ポートフォリオを作成する。Portfolioクラスを使い、ポートフォリオの運用シミュレーションを行う。

from data_fetcher.investment import Investment, Trade
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
        self.principal = 0
        self.cash_ratio = 0
        self.cash = 0
        self.init_investments()
        self.get_data()

    @staticmethod
    def check_total_ratio(plan: dict):
        ratios = [plan[asset]['ratio'] for asset in plan.keys()]
        return round(sum(ratios), ndigits=8) == 1

    def init_investments(self):
        self.investments = []
        for ticker in self.plan.keys():
            if self.plan[ticker]['type'] not in Asset.Type.__members__:
                raise ValueError(f'Invalid asset type for asset: {ticker}')
            if ticker == 'CASH':
                self.cash_ratio = self.plan[ticker]['ratio']
                continue
            asset = Asset(Asset.Type[self.plan[ticker]['type']], ticker)
            investment = Investment(asset)
            self.investments.append(investment)

    def get_data(self):
        for investment in self.investments:
            # すべてのAssetのdate_rangeからすべてのAssetで共通のdate_rangeを取得する
            if self.date_range is None:
                self.date_range = investment.asset.date_range
            else:
                self.date_range = (max(self.date_range[0], investment.asset.date_range[0]),
                                   min(self.date_range[1], investment.asset.date_range[1]))
        for investment in self.investments:
            investment.asset.fetch_data(self.date_range[0].strftime('%Y-%m-%d'),
                                        self.date_range[1].strftime('%Y-%m-%d'))
            investment.asset.convert_to_target_currency()
        # すべてのデータで開始日と終了日が共通か確認する。
        # 一致しない場合は開始日は後ろにずらし、終了日は前にずらして再取得する。
        # これを一致するまで続ける。３０回以上繰り返す場合はエラーを出力する。
        start_dates = [investment.asset.data.index.min() for investment in self.investments]
        end_dates = [investment.asset.data.index.max() for investment in self.investments]
        for i in range(30):
            if len(set(start_dates)) == 1 and len(set(end_dates)) == 1:
                break
            start_date = max(start_dates)
            end_date = min(end_dates)
            for investment in self.investments:
                investment.asset.fetch_data(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                investment.asset.convert_to_target_currency()
            start_dates = [investment.asset.data.index.min() for investment in self.investments]
            end_dates = [investment.asset.data.index.max() for investment in self.investments]

        if len(set(start_dates)) != 1 or len(set(end_dates)) != 1:
            raise ValueError('Date ranges of assets do not match')

        self.date_range = (start_dates[0], end_dates[0])

    def invest_all(self, date: str, amount: int):
        """
        ポートフォリオ全体に設定した割合で投資する。
        :param date:
        :param amount:
        :return:
        """
        for investment in self.investments:
            investment.record_trade(date, Trade.Type.BUY, amount * self.plan[investment.asset.ticker]['ratio'])
        if self.cash_ratio > 0:
            self.cash += amount * self.cash_ratio
        self.principal += amount

    def invest_to(self, ticker: str, date: str, amount: int):
        """
        特定のAssetに投資する。
        :param ticker:
        :param date:
        :param amount:
        :return:
        """
        if ticker == 'CASH':
            self.cash += amount
            self.principal += amount
            return
        for investment in self.investments:
            if investment.asset.ticker == ticker:
                investment.record_trade(date, Trade.Type.BUY, amount)
                self.principal += amount
                return
        raise ValueError(f'Investment not found for asset: {ticker}')

    def transfer(self, from_: str, to_: str, date: str, amount: int):
        """
        特定のAssetから特定のAssetに資金を移動する。
        :param from_:
        :param to_:
        :param date:
        :param amount:
        :return:
        """
        for investment in self.investments:
            if investment.asset.ticker == from_:
                investment.record_trade(date, Trade.Type.SELL, amount)
            elif investment.asset.ticker == to_:
                investment.record_trade(date, Trade.Type.BUY, amount)
        if from_ == 'CASH':
            self.cash -= amount
        if to_ == 'CASH':
            self.cash += amount

    def get_valuation(self, date: str):
        """
        特定の日付のポートフォリオの評価額を取得する。
        :param date:
        :return:
        """
        valuation = self.cash
        for investment in self.investments:
            average_share_price, shares, principal, asset_valuation = investment.get_state_at(date)
            valuation += asset_valuation
        return valuation

    def rebalance(self, date: str):
        """
        ポートフォリオをリバランスする。
        :param date:
        :return:
        """
        total_valuation = self.get_valuation(date)
        for investment in self.investments:
            average_share_price, shares, principal, valuation = investment.get_state_at(date)
            target_valuation = total_valuation * self.plan[investment.asset.ticker]['ratio']
            if valuation > target_valuation:
                investment.record_trade(date, Trade.Type.SELL, valuation - target_valuation)
            elif valuation < target_valuation:
                investment.record_trade(date, Trade.Type.BUY, target_valuation - valuation)
        if self.cash_ratio > 0:
            self.cash = total_valuation * self.cash_ratio

    def get_profit(self, date: str):
        """
        特定の日付のポートフォリオの利益を取得する。
        :param date:
        :return:
        """
        return self.get_valuation(date) - self.principal

    def get_profit_rate(self, date: str):
        """
        特定の日付のポートフォリオの利益率を取得する。
        :param self:
        :param date:
        :return:
        """
        return self.get_profit(date) / self.principal - 1

    def reset(self):
        """
        ポートフォリオをリセットする。
        :return:
        """
        self.principal = 0
        self.cash = 0
        for investment in self.investments:
            investment.trades = []
