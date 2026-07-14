#!/home/iain/.venv/bin/python3

# GetSingleYahooPrice.py
# Ripped off from https://gist.github.com/stonefullstm/cbc789565cc521df89c29ead836c8cef
# Issue running YahooFinance directly from LibeOffice (liekly due to env)
# Instead run this script from there and return the desired price

import sys
import yfinance as yf

ticker = sys.argv[1]

yahooData = yf.Ticker(ticker)

try:
	if 'currentPrice' in yahooData.info:
		quoteVal = yahooData.info['currentPrice']
	elif 'regularMarketPrice' in yahooData.info:
		quoteVal = yahooData.info['regularMarketPrice']
except:
	try:
		if 'lastPrice' in yahooData.fast_info:
			quoteVal = yahooData.fast_info['lastPrice']	
	except:
		# Yahoo not always populating prices which gives error, so..
		quoteVal=-1

# Guy originally returning history(period="1d")["Close"].iloc[-1]

print(quoteVal)

