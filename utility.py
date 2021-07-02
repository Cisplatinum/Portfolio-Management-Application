import pandas as pd
import numpy as np
from scipy import stats
import StockFetcher

# Retrieve Standard Poor Index data
sp_500 = StockFetcher.fetch_stock('^GSPC')

# Initializing 2D list to store portfolio covariance matrix
# Format: 2D array where the rows and columns are both list of tickers and the respective cell represents
# the covariance between the two tickers
# like      AAPL    GOOG
#      AAPL (cov)   (cov)
#      GOOG (cov)   (cov)
# e.g. [[0.00016886 0.00011057]
#       [0.00011057 0.00017621]]
master_covmatrix = []

# Initializing the list of portfolios
# e.g. ['AAPL','GOOG']
portfolio_list = []

# Initializing the list of portfolios' weightages where the index reflects the one in portfolio_list
# e.g. [0.5,0.5]
weights = []


def set_portfolio(portfolio):
    """
    Get the updated portfolio Main.py and replicate one
    :param portfolio: portfolio dict form Main.py
    :return: null
    """
    global portfolio_list
    portfolio_list = list(portfolio.keys())
    portfolio_list.remove('sum')
    global weights
    weights = []
    for key in portfolio_list:
        weights.append(float(portfolio[key]) / float(portfolio['sum']))


def individual_return_and_risk(data):
    """
    Calculate stock's individual return and individual risk
    with 3-year monthly stock data
    :param data: stock data in pandas.dataFrame
    :return: tuple of individual return and individual risk
    """
    monthly_returns = data['Close'].pct_change(1)
    individual_risk = monthly_returns.std()
    individual_return = monthly_returns.mean()
    
    return (individual_return,individual_risk)

def individual_beta(data):
    """
    Calculate stock's individual beta
    :param data: stock data in pandas.dataFrame
    :return: individual beta
    """
    monthly_prices = pd.concat([data['Close'], sp_500['Close']], axis=1)
    monthly_prices.columns = ['NKE', 'SPY']

    monthly_returns = monthly_prices.pct_change(1)
    clean_monthly_returns = monthly_returns.dropna(axis=0)

    x = clean_monthly_returns['SPY']
    y = clean_monthly_returns['NKE']

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return slope


def portfolio_beta(stock_table):
    """
    Calculate portfolio beta
    :param stock_table:  all stock's data
    :return: portfolio beta
    """
    result = 0
    for ticker in portfolio_list:
        if ticker != 'sum':
            result += (float(stock_table[ticker][2]) * float(weights[portfolio_list.index(ticker)]))
    return result


def get_daily_returns_covmatrix():
    """
    Get a daily returns covariance matrix
    :return: tuple of mean daily returns, daily risk list and covariance matrix
    """
    data = StockFetcher.fetch_stock_1year(portfolio_list)
    returns = data.pct_change(1)
    daily_risk = np.sqrt(np.var(returns))
    covmatrix = returns.cov().values
    global master_covmatrix
    master_covmatrix = covmatrix
    mean_daily_returns = returns.mean().values
    return (mean_daily_returns,daily_risk.values,covmatrix)


def portfolio_risk_and_return_and_rho():
    """
    Calculate portfolio risk, portfolio return and portfolio rho
    :return: tuple of portfolio risk, portfolio return and portfolio rho
    """
    sum1 = 0
    sum2 = 0
    sum3 = 0

    data = get_daily_returns_covmatrix()
    daily_return = data[0]
    covmatrix = data[2]
    daily_risk = data[1]
    for i in range(len(portfolio_list)):
        for j in range(len(portfolio_list)):
            if i == j:
                sum1 += float(weights[i]) * float(weights[j]) * np.square(covmatrix[i,j])
            else:
                sum2 += float(weights[i]) * float(weights[j]) * covmatrix[i,j]
                sum3 += weights[i] * weights[j] * daily_risk[i] * daily_risk[j]
    sum = sum1 + sum2
    portfolio_risk = np.sqrt(sum * 252)
    
    risk_daily = np.square(portfolio_risk)/252
    rho = 0
    if len(portfolio_list) != 1:
        rho = (risk_daily - sum1) / sum3
    else:
        rho = 0

    mean_daily_returns = np.mean(daily_return)
    portfolio_return = np.sum(mean_daily_returns * np.asarray(weights)) * 252

    return (portfolio_risk,portfolio_return,rho)


def marginal_risk_contribution(ticker, portfolio_risk):
    """
    Calculate marginal risk contribution of each stock
    :param ticker: stock name
    :param portfolio_risk: portfolio risk
    :return: marginal risk contribution of given stock ticker
    """
    index = portfolio_list.index(ticker)
    cov_sum = 0
    mrc = 0
    for i in range(len(portfolio_list)):
        if i != index:
            cov_sum += weights[i] * master_covmatrix[i, index]
    if(len(portfolio_list) == 1):
        mrc = portfolio_risk
    else:
        mrc = 252 * weights[index] * (weights[index] * (master_covmatrix[index, index] ** 2) + cov_sum) / portfolio_risk
    return mrc


def pull_plot_data(ticker):
    """
    Retrieve data for plotting purpose
    :param ticker: stock name
    :return: stock data in pandas.dataFrame
    """
    data = StockFetcher.fetch_stock_for_plot(ticker)
    return data