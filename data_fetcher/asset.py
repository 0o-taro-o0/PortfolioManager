import yfinance as yf

from helper.config import Config


class AssetType:
    STOCK = 'stock'
    BOND = 'bond'
    CASH = 'cash'


class Asset:
    def __init__(self, ticker, target_currency='JPY'):
        self.ticker = ticker
        self.data = None
        self.info = {}
        self.exchange_rate = None
        self.target_currency = target_currency
        self.fillna_method = Config().config['fillna_method']
        self.is_converted = False

    def fetch_data(self, start_date: str, end_date: str):
        try:
            ticker_obj = yf.Ticker(self.ticker)
            self.data = ticker_obj.history(start=start_date, end=end_date)
            self.info['currency'] = ticker_obj.info['currency']
            if self.info['currency'] != self.target_currency:
                self.exchange_rate = self.fetch_exchange_rate(self.info['currency'], self.target_currency, start_date,
                                                              end_date)
                if self.fillna_method == 'ffill':
                    self.exchange_rate = self.exchange_rate.ffill()
                elif self.fillna_method == 'bfill':
                    self.exchange_rate = self.exchange_rate.bfill()
                self.convert_to_target_currency()
        except Exception as e:
            print(f"Error occurred while fetching data: {e}")
            self.data = None
            self.info = {}

    def convert_to_target_currency(self):
        if self.is_converted:
            return
        if self.info['currency'] != self.target_currency:
            self.data = self.data.apply(self._convert_row_to_target_currency, axis=1)
            self.is_converted = True

    def _convert_row_to_target_currency(self, row):
        date = row.name.date()
        if date in self.exchange_rate.index:
            rate = self.exchange_rate.loc[date]
            return row * rate
        return row

    @staticmethod
    def fetch_exchange_rate(base_currency, target_currency, start_date, end_date):
        try:
            ticker_obj = yf.Ticker(f'{base_currency}{target_currency}=X')
            data = ticker_obj.history(start=start_date, end=end_date)
            data.index = data.index.date
            return data['Close']
        except Exception as e:
            print(f"Error occurred while fetching exchange rate: {e}")
            return None
