import sys
import PullStock
import StockFetcher
from PyQt5.QtWidgets import *
from PyQt5 import uic
import matplotlib.pyplot as plt
import numpy as np
from mpl_finance import candlestick_ohlc
from matplotlib.dates import date2num
from CustomExceptions import *
import utility

# Loading UI files
Ui_MainWindow, QtBaseClass = uic.loadUiType("Main.ui")
Ui_StockList, QtBaseClass = uic.loadUiType("StockList.ui")
Ui_Amount, QtBaseClass = uic.loadUiType("Amount.ui")

# Initializing global dictionary that stores all stocks' data
# Format: {ticker : [individual return, individual risk and individual beta]}
# e.g. {'AAPL' : [0.0136,0.06523,1.1085]}
stock_table = {}

# Initializing global dictionary that stores amount of stocks in portfolio table
# Format: {'sum': amount(in string), 'ticker : amount(in string)}
# e.g. {'sum' : '10000','AAPL' : '10000'}
portfolio =  {}

# Initializing sum as 0
portfolio['sum'] = '0'

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.searchButton.clicked.connect(self.open_stock_list)
        self.portfolioTable.itemDoubleClicked.connect(self.show_graph)

    # Opens Stock table with individual values
    def open_stock_list(self):
        self.dialog = None
        self.dialog = Ui_StockList(parent=self)
        self.dialog.show()

    # Opens graph of the stock's 1-year performance
    def show_graph(self):
        index = self.portfolioTable.selectedIndexes()
        symbol = index[0].data()
        data = utility.pull_plot_data(symbol)
        fig, ax = plt.subplots()
        d = np.array(data.Date, dtype='datetime64')
        dates = date2num(d)
        candlestick_ohlc(ax, zip(dates, data.Open, data.High, data.Low, data.Close), width=2, colorup='g',
                         colordown='r', alpha=1)
        plt.setp(ax.get_xticklabels(), rotation=30)
        ax.xaxis_date()
        plt.show()


class Ui_StockList(QDialog, Ui_StockList):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.AddButton.clicked.connect(self.add_button)
        self.CancelButton.clicked.connect(self.cancel_button)
        self.set_table_data()
        self.show()

    # Builds the stock table with individual values
    def set_table_data(self):
        if len(stock_table) == 0:
            stock_list = PullStock.scan_file('stocklist.csv')
            if len(stock_list) == 0:
                raise ApplicationException('Stock symbol not found', '')
            index = 0
            for key, value in stock_list.items():
                self.stockListTable.insertRow(index)
                self.stockListTable.setItem(index, 0, QTableWidgetItem(key.strip("\"")))

                data = self.get_stock(key.strip("\""))
                reri = self.calc_individual_return_and_risk(data)
                ire = str('{:.2%}'.format(reri[0]))
                iri = str('{:.2%}'.format(reri[1]))
                ibeta = str('{:.4f}'.format(self.calc_beta(data)))

                self.stockListTable.setItem(index, 1, QTableWidgetItem(ire))
                self.stockListTable.setItem(index, 2, QTableWidgetItem(iri))
                self.stockListTable.setItem(index, 3, QTableWidgetItem(ibeta))

                stock_table[key.strip("\"")] = [ire,iri,ibeta]

                index += 1
        else:
            index = 0
            for key, value in stock_table.items():
                self.stockListTable.insertRow(index)
                self.stockListTable.setItem(index, 0, QTableWidgetItem(key))
                self.stockListTable.setItem(index, 1, QTableWidgetItem(value[0]))
                self.stockListTable.setItem(index, 2, QTableWidgetItem(value[1]))
                self.stockListTable.setItem(index, 3, QTableWidgetItem(value[2]))

                index += 1

    # Calls function in utility to calculate individual return and risk
    def calc_individual_return_and_risk(self, data):
        return utility.individual_return_and_risk(data)

    # Calls function in utility to calculate individual beta
    def calc_beta(self, data):
        return utility.individual_beta(data)

    # Calls function in StockFetcher to get original data from Yahoo
    def get_stock(self, ticker):
        return StockFetcher.fetch_stock(ticker)

    # Add_button opens a new window that prompts the user to input the amount
    def add_button(self):
        if self.stockListTable.itemClicked:
            self.dialog = None
            self.dialog = Ui_Amount(parent=self)
            self.dialog.show()

    # Cancel_button closes the window
    def cancel_button(self):
        return self.accept()

    # Cross closes the window
    def close_dialog(self):
        return self.accept()

class Ui_Amount(QDialog, Ui_Amount):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.AddButton.clicked.connect(self.add_button)
        self.CancelButton.clicked.connect(self.cancel_button)
        self.show()

    # Add_button adds the selected stock in the portfolio table of Main Window and stock the amount in portfolio
    # and it triggers the calculation of portfolio values including
    # portfolio return, portfolio risk, portfolio beta, average portfolio correlation, and
    # individual values including weightage and MCTOR
    def add_button(self):
        if self.Amount.text().strip() != '':
            parent = self.parent()
            main = self.parent().parent()

            index = parent.stockListTable.selectedIndexes()
            ticker = index[0].data()
            if ticker in portfolio:
                portfolio['sum'] = str(float(portfolio['sum']) + float(self.Amount.text().strip()))
                portfolio[ticker] = str(float(portfolio[ticker]) + float(self.Amount.text().strip()))
            else:
                portfolio[ticker] = str(float(self.Amount.text().strip()))
                portfolio['sum'] = str(float(portfolio['sum']) + float(portfolio[ticker]))
            utility.set_portfolio(portfolio)

            portfolio_beta = utility.portfolio_beta(stock_table)
            portfolio_risk_and_return_and_rho = utility.portfolio_risk_and_return_and_rho()
            portfolio_risk = portfolio_risk_and_return_and_rho[0]
            portfolio_return = portfolio_risk_and_return_and_rho[1]
            rho = portfolio_risk_and_return_and_rho[2]
            percentages = self.calculate_percentages(ticker)
            mctors = self.calculate_mctors(portfolio_risk)

            main.portfolioTable.setRowCount(0)
            for ticker in portfolio.keys():
                if ticker != 'sum':
                    row = main.portfolioTable.rowCount()
                    main.portfolioTable.insertRow(row)
                    main.portfolioTable.setItem(row, 0, QTableWidgetItem(ticker))
                    main.portfolioTable.setItem(row, 1, QTableWidgetItem(percentages[ticker]))
                    main.portfolioTable.setItem(row, 2, QTableWidgetItem(mctors[ticker]))
                    main.portfolioTable.setItem(row, 3, QTableWidgetItem(stock_table[ticker][2]))

            main.PortfolioReturn.setText(str('{:.2%}'.format(portfolio_return)))
            main.PortfolioRisk.setText(str('{:.2%}'.format(portfolio_risk)))
            main.PortfolioBeta.setText(str('{:.4f}'.format(portfolio_beta)))
            main.AvePortforlioCorr.setText(str('{:.4f}'.format(rho)))

            self.parent().accept()
            return self.accept()

    # calculates percentages of individual stock in portfolio in terms of amount
    def calculate_percentages(self, ticker):
        percentages = {}
        for key, value in portfolio.items():
            if key != 'sum':
                percentages[key] = str('{:.2%}'.format(float(value) / float(portfolio['sum'])))
        return percentages

    # calls function in utility to calculates individual stock mctors
    def calculate_mctors(self,portfolio_risk):
        mctors = {}
        for key, value in portfolio.items():
            if key != 'sum':
                mctors[key] = str('{:.2%}'.format(utility.marginal_risk_contribution(key,portfolio_risk)))
        return mctors

    # Cancel_button closes the window
    def cancel_button(self):
        return self.accept()

    # Cross closes the window
    def close_dialog(self):
        return self.accept()


if __name__=='__main__':
    app=QApplication(sys.argv)
    main=Main()
    main.show()
    sys.exit(app.exec_())
