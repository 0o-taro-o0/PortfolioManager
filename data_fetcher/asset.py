"""
アセットを表すクラスを定義するモジュール。
"""

from enum import Enum

import numpy as np
import pandas as pd
import yfinance as yf

from helper.config import Config


class Asset:
    """
    アセットを表すクラス。

    Attributes
    ----------
    asset_type : Type
        アセットの種類（株式、債券など）。
    ticker : str
        アセットのティッカーシンボル。
    data : pd.DataFrame
        アセットのデータ。
    info : dict
        アセットの情報。
    exchange_rate : pd.Series
        為替レート。
    target_currency : str
        換算する通貨の種類。
    fillna_method : str
        欠損値を埋める方法。
    is_converted : bool
        アセットデータが換算されたかどうか。
    date_range : tuple
        データを取得できる日付の範囲。

    Methods
    -------
    fetch_data(start_date: str = None, end_date: str = None, entirely: bool = False)
        指定された日付範囲のアセットデータを取得するメソッド。
    convert_to_target_currency()
        アセットデータを目標通貨に換算するメソッド。
    fetch_exchange_rate(base_currency, target_currency, start_date, end_date)
        指定された日付範囲の為替レートを取得するメソッド。
    """
    class Type(Enum):
        """
        アセットの種類を表すEnumクラス。
        """
        STOCK = 'stock'
        BOND = 'bond'
        CASH = 'cash'
        ETF = 'etf'
        INDEX = 'index'

    def __init__(self, asset_type: Type, ticker: str = None, target_currency: str = 'JPY'):
        """
        Assetクラスの初期化メソッド。

        Parameters
        ----------
        asset_type : Type
            アセットの種類（株式、債券など）。
        ticker : str, optional
            アセットのティッカーシンボル。
        target_currency : str, optional
            換算する通貨の種類。デフォルトは'JPY'。
        """
        self.asset_type = asset_type
        self.ticker = ticker
        self.data = None
        self.info = {}
        self.exchange_rate = None
        self.target_currency = target_currency
        self.fillna_method = Config().config['fillna_method']
        self.is_converted = False
        self.date_range = self.__get_date_range()

    def __get_date_range(self):
        """"
        アセットのデータを取得できる日付の範囲を取得するプライベートメソッド。

        Returns
        -------
        tuple
            データを取得できる日付の範囲（開始日、終了日）。
        """
        try:
            ticker_obj = yf.Ticker(self.ticker)
            data = ticker_obj.history(period='max')
            date_range = (data.index.min(), data.index.max())
            del data
        except Exception as e:
            print(f"Error occurred while fetching data: {e}")
            date_range = None
        return date_range

    def fetch_data(self, start_date: str = None, end_date: str = None, entirely: bool = False):
        """
        指定された日付範囲のアセットデータを取得するメソッド。

        Parameters
        ----------
        start_date : str, optional
            データを取得する開始日。
        end_date : str, optional
            データを取得する終了日。
        entirely : bool, optional
            データを全期間取得するかどうか。デフォルトはFalse。
        """
        try:
            ticker_obj = yf.Ticker(self.ticker)
            if entirely:
                self.data = ticker_obj.history(period='max')
            else:
                self.data = ticker_obj.history(start=start_date, end=end_date)
            self.is_converted = False
            self.info['currency'] = ticker_obj.info['currency']

        except Exception as e:
            print(f"Error occurred while fetching data: {e}")
            self.data = None
            self.info = {}

    def convert_to_target_currency(self):
        """
        アセットデータを目標通貨に換算するメソッド。
        """
        if self.is_converted:
            return
        if self.info['currency'] != self.target_currency:
            self.exchange_rate = self.fetch_exchange_rate(self.info['currency'], self.target_currency,
                                                          self.data.index.min(),
                                                          self.data.index.max())
            self.data = self.data.apply(self.__convert_row_to_target_currency, axis=1)
            # Drop rows with NaN values
            self.data.dropna(inplace=True)
            self.is_converted = True

    def __convert_row_to_target_currency(self, row):
        """
        行を目標通貨に換算するプライベートメソッド。
        :param row:
        """
        date = pd.Timestamp(row.name.date())
        if date in self.exchange_rate.index:
            rate = self.exchange_rate.loc[date]
            return row * rate
        # Return NaN if the exchange rate is unknown
        return pd.Series([np.nan] * len(row), index=row.index)

    def fetch_exchange_rate(self, base_currency, target_currency, start_date, end_date):
        """
        指定された日付範囲の為替レートを取得するメソッド。

        Parameters
        ----------
        base_currency : str
            基準となる通貨の種類。
        target_currency : str
            換算する通貨の種類。
        start_date : str
            為替レートを取得する開始日。
        end_date : str
            為替レートを取得する終了日。

        Returns
        -------
        pd.Series
            指定された日付範囲の為替レート。
        """
        try:
            ticker_obj = yf.Ticker(f'{base_currency}{target_currency}=X')
            data = ticker_obj.history(start=start_date, end=end_date)
            data.index = data.index.date
            # Create a date range from start_date to end_date
            date_range = pd.date_range(start=data.index.min(), end=data.index.max())

            # Reindex the data with the full date range
            data = data.reindex(date_range)

            # Fill missing values after reindexing
            if self.fillna_method == 'ffill':
                data = data.ffill()
            elif self.fillna_method == 'bfill':
                data = data.bfill()
            return data['Close']
        except Exception as e:
            print(f"Error occurred while fetching exchange rate: {e}")
        return None
