# lvl_2

A simple algo trading Python script that makes decisions based on Level II market data.

# How it Works

Every 5 seconds, the script will check if the stock market is open and pull all asks and bids from the Level II data API. If the total number of asks is less than the number of bids, then sell the position. Otherwise, buy the position and set a stop loss at 3% below current price.
