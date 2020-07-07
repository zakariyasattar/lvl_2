import sys
import time
import requests
import math
from bs4 import BeautifulSoup
import alpaca_trade_api as tradeapi
from iexfinance.stocks import Stock
import json
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np

"""
    TODO:

    PSUEDO: Once one target price is found and is unchanching, stick with it
    keep making sure that asks > bids even after position is assumed (make a routine check function)
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

iex_api_key = "pk_0ebcc25609b045788b2b29b9c57f1bb6"
iex_sandbox = "Tpk_4bd3eca6cc5d45418180c6881292b18e"

# pull data from cboe: https://markets.cboe.com/us/equities/market_statistics/book/?mkt=edgx
driver.get("https://markets.cboe.com/us/equities/market_statistics/book/?mkt=edgx")
html = driver.execute_script('return document.body.innerHTML;')
cboe_data = BeautifulSoup(html, 'lxml')

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
    asks.reverse()
    bids.reverse()

    if(len(api.list_positions()) == 0):
        ask_share_count = 0
        bid_share_count = 0
        selected_ask = 0
        selected_bid = 0

        for ask in asks:
            ask_shares = (int(ask[0].replace(',', '')))

            if(asks.index(ask) > 0):
                if(ask_shares > initial_ask_share_count):
                    selected_ask = asks.index(ask)
            else:
                initial_ask_share_count = ask_shares
            ask_share_count = ask_share_count + ask_shares

        for bid in (bids):
            bid_shares = (int(ask[0].replace(',', '')))

            if(bids.index(bid) > 0):
                if(bid_shares > initial_bid_share_count):
                    selected_bid = bids.index(bid)
            else:
                initial_bid_share_count = bid_shares
            bid_share_count = bid_share_count + bid_shares

        if(ask_share_count > bid_share_count):
            submitOrder(ticker)

    else:
        # DETERMINE RIGHT PRICE TO SELL AT
        qty = api.get_position(ticker).qty

        #####
        target_price = api.get_position(ticker).limit_price
        #####

        for ask in asks:
            if(target_price == ""):
                ask_shares = (int(ask[0].replace(',', '')))
                ask_target_price = (float(ask[1].replace(',', '')))

                if((ask_shares * ask_target_price) > 5000 and len(api.list_positions()) > 0):
                    api.cancel_all_orders()
                    time.sleep(2)
                    api.submit_order(ticker, qty, "sell", "limit", "day", limit_price = ask_target_price)

                    print(ask_target_price)
                    print("Sold " + str(qty) + " shares of " + ticker)
            else:

                #PSUEDO CHECK UNDER REAL CIRCUMSTANCES
                ask_shares = (int(ask[0].replace(',', '')))
                ask_target_price = (float(ask[1].replace(',', '')))

                if(ask_target_price == target_price):
                    if(ask_shares * ask_target_price > 5000):
                    else:
                        api.cancel_all_orders()


# get last close for param: ticker
def getQuote(symbol):
    # replace sandbox with cloud and replace api key
    iex_url = "https://cloud.iexapis.com/stable/stock/" + symbol + "/quote?token=" + iex_api_key
    iex_data = requests.get(iex_url).content

    price_data = json.loads(json.dumps(json.loads(iex_data.decode('utf8').replace("'", '"')), indent=4, sort_keys=True))
    return (price_data["latestPrice"])

def submitOrder(ticker):
    buying_power = (float(api.get_account().buying_power))
    price = getQuote(ticker)

    qty = math.floor(buying_power / price)

    api.submit_order(ticker, qty, "buy", "market", "day")
    time.sleep(2)
    api.submit_order(ticker, qty, 'sell', "stop", "day", stop_price = price - (price * .03))

    print("Market order of | " + str(qty) + " " + ticker + " " + "buy" + " | completed.")


while True:
    if(api.get_clock().is_open):
        populateAsksBids(bid_share_count, bid_price, ask_share_count, ask_price)
    time.sleep(5)
