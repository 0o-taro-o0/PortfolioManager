import yfinance as yf

def print_info_keys(ticker):
    ticker_obj = yf.Ticker(ticker)
    print(ticker_obj.info.keys())

if __name__ == '__main__':
    print_info_keys('AAPL')