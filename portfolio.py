#!/usr/bin/python3

######################################################################################
# Name:			portfolio.py
# Author:		Iain Benson
# Description:	Portfolio monitor that grabs prices from Yahoo price feed
#				Allows secififcation of NAmes, Dps and to set target prices
# 
# Dependancies:	None
#
#####################################################################################
# Basic script to output Portfolio to console
# Can specify all time high (so as get output detailing how far off it is) and set Target Prices.


# Note:  installed yFinanc and can use that as alterntive.  Need to rewrite code and do individual 
# https://www.geeksforgeeks.org/get-financial-data-from-yahoo-finance-with-python/
# https://pypi.org/project/yfinance/

import requests
import collections
import os
import time, datetime
import yfinance as YahooFinance				# pip install yfinance --upgrade
from contextlib import redirect_stdout
import io

try:
	import json
except ImportError:
	import simplejson as json

# Assign Indexes into array
IDX_ACTUAL_TICKER = 0
IDX_FULL_NAME = 1
IDX_CURRENCY = 2
IDX_PRINT_DPS = 3
IDX_ALL_TIME_HIGH = 4		# Get this from FT market data
IDX_BUY_PRICE_ALERT  = 5	# Flag when it's reached my buy price
IDX_LAST_READ_PRICE = 6

# Other Defintions
NO_TARGET_PRICE	 =  -1
NO_ALL_TIME_HIGH =  -1

REFRESH_SECONDS = 180
YAHOO_RETRIES = 3


def clear(): 
	if os.name == 'nt':	# Windows
		os.system('cls') 
	else:				#Linux
		os.system('clear') 

def	SetupShareDictionaries(currDict, shareDictMultiAss, shareDictGrowth, shareDictIndexes, pmDict, shareDictWatchlist):
	"""Setup Ordered Dictionaries of shares / rates"""


	#				Yahoo Tkr	Ticker		FullName							Currency	Dps		AllTimeHigh		TargetPrice
	shareDictIndexes['^FTSE']	= ['FTSE 100',	'FTSE 100',							'GBX',		0,		7792,			NO_TARGET_PRICE]
	shareDictIndexes['^GSPC']	= ['S&P 500',	'S&P 500',							'USD',		0,		4720,			NO_TARGET_PRICE]
	#shareDictIndexes['EEM']		= ['EM USD',	'iShares Emerging ETF USD',			'USD',		1,		57.96,			NO_TARGET_PRICE] 
	#shareDictIndexes['VFEM.L']	= ['EM GBP',	'Vanguard Emergin ETF GBP',			'GBX',		1,		48.57,			NO_TARGET_PRICE] 

	pmDict['GC=F'] =			['Gold',	'Gold',								'USD',		0,		1838,			NO_TARGET_PRICE] 
	pmDict['SI=F'] =			['Silvr',	'Silver',							'USD',		2,		46.4,			NO_TARGET_PRICE]
	pmDict['CL=F'] =			['WTI',		'Crude',							'USD',		1,		140,			NO_TARGET_PRICE]
	#pmDict['CNQ.TO'] =			['CNQ',		'Canadian Natural Resources',		'CAD',		2,		67.19,			NO_TARGET_PRICE]
	#pmDict['PSK.TO'] =			['PSK',		'Prarie Sky Royalty',				'CAD',		2,		40.90,			NO_TARGET_PRICE]

	#shareDictMultiAss['CGT.L']  = ['CGT',	'Capital Gearing',					'GBX',		0,		5150,			NO_TARGET_PRICE]
	#shareDictMultiAss['PNL.L']  = ['PNL',	'Personal Assets',					'GBX',		0,		51166,			NO_TARGET_PRICE]
	#shareDictMultiAss['RCP.L']  = ['RCP',	'RIT Capital Partners',				'GBX',		0,		2760,			1200]
	#shareDictMultiAss['HANA.L'] = ['HANA',	'Hansa',							'GBX',		0,		215,			NO_TARGET_PRICE]

	#shareDictGrowth['SST.L']   =  ['SST',	'Scottish Oriental Smaller Cos',	'GBX',		0,		1292,			800] 
	#shareDictGrowth['0P00012PN5.L']  =  ['LTG',	'Lindsell Train Global D',		'GBX',		0,		304,			NO_TARGET_PRICE ]
	shareDictGrowth['BATS.L']  =  ['BATS',	'British American Tobacco',			'GBX',		0,		5530,			NO_TARGET_PRICE ]
	shareDictGrowth['DGE.L']   =  ['DGE',	'Deageo',							'GBX',		0,		4036,			3000] 
	shareDictGrowth['BRBY.L']   =  ['BRBY',	'Deageo',							'GBX',		0,		2591,			3000] 
	#shareDictGrowth['MO']      =  ['MO',	'Altria',							'USD',		2,		71.42,			NO_TARGET_PRICE ]

	shareDictGrowth['RIG']     =  ['RIG',	'Transocean',						'USD',		2,		18.82,			NO_TARGET_PRICE]
	shareDictGrowth['BORR']    =  ['BORR',	'Borr Drilling',					'USD',		2,		8.78,			NO_TARGET_PRICE]
	#shareDictGrowth['DB1.DE']  =  ['DB1',	'Deutsche Borse',					'EUR',		1,		172.55,			NO_TARGET_PRICE ]
	#shareDictGrowth['PBR-A']     =  ['PBR-A','Petrobas Perfs',						'USD',		2,		14.92,			NO_TARGET_PRICE]
	#shareDictGrowth['EC']	   =  ['EC',	'EcoPetrol',						'USD',		2,		26.93,			NO_TARGET_PRICE]
	#shareDictGrowth['WG.L']    =  ['WG',	'Wood Group',						'GBX',		1,		900,			120] 
	shareDictGrowth['ECOR.L']  =  ['ECOR',	'Ecora',							'GBX',		1,		350,			NO_TARGET_PRICE] 
	shareDictGrowth['ALS.TO']  =  ['ALS',	'Altius Minerals',					'CAD',		2,		24.1,			4]
	shareDictGrowth['LIF.TO']  =  ['LIF',	'LIORC',							'CAD',		2,		49.61,			NO_TARGET_PRICE]
	shareDictGrowth['VALE']    =  ['VALE',	'Vale',								'USD',		2,		22.81,			NO_TARGET_PRICE]
	shareDictGrowth['GLEN.L']  =  ['GLEN',	'Glencore',							'GBX',		1,		475,			NO_TARGET_PRICE]
	#shareDictGrowth['AMR']    =  ['AMR',	'Vale',								'USD',		2,		439,			NO_TARGET_PRICE]
	shareDictGrowth['HCC']    =  ['HCC',	'Vale',								'USD',		2,		70.62,			NO_TARGET_PRICE]
	#shareDictGrowth['MLX.AX']  =  ['MLX',	'Metals X',							'AUD',		2,		0.74,			NO_TARGET_PRICE]
	shareDictGrowth['ADT1.L']  =  ['ADT',	'ADT',								'GBX',		1,		218,			NO_TARGET_PRICE]
	shareDictGrowth['WHC.AX']  =  ['WHC',	'WHC',								'AUD',		2,		10.52,			NO_TARGET_PRICE]
	#shareDictGrowth['TGA.L']   =  ['TGA',	'TGA',								'GBP',		2,		1900,			NO_TARGET_PRICE]
	#shareDictGrowth['IBZL.L']  =  ['IBZL',	'iShares Brazil',					'GBX',		1,		4004,			NO_TARGET_PRICE]
	#shareDictGrowth['WPM.L']   =  ['WPM',		'Wheaton Precious',					'GBX',		0,		3345,			NO_TARGET_PRICE]


	currDict['GBPEUR=X']	=	['GBPEUR',	'GBP to EUR XRate',					'',			4,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	currDict['GBPUSD=X']	=	['GBPUSD',	'GBP to USD XRate',					'',			4,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	currDict['GBPCAD=X']	=	['GBPCAD',	'GBP to CAD XRate',					'',			4,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	#currDict['GBPAUD=X']	=	['GBPAUD',	'GBP to AUD XRate',					'',			4,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	#currDict['BTC-USD']		=	['BTC',		'BITCOIN',							'',			0,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	#currDict['ETH-USD']		=	['ETH',		'ETHER',							'',			0,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]

	#shareDictWatchlist[['ADM']  =  ['ADM',	'Archer Danlels Midland',			'USD',		2,		96.91,			NO_TARGET_PRICE]
	#shareDictWatchlist['CNQ.TO']  =  ['CNQ',	'Canadian Natural Resources',		'CAD',		1,		85.2,			NO_TARGET_PRICE]
	#shareDictWatchlist['AGT.L']   =  ['AGT',	'AVI Growth Trust',					'GBX',		0,		222,			NO_TARGET_PRICE]
	#shareDictWatchlist['AFM.V']   =  ['AFM',	'Alphamin',							'CAD',		2,		1.39,			NO_TARGET_PRICE]
	#shareDictWatchlist['LSEG.L']  =  ['LSEG',	'Metal Tiger',						'GBX',		0,		9990,			NO_TARGET_PRICE] 
	#shareDictWatchlist['X.TO']    =  ['X',		'TMX',								'CAD',		1,		140.85,			NO_TARGET_PRICE ]
	#shareDictWatchlist['ASX.AX']  =  ['ASX',	'ASX',								'AUD',		1,		92.9,			NO_TARGET_PRICE ]
	#shareDictWatchlist['ICE']     =  ['ICE',	'Intercontenental Exchange',		'USD',		2,		138.46,			NO_TARGET_PRICE]
	#shareDictWatchlist['FGT.L']   =  ['FGT',	'FGT',								'GBX',		0,		958,			NO_TARGET_PRICE ]
	#shareDictWatchlist['CKN.L']   =  ['CKN',	'Clarksons',						'GBX',		0,		4055,			NO_TARGET_PRICE ]
	shareDictWatchlist['AJOT.L']  =  ['AJOT',	'AVI Japan Global Ops',				'GBX',		1,		127,			NO_TARGET_PRICE]
	#shareDictWatchlist['YCA.L']   =  ['YCA',	'Anglo Pacific',					'GBX',		0,		444,			100] 
	#shareDictWatchlist['FIL.TO']  =  ['FIL',	'Filo',								'CAD',		2,		27.8,			NO_TARGET_PRICE]
	#shareDictWatchlist['NTR']     =  ['NTR',	'Nutrien',							'USD',		2,		104,			NO_TARGET_PRICE]
	#shareDictWatchlist['VAL']     =  ['VAL',	'Valaris',							'USD',		2,		76.8,			NO_TARGET_PRICE ]
	#shareDictWatchlist['SU.TO']   =  ['SU',	'Labrador Iron Ore',					'CAD',		2,		54.78,			NO_TARGET_PRICE]
	shareDictWatchlist['FRU.TO']  =  ['FRU',	'Freehold Royalties',				'CAD',		2,		27.78,			NO_TARGET_PRICE]
	#shareDictWatchlist['PSK.TO']  =  ['PSK',	'Prarie Sky',						'CAD',		2,		42.39,			NO_TARGET_PRICE]
	shareDictWatchlist['TPZ.TO']  =  ['TPZ',	'Topaz',							'CAD',		2,		23.99,			NO_TARGET_PRICE]
	#shareDictWatchlist['ENX.PA']  =  ['ENX',	'Euronext',							'EUR',		1,		98.3,			NO_TARGET_PRICE ]
	shareDictWatchlist['ASX.AX']  =  ['ASX',	'ASX',								'AUD',		1,		92.9,			NO_TARGET_PRICE ]
	shareDictWatchlist['CME']     =  ['CME',	'Intercontenental Exchange',		'USD',		2,		238,			NO_TARGET_PRICE]
	shareDictWatchlist['S68.SI']  =  ['S68',	'Singapore Exchange',				'SGD',		2,		11.9,			NO_TARGET_PRICE]
	shareDictWatchlist['DB1.DE']  =  ['DB1',	'Deutsche Borse',					'EUR',		1,		194,			NO_TARGET_PRICE ]
	#shareDictWatchlist['CRL']  =  ['CRL',	'Charles River Lans',				'USD',		2,		458.3,			NO_TARGET_PRICE]
	shareDictWatchlist['SBSW']  =  ['SBSW',	'SBSW',								'USD',		2,		19.12,			NO_TARGET_PRICE]
	shareDictWatchlist['SLP.L']  =  ['SLP',	'SLP',								'GBP',		2,		139,			NO_TARGET_PRICE]
	shareDictWatchlist['FNV']     =  ['FNV',	'Franco Nevada',					'USD',		2,		158.95,			NO_TARGET_PRICE]



def GetTabs(Ticker):
	"""Get the number of tabs depending on length of ticker so stuff lines up"""

	# Bit hackey but doesn't need to be more complicated
	endTab='\t\t'
	if len(Ticker) > 5:
		endTab='\t'

	return endTab


def PrintSharePriceWithDPS(fPrice, v):
	"""Print the share price with DPS as specified in shareDict"""
 

	# Copy price to string with correct DPs
	if(v[IDX_PRINT_DPS] == 0):
		sPrice = "%0.0f"%fPrice
	elif(v[IDX_PRINT_DPS] == 1):
		sPrice = "%0.1f"%fPrice
	elif(v[IDX_PRINT_DPS] == 2):
		sPrice = "%0.2f"%fPrice
	elif(v[IDX_PRINT_DPS] == 3):
		sPrice = "%0.3f"%fPrice
	elif(v[IDX_PRINT_DPS] == 4):
		sPrice = "%0.4f"%fPrice
	elif(v[IDX_PRINT_DPS] == 5):
		sPrice = "%0.5f"%fPrice
	else:
		sPrice = "%0.0f"%fPrice

	# Print price, space padded to 8 Chars
	print(sPrice.ljust(8), end='' ) 


def PrintPercentOffAllTimeHigh(fPrice, v):
	"""Print the percentage value off of the all time high.  Now in Techni-colour!"""

	# If we want to sko this then just return
	if v[IDX_ALL_TIME_HIGH] == NO_ALL_TIME_HIGH:
		return

	# Print amount off of all time high
	percentOff = (1 - (fPrice/v[IDX_ALL_TIME_HIGH])) * 100
	if percentOff > 0:
		print("\033[0;91m -", end='' ) # Turn On Red
	else:
		print("\033[0;92m +", end='' ) # Turn On Green

	print("%0.0f"%percentOff + "%", end='' ) 
	print("\033[00m", end=' ' ) # Turn colour back to normal


def CheckAgainstTargetPrice(fPrice, v):
	"""Checks the current price against the target price and prints if it is reached"""

	if v[IDX_BUY_PRICE_ALERT] != NO_TARGET_PRICE and fPrice < v[IDX_BUY_PRICE_ALERT]:
		print ("BUY")
	else:
		print('')



def GetAndPrintSharePrices(shareDict, inputIndexName):
	"""Fetches the share prices from Yahoo.  Note previous yahoo_finance stopped working and they changed to json"""


	# Was getting 403 forbidden error.  Putting in USer Agent stopped this
	#headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:111.0) Gecko/20100101 Firefox/111.0'}

	# Yahoo changed to Now output json like:
	#yahooQuery = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
	#yahooQuery = ""

	# For each item, print the price
	for k, v in shareDict.items():

		price=""
		yahooData = YahooFinance.Ticker(k)

		try:
			# price = yahooData.info[indexName]
			# https://stackoverflow.com/questions/61104362/how-to-get-actual-stock-prices-with-yfinance
			# Someties its currentPrice, regularMarketprice or neither
			if 'currentPrice' in yahooData.info:
				price = yahooData.info['currentPrice']
			elif 'regularMarketPrice' in yahooData.info:
				price = yahooData.info['regularMarketPrice']
			else:
				# Use history
					
				#Getting annoying warnings from yahoodata.history.  Cant see flag to turn off so turn off all output
				#with redirect_stdout(io.StringIO()) as f:
				todayData = yahooData.history(period='1d')
				price = todayData['Close'][0]

			#append last read price in case fail to read next time.
			if len(v)==6:
				shareDict[k].append(price)
			else:
				v[IDX_LAST_READ_PRICE] = price 

			print("  ", end='')
	
		except:
			# If any http error in fetching info then get an exception
			# cath it and then try the fat_info which has worked previously
			try:
				if 'lastPrice' in yahooData.fast_info:			#this has been populated when 'info' wasn't
					price = yahooData.fast_info['lastPrice']
			except:
				# Neither info nor fast_info working.  Try cached values
				if len(v)==7:
					# Use the cached value
					price = v[IDX_LAST_READ_PRICE]
					print(" \033[0;91mc\033[00m", end='' ) # Print red 'c' to show cached
				else:
					print("issue fetching price")
					#print(yahooData.info)
		
		print(v[IDX_ACTUAL_TICKER].ljust(10) , end='')

		# Get the index in the pricesList and get da price
		index = list(shareDict.keys()).index(k)

		# Assuming we got a price, print it
		if price:
			fPrice = float(price)
			PrintSharePriceWithDPS(fPrice, v)
			PrintPercentOffAllTimeHigh(fPrice, v)
			CheckAgainstTargetPrice(fPrice, v)



def WaitaBitForYahoo():
	"""Yahoo sporadically returning errors, think throttling.  Add a wait."""
	time.sleep(1)



if __name__ == "__main__":

	# As running at startup, enter a pause to give internet time to come up	
	time.sleep(5)

	# Use Ordered dicts to store all shares we're fetching.
	currDict = collections.OrderedDict() 
	shareDictMultiAss = collections.OrderedDict() 
	shareDictGrowth = collections.OrderedDict() 
	shareDictIndexes = collections.OrderedDict()
	shareDictWatchlist = collections.OrderedDict()
	pmDict = collections.OrderedDict()

	# Failure to reads causing issues, cache last read and output that.
	currDict_cached = collections.OrderedDict() 
	shareDictMultiAss_cached = collections.OrderedDict() 
	shareDictGrowth_cached = collections.OrderedDict() 
	shareDictIndexes_cached = collections.OrderedDict()
	shareDictWatchlist_cached = collections.OrderedDict()
	pmDict_cached = collections.OrderedDict()


	SetupShareDictionaries(currDict, shareDictMultiAss, shareDictGrowth, shareDictIndexes, pmDict, shareDictWatchlist)

	# This runs every half hour or so, just leaving it in a terminal
	while True:
		clear()

		print("= Currencies =")
		GetAndPrintSharePrices(currDict, "bid")

		print("\n= Indices =")
		GetAndPrintSharePrices(shareDictIndexes, 'bid')

		print("\n= Commodities =")
		GetAndPrintSharePrices(pmDict, 'bid')

		#print("\n= Multi Asset Portfolio =")
		#GetAndPrintSharePrices(shareDictMultiAss, 'currentPrice')

		print("\n= Growth/Pen Portfolio =")
		GetAndPrintSharePrices(shareDictGrowth, 'currentPrice')

		print("\n= Watchlist =")
		GetAndPrintSharePrices(shareDictWatchlist,'currentPrice')

		print("\nLast Runtime: ", end="")
		print(time.strftime("%H:%M",time.localtime()))
		
		# Save querying yahoo unnecessarily.  only once per hour outside market hours
		if datetime.datetime.today().weekday() < 5:
			# If market hours then run frequently
			time.sleep(REFRESH_SECONDS)
		else:
			# WEEKEND.  IF pause display refreshes, so just set big time.
			time.sleep(3600)



