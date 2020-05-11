import sys
import time
import requests
from bs4 import BeautifulSoup
import alpaca_trade_api as tradeapi
from iexfinance.stocks import Stock
import json
import re
import numpy as np

"""
    TODO:

    Finish decide
    Test submitOrder
    Finish getQuote
"""


# ALPACA API INIT
api = tradeapi.REST('PKWS07EUH6HN0TVT14O2', 'A5Ffk2KHJ6UO10xiEqwrsRzh4G68e5Am3OlQ421m', "https://paper-api.alpaca.markets", api_version='v2')
alphavantage_api_key = "L9ORMXCSUYTKB325"
iex_api_key = "Tpk_4bd3eca6cc5d45418180c6881292b18e"

# pull data from cboe: https://markets.cboe.com/us/equities/market_statistics/book/?mkt=edgx
CBOE_URL = 'https://markets.cboe.com/us/equities/market_statistics/book/?mkt=edgx'
page = requests.get(CBOE_URL)
cboe_data = BeautifulSoup(page.content, 'html.parser')

# Populate bids and asks arrays with order size data
def populateAsksBids(bid_share_count, bid_price, ask_share_count, ask_price):
    bids = []
    for x in range(len(bid_share_count)):
        bids.append([])
        bids[x].append(bid_share_count[x].text)
        bids[x].append(bid_price[x].text)

    asks = []
    for x in range(len(ask_share_count)):
        asks.append([])
        asks[x].append(ask_share_count[x].text)
        asks[x].append(ask_price[x].text)
    decide(asks, bids)

# Isolate necessary data
ticker = (cboe_data.find("input", {"id": "symbol0"}).get('value'))

bid_share_count = (cboe_data.findAll("td", {"class": "book-viewer__bid book-viewer__bid-shares"}))
ask_share_count = (cboe_data.findAll("td", {"class": "book-viewer__ask book-viewer__ask-shares"}))

ask_price = (cboe_data.findAll("td", {"class": "book-viewer__ask book-viewer__ask-price book-viewer-price"}))
bid_price = (cboe_data.findAll("td", {"class": "book-viewer__bid book-viewer__bid-price book-viewer-price"}))

def decide(asks, bids):
    for ask in asks:
        print(ask)
    for bid in bids:
        print(bid)

# get last close for param: ticker
def getQuote(symbol):
    # replace sandbox with cloud and replace api key
    iex_url = "https://sandbox.iexapis.com/stable/stock/" + symbol + "/quote?token=" + iex_api_key
    iex_data = requests.get(iex_url).content
    price_data = iex_data.decode('utf8').replace("'", '"')
    data = json.loads(price_data)
    s = json.loads(json.dumps(data, indent=4, sort_keys=True))
    return (s["latestPrice"])

def submitOrder(side, ticker):
    buying_power = (float(api.get_account().buying_power)) - 1000
    api.submit_order(ticker, round(buying_power / getQuote(ticker)), side, "market", "day")
    # print("Market order of | " + round(float(api.get_account().buying_power) / getQuote(ticker)) + " " + ticker + " " + side + " | completed.")


# while True:
#     if(api.get_clock().is_open):
#         populateAsksBids(bid_share_count, bid_price, ask_share_count, ask_price)
#     time.sleep(5)

print(getQuote("INO"))
