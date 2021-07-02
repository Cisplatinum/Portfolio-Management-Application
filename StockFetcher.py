from datetime import datetime
from CustomExceptions import *
from yahoo_historical import Fetcher
import pandas as pd
import pandas_datareader.data as web


def fetch_stock(ticker):
    """
    Retrieves 3-year monthly stock data from Yahoo with given ticker
    :param ticker: stock ticker name e.g. 'AAPL'
    :return: Stock data in pandas.dataFrame structure
    """
    today = datetime.now()
    try:
        data = Fetcher(ticker, [today.year - 3, today.month, today.day], interval='1mo')
        return data.getHistorical()
    except ApplicationException:
        raise ApplicationException('The ticker input is invalid','')


def fetch_stock_1year(portfolio_list):
    """
    Retrieves 1-year daily stock 'Adj Close' data from Yahoo with given ticker list
    :param portfolio_list: list of tickers e.g. ['AAPL', 'GOOG']
    :return: Stock data in pandas.dataFrame structure
    """
    data = pd.DataFrame()
    for ticker in portfolio_list:
        try:
            today = datetime.now()
            data_daily = Fetcher(ticker, [today.year - 1, today.month, today.day])
            data[ticker] = data_daily.getHistorical()['Adj Close']
        except ApplicationException:
            raise ApplicationException('The ticker input is invalid','')
    return data

def fetch_stock_for_plot(ticker):
    """
    Retrieves 1-year daily stock data from Yahoo with given ticker for plotting purpose
    :param ticker: stock ticker name e.g. 'AAPL'
    :return: Stock data in pandas.dataFrame structure
    """
    try:
        today = datetime.now()
        data_daily = Fetcher(ticker, [today.year - 1, today.month, today.day]).getHistorical()
    except ApplicationException:
        raise ApplicationException('The ticker input is invalid','')
    return data_daily


