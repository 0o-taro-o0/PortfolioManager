from data_fetcher.asset import Asset

from pandas import Timestamp

if __name__ == '__main__':
    asset = Asset('AAPL')
    asset.fetch_data('2021-12-01', '2022-12-31')
    time: Timestamp = asset.data.index[0]
    print(time.tz)