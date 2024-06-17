"""
ポートフォリオを表すクラスを定義するモジュール。
"""

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
    """
    ポートフォリオを表すクラス。

    Attributes
    ----------
    plan : dict
        投資計画を表す辞書。銘柄をキーとし、その銘柄に対する投資比率とアセットタイプを値とする。
    investments : list
        投資のリスト。
    date_range : tuple
        データを取得できる日付の範囲。
    principal : int
        投資元本。
    cash_ratio : float
        現金の投資比率。
    cash : int
        現金。

    Methods
    -------
    check_total_ratio(plan: dict)
        投資計画の投資比率の合計が1であることを確認するメソッド。
    init_investments()
        投資計画に基づいて投資を初期化するメソッド。
    get_data()
        ポートフォリオ内のすべての投資のデータを取得するメソッド。
    invest_all(date: str, amount: int)
        ポートフォリオ全体に設定した割合で投資するメソッド。
    invest_to(ticker: str, date: str, amount: int)
        特定のAssetに投資するメソッド。
    transfer(from_: str, to_: str, date: str, amount: int)
        特定のAssetから特定のAssetに資金を移動するメソッド。
    get_valuation(date: str)
        特定の日付のポートフォリオの評価額を取得するメソッド。
    rebalance(date: str)
        ポートフォリオをリバランスするメソッド。
    get_profit(date: str)
        特定の日付のポートフォリオの利益を取得するメソッド。
    get_profit_rate(date: str)
        特定の日付のポートフォリオの利益率を取得するメソッド。
    reset()
        ポートフォリオをリセットするメソッド。
    """

    def __init__(self, plan: dict):
        """
        Portfolioクラスの初期化メソッド。

        Parameters
        ----------
        plan : dict
            投資計画を表す辞書。銘柄をキーとし、その銘柄に対する投資比率とアセットタイプを値とする。
        """
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
        """
        投資計画の投資比率の合計が1であることを確認するメソッド。

        Parameters
        ----------
        plan : dict
            投資計画を表す辞書。

        Returns
        -------
        bool
            投資比率の合計が1であればTrue、そうでなければFalse。
        """
        ratios = [plan[asset]['ratio'] for asset in plan.keys()]
        return round(sum(ratios), ndigits=8) == 1

    def init_investments(self):
        """
        投資計画に基づいて投資を初期化するメソッド。
        """
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
        """
        ポートフォリオ内のすべての投資のデータを取得するメソッド。
        """
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
        ポートフォリオ全体に設定した割合で投資するメソッド。

        Parameters
        ----------
        date : str
            投資を行う日付。
        amount : int
            投資する金額。
        """
        for investment in self.investments:
            investment.record_trade(date, Trade.Type.BUY, amount * self.plan[investment.asset.ticker]['ratio'])
        if self.cash_ratio > 0:
            self.cash += amount * self.cash_ratio
        self.principal += amount

    def invest_to(self, ticker: str, date: str, amount: int):
        """
        特定のAssetに投資するメソッド。

        Parameters
        ----------
        ticker : str
            投資する銘柄。
        date : str
            投資を行う日付。
        amount : int
            投資する金額。
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
        特定のAssetから特定のAssetに資金を移動するメソッド。

        Parameters
        ----------
        from_ : str
            資金を移動する元の銘柄。
        to_ : str
            資金を移動する先の銘柄。
        date : str
            資金の移動を行う日付。
        amount : int
            移動する金額。
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
        特定の日付のポートフォリオの評価額を取得するメソッド。

        Parameters
        ----------
        date : str
            評価額を取得する日付。

        Returns
        -------
        float
            指定した日付でのポートフォリオの評価額。
        """
        valuation = self.cash
        for investment in self.investments:
            average_share_price, shares, principal, asset_valuation = investment.get_state_at(date)
            valuation += asset_valuation
        return valuation

    def rebalance(self, date: str):
        """
        ポートフォリオをリバランスするメソッド。

        Parameters
        ----------
        date : str
            リバランスを行う日付。
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
        特定の日付のポートフォリオの利益を取得するメソッド。

        Parameters
        ----------
        date : str
            利益を取得する日付。

        Returns
        -------
        float
            指定した日付でのポートフォリオの利益。
        """
        return self.get_valuation(date) - self.principal

    def get_profit_rate(self, date: str):
        """
        特定の日付のポートフォリオの利益率を取得するメソッド。

        Parameters
        ----------
        date : str
            利益率を取得する日付。

        Returns
        -------
        float
            指定した日付でのポートフォリオの利益率。
        """
        return self.get_profit(date) / self.principal

    def reset(self):
        """
        ポートフォリオをリセットするメソッド。
        """
        self.principal = 0
        self.cash = 0
        for investment in self.investments:
            investment.trades = []
