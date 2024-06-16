# assetクラスを使い、ポートフォリオを作成する。Portfolioクラスを使い、ポートフォリオの運用シミュレーションを行う。

import pandas as pd
import matplotlib.pyplot as plt


class Portfolio:
    """
    A class to represent a portfolio.
    アセットクラスとポートフォリオ内でのアセットの割合を受け取り、ポートフォリオを作成する。

    """
    def __init__(self, assets, weights, target_currency='JPY'):
        self.assets = assets
        self.weights = weights
        self.target_currency = target_currency
        self.data = None
        self.info = {}
        self.exchange_rate = None

    def fetch_data(self, start_date, end_date):
        for asset in self.assets:
            asset.fetch_data(start_date, end_date)
        self.data = pd.concat([asset.data for asset in self.assets], axis=1)
        self.data = self.data.dropna()

    def convert_to_target_currency(self):
        for asset in self.assets:
            asset.convert_to_target_currency()
        self.exchange_rate = self.assets[0].exchange_rate

    def calculate_portfolio_return(self):
        self.data['Portfolio'] = 0
        for i, asset in enumerate(self.assets):
            self.data['Portfolio'] += self.data[asset.ticker] * self.weights[i]
        self.data['Portfolio'] = self.data['Portfolio'] / self.data['Portfolio'].iloc[0]
        self.data['Portfolio'] = self.data['Portfolio'] * self.exchange_rate

    def calculate_portfolio_statistics(self):
        self.info['Portfolio'] = {}
        self.info['Portfolio']['Return'] = (self.data['Portfolio'].iloc[-1] / self.data['Portfolio'].iloc[0]) - 1
        self.info['Portfolio']['StdDev'] = self.data['Portfolio'].pct_change().std()
        self.info['Portfolio']['SharpeRatio'] = self.info['Portfolio']['Return'] / self.info['Portfolio']['StdDev']

    def plot_portfolio(self):
        plt.figure(figsize=(12, 6))
        for asset in self.assets:
            plt.plot(self.data[asset.ticker] / self.data[asset.ticker].iloc[0], label=asset.ticker)
        plt.plot(self.data['Portfolio'] / self.data['Portfolio'].iloc[0], label='Portfolio', linewidth=3)
        plt.legend()
        plt.show()