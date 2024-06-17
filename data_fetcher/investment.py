from enum import Enum
import pandas as pd
from pandas import Timestamp


class Trade:
    class Type(Enum):
        BUY = 'buy'
        SELL = 'sell'

    def __init__(self, date, trade_type, amount, tax_rate=0):
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
    def __init__(self, asset):
        self.asset = asset
        self.trades = []

    def get_state_at(self, date: str):
        """
        任意の日時での平均取得価格を取得する。
        :param date:
        :return:
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
        if date not in self.asset.data.index:
            next_date = self.asset.data.index[self.asset.data.index > date].min()
            if pd.isna(next_date):
                raise ValueError(f"No data available for date: {date} and onwards")
            date = next_date
        trade = Trade(date, trade_type, amount)
        closing_price = self.asset.data.loc[date, 'Close']
        trade.quantity = amount / closing_price
        self.trades.append(trade)
