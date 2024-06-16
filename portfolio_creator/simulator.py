# 任意のポートフォリオで運用した場合の期待収益率と標準偏差を計算する。
# モンテカルロ法で運用した場合の収益率のサンプルを作成する。
# 運用は積立を前提とし、リバランスと追加投資を行う。
# リバランスの頻度は原則ボーナスの支給タイミングで行うものとするが、弱気相場や強気相場、調整局面などの評価額が大きく変動した場合、および株価が割安と判断された場合にも行う。
# 追加投資はポートフォリオ内のキャッシュから行う。実施タイミングは弱気相場や調整局面などの評価額が低下した場合に行う。
# 毎月の積立はポートフォリオの設定割合に基づいて行うが、弱気相場や調整局面では、キャッシュの積立を株式の積立に振り替えることができる。
# 以上のシナリオで運用した場合の期待収益率と標準偏差を計算する。

import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import os
import sys
from helper.config import Config
from data_fetcher.asset import Asset
from data_fetcher.portfolio import Portfolio

