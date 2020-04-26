import sys
import time
import requests
from bs4 import BeautifulSoup
import alpaca_trade_api as tradeapi
import json
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# ALPACA API INIT
api = tradeapi.REST('PKWS07EUH6HN0TVT14O2', 'A5Ffk2KHJ6UO10xiEqwrsRzh4G68e5Am3OlQ421m', "https://paper-api.alpaca.markets", api_version='v2')
alphavantage_api_key = "L9ORMXCSUYTKB325"

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
driver.set_window_position(-10000,0)

# pull data from cboe
URL = 'https://markets.cboe.com/us/equities/market_statistics/book_viewer/'
page = requests.get(URL)
cboe = BeautifulSoup(page.content, 'html.parser')

driver.get("https://markets.cboe.com/us/equities/market_statistics/book_viewer/")
html = driver.execute_script('return document.body.innerHTML;')
cboeData = BeautifulSoup(page.content, 'html.parser')
print([entry.text for entry in cboeData.findAll("div", {"class": "app__bd"})])

wholeTable = cboe.findAll("div", {"class": "app__bd"})
ticker = (cboe.find("input", {"id": "symbol0"}).get('value'))

# get last close for param: ticker
def getQuote(ticker):
    response = (requests.get("https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=" + ticker + "&apikey=" + alphavantage_api_key))
    data = response.content.decode('utf8').replace("'", '"')
    formatted_json = json.loads(data)

    if(not 'Note' in formatted_json):
        return float((formatted_json["Global Quote"]["05. price"]))
    else:
        driver.get("https://finance.yahoo.com/quote/" + ticker)
        html = driver.execute_script('return document.body.innerHTML;')
        yahoo_data = BeautifulSoup(html,'lxml')
        close_price = [entry.text for entry in yahoo_data.find_all('span', {'class':'Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)'})]
        return float(close_price[0])


# while True:
#     if(api.get_clock().is_open):
#         print(getQuote(ticker))
#     else:
#         print("wms")
#     time.sleep(12)
