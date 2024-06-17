# 任意のポートフォリオで運用した場合の期待収益率と標準偏差を計算する。
# モンテカルロ法で運用した場合の収益率のサンプルを作成する。
# 運用は積立を前提とし、リバランスと追加投資を行う。
# リバランスの頻度は原則ボーナスの支給タイミングで行うものとするが、弱気相場や強気相場、調整局面などの評価額が大きく変動した場合、および株価が割安と判断された場合にも行う。
# 追加投資はポートフォリオ内のキャッシュから行う。実施タイミングは弱気相場や調整局面などの評価額が低下した場合に行う。
# 毎月の積立はポートフォリオの設定割合に基づいて行うが、弱気相場や調整局面では、キャッシュの積立を株式の積立に振り替えることができる。
# 以上のシナリオで運用した場合の期待収益率と標準偏差を計算する。
import pandas as pd

import yfinance as yf

from data_fetcher.portfolio import Portfolio

if __name__ == '__main__':
    plan = {
        'AAPL': {
            'ratio': 1,
            'type': 'STOCK'
        },
        # 'GOOGL': {
        #     'ratio': 0.3,
        #     'type': 'STOCK'
        # }
    }

    portfolio = Portfolio(plan)

    # 毎月２万円の積立を２年間行う。
    # 開始日はportfolio.date_range[0]後の最初の月初とする。
    # 終了日は開始日から２年後の最初の月初とする。
    # start_date = pd.Timestamp('1996-01-01').tz_localize('America/New_York') + pd.DateOffset(months=1)
    start_date = portfolio.date_range[0] + pd.DateOffset(months=1)
    end_date = start_date + pd.DateOffset(years=3) - pd.DateOffset(days=1)
    print(f"Start date: {start_date}")
    print(f"End date: {end_date}")

    # 毎月積立る
    for date in pd.date_range(start_date, end_date, freq='MS'):
        portfolio.invest_all(date.strftime('%Y-%m-%d'), 20000)

    # 結果を表示
    print(f"Principal: {portfolio.principal}")
    print(f"Cash: {portfolio.cash}")
    print(f"Valuation: {portfolio.get_valuation(end_date.strftime('%Y-%m-%d'))}")
    print(f"Profit: {portfolio.get_profit(end_date.strftime('%Y-%m-%d'))}")
    print(f"Profit rate: {portfolio.get_profit_rate(end_date.strftime('%Y-%m-%d'))}")
    for investment in portfolio.investments:
        state = investment.get_state_at(end_date.strftime('%Y-%m-%d'))
        print(f"Ticker: {investment.asset.ticker}")
        print(f"Shares: {state[1]}")
        print(f"Average share price: {state[0]}")
        print(f"Principal: {state[2]}")
        print(f"Valuation: {state[3]}")
        print()

    print(portfolio.investments[0].asset.date_range)
    print(portfolio.investments[0].asset.info)
    print(portfolio.investments[0].asset.is_converted)

ticker_obj = yf.Ticker(f'USDJPY=X').history(period='max')
print(ticker_obj)

