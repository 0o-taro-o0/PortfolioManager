from enum import Enum

import pandas as pd
import yfinance as yf

from helper.config import Config


class Asset:
    class Type(Enum):
        STOCK = 'stock'
        BOND = 'bond'
        CASH = 'cash'
        ETF = 'etf'
        INDEX = 'index'

    def __init__(self, asset_type: Type, ticker: str = None, target_currency: str = 'JPY'):
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
        if self.is_converted:
            return
        if self.info['currency'] != self.target_currency:
            self.exchange_rate = self.fetch_exchange_rate(self.info['currency'], self.target_currency,
                                                          self.data.index.min(),
                                                          self.data.index.max())
            self.data = self.data.apply(self._convert_row_to_target_currency, axis=1)
            self.is_converted = True

    def _convert_row_to_target_currency(self, row):
        date = pd.Timestamp(row.name.date())
        if date in self.exchange_rate.index:
            rate = self.exchange_rate.loc[date]
            return row * rate
        return row

    def fetch_exchange_rate(self, base_currency, target_currency, start_date, end_date):
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
