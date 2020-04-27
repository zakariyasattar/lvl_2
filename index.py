import sys
import time
import requests
from bs4 import BeautifulSoup
import alpaca_trade_api as tradeapi
import json
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np

"""
    TODO:

    Finish populateAsksBids, decide
    Test submitOrder


"""

# Init Webdriver
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
driver.set_window_position(-10000,0)

# ALPACA API INIT
api = tradeapi.REST('PKWS07EUH6HN0TVT14O2', 'A5Ffk2KHJ6UO10xiEqwrsRzh4G68e5Am3OlQ421m', "https://paper-api.alpaca.markets", api_version='v2')
alphavantage_api_key = "L9ORMXCSUYTKB325"

# pull data from cboe
driver.get("https://markets.cboe.com/us/equities/market_statistics/book/?mkt=edgx")
html = driver.execute_script('return document.body.innerHTML;')
cboe_data = BeautifulSoup(html, 'lxml')

# Isolate necessary data
ticker = (cboe_data.find("input", {"id": "symbol0"}).get('value'))

bid_share_count = (cboe_data.findAll("td", {"class": "book-viewer__bid book-viewer__bid-shares"}))
ask_share_count = (cboe_data.findAll("td", {"class": "book-viewer__ask book-viewer__ask-shares"}))

ask_price = (cboe_data.findAll("td", {"class": "book-viewer__ask book-viewer__ask-price book-viewer-price"}))
bid_price = (cboe_data.findAll("td", {"class": "book-viewer__bid book-viewer__bid-price book-viewer-price"}))

asks = [
            ["3500", "14.75"],
            ["1000", "14.6"],
            [""]
        ]
bids = ["3000", "300", "600", "30000"]


# Populate bids and asks arrays with order size data
def populateAsksBids(bid_share_count, bid_price, ask_share_count, ask_price):
    asks = "ekmd"


def decide():
    for ask in asks:
        print(ask)

decide()

# get last close for param: ticker
def getQuote(ticker):
    # response = (requests.get("https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=" + ticker + "&apikey=" + alphavantage_api_key))
    # data = response.content.decode('utf8').replace("'", '"')
    # formatted_json = json.loads(data)
    #
    # # checks if overusage message is returned
    # if(not 'Note' in formatted_json):
    #     return float((formatted_json["Global Quote"]["05. price"]))
    # # use Yahoo Finance if Alpha throws overusage
    # else:
    #     driver.get("https://finance.yahoo.com/quote/" + ticker)
    #     html = driver.execute_script('return document.body.innerHTML;')
    #     yahoo_data = BeautifulSoup(html, 'lxml')
    #     close_price = [entry.text for entry in yahoo_data.find_all('span', {'class':'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'})]
    #     return float(close_price[0])
    return 14.59

def submitOrder(side):
    api.submit_order(ticker, api.get_account().buying_power / getQuote(ticker), side, "market", "day")
    print("Market order of | " + api.get_account().buying_power/ getQuote(ticker) + " " + ticker + " " + side + " | completed.")


# while True:
#     if(api.get_clock().is_open):
#         print(getQuote(ticker))
#     else:
#         print("wms")
#     time.sleep(12)

class NeuralNetwork:
    def __init__(self, x, y):
        self.input      = x
        self.weights1   = np.random.rand(self.input.shape[1],4)
        self.weights2   = np.random.rand(4,1)
        self.y          = y
        self.output     = np.zeros(self.y.shape)

    def feedforward(self):
        self.layer1 = sigmoid(np.dot(self.input, self.weights1))
        self.output = sigmoid(np.dot(self.layer1, self.weights2))

    def backprop(self):
        # application of the chain rule to find derivative of the loss function with respect to weights2 and weights1
        d_weights2 = np.dot(self.layer1.T, (2*(self.y - self.output) * sigmoid_derivative(self.output)))
        d_weights1 = np.dot(self.input.T,  (np.dot(2*(self.y - self.output) * sigmoid_derivative(self.output), self.weights2.T) * sigmoid_derivative(self.layer1)))

        # update the weights with the derivative (slope) of the loss function
        self.weights1 += d_weights1
        self.weights2 += d_weights2

nn = NeuralNetwork(1,0)
nn.feedforward()
nn.backprop()
