"""
投資を表すクラスと取引を表すクラスを定義するモジュール。
"""

from enum import Enum
import pandas as pd
from pandas import Timestamp


class Trade:
    """
    取引を表すクラス。

    Attributes
    ----------
    date : Timestamp
        取引の日付。
    trade_type : TradeType
        取引の種類（購入または売却）。
    amount : float
        取引の金額。
    tax_rate : float
        取引にかかる税率。
    average_share_price : float
        取引の平均株価。

    Methods
    -------
    None
    """
    class Type(Enum):
        """
        取引の種類を表すEnumクラス。
        """
        BUY = 'buy'
        SELL = 'sell'

    def __init__(self, date, trade_type, amount, tax_rate=0):
        """
        Tradeクラスの初期化メソッド。

        Parameters
        ----------
        date : str
            取引の日付。
        trade_type : TradeType
            取引の種類（購入または売却）。
        amount : float
            取引の金額。
        tax_rate : float
            取引にかかる税率。
        """
        self.date = Timestamp(date)
        if self.date.tzinfo is None:
            self.date = self.date.tz_localize('America/New_York')
        else:
            self.date = self.date.tz_convert('America/New_York')
        self.trade_type = trade_type
        self.amount = amount
        self.tax_rate = tax_rate
        self.average_share_price = None


class Investment:
    """
    投資を表すクラス。

    Attributes
    ----------
    asset : Asset
        投資対象のアセット。
    trades : list
        取引のリスト。

    Methods
    -------
    get_state_at(date: str)
        指定した日付での投資の状態を取得するメソッド。
    record_trade(date: str, trade_type: TradeType, amount: float)
        取引を記録するメソッド。
    """
    def __init__(self, asset):
        """
        Investmentクラスの初期化メソッド。

        Parameters
        ----------
        asset : Asset
            投資対象のアセット。
        """
        self.asset = asset
        self.trades = []

    def get_state_at(self, date: str):
        """
        指定した日付での投資の状態を取得するメソッド。

        Parameters
        ----------
        date : str
            状態を取得する日付。

        Returns
        -------
        dict
            指定した日付での投資の状態。
        """
        date = Timestamp(date).tz_localize('America/New_York')
        if date not in self.asset.data.index:
            previous_date = self.asset.data.index[self.asset.data.index < date].max()
            if pd.isna(previous_date):
                raise ValueError(f"No data available for date: {date} and before")
            date = previous_date
        shares = 0
        average_share_price = 0
        # tradesを過去の取引から順に見ていく
        for trade in sorted(self.trades, key=lambda x: x.date):
            if trade.date <= date:
                if trade.trade_type == Trade.Type.BUY:
                    # 過去の取引での購入価格の総額
                    temp_principal = shares * average_share_price
                    shares += trade.quantity
                    average_share_price = (temp_principal + trade.amount) / shares
                elif trade.trade_type == Trade.Type.SELL:
                    # sharesをtrade.quantity分減らす。
                    shares -= trade.quantity

        average_share_price = average_share_price if shares > 0 else 0
        shares = shares if shares > 0 else 0
        principal = shares * average_share_price
        valuation = self.asset.data.loc[date, 'Close'] * shares
        return average_share_price, shares, principal, valuation

    def record_trade(self, date: str, trade_type: Trade.Type, amount: int):
        """
        取引を記録するメソッド。

        Parameters
        ----------
        date : str
            取引の日付。
        trade_type : TradeType
            取引の種類（購入または売却）。
        amount : float
            取引の金額。
        """
        if date not in self.asset.data.index:
            next_date = self.asset.data.index[self.asset.data.index > date].min()
            if pd.isna(next_date):
                raise ValueError(f"No data available for date: {date} and onwards")
            date = next_date
        trade = Trade(date, trade_type, amount)
        closing_price = self.asset.data.loc[date, 'Close']
        trade.quantity = amount / closing_price
        self.trades.append(trade)
