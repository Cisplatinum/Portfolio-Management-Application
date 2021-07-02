from datetime import datetime
from CustomExceptions import *
from yahoo_historical import Fetcher
import pandas as pd
import numpy as np
from scipy import stats

today = datetime.now()
data_daily1 = Fetcher('^GSPC', [today.year - 1, today.month, today.day]).getHistorical()
data_daily2 = Fetcher('AAPL', [today.year - 1, today.month, today.day]).getHistorical()

monthly_prices = pd.concat([data_daily2['Close'], data_daily1['Close']], axis=1)
monthly_prices.columns = ['NKE', 'SPY']

monthly_returns = monthly_prices.pct_change(1)
clean_monthly_returns = monthly_returns.dropna(axis=0)

x = clean_monthly_returns['SPY']
y = clean_monthly_returns['NKE']

slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
print(slope, intercept)
