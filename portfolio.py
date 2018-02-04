# Basic script to output Portfolio to console
# Can specify all time high (so as get output detailing how far off it is) and set Target Prices.

import requests
import collections
import os
import time

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

# Other Defintions
NO_TARGET_PRICE	=  -1

def	SetupShareDictionaries(currDict, shareDictMultiAss, shareDictGrowth, shareDictIndexes, pmDict):
	"""Setup Ordered Dictionaries of shares / rates"""

	currDict['GBPEUR'] = ['GBPEUR']
	currDict['GBPUSD'] = ['GBPUSD']

	#				Yahoo Tkr	Ticker		FullName							Currency	Dps		AllTimeHigh		TargetPrice
	shareDictIndexes['^FTSE'] = ['FTSE 100','FTSE 100',							'GBX',		0,		7792,			NO_TARGET_PRICE]
	shareDictIndexes['^GSPC'] = ['S&P 500',	'S&P 500',							'USD',		0,		2872,			NO_TARGET_PRICE]

	pmDict['GC=F'] =			['Gold',	'Gold',								'USD',		0,		1838,			NO_TARGET_PRICE] 
	pmDict['SI=F'] =			['Silvr',	'Silver',							'USD',		2,		46.4,			NO_TARGET_PRICE]
	pmDict['CL=F'] =			['Crude',	'Crude',							'USD',		2,		147,			NO_TARGET_PRICE]

	shareDictMultiAss['PNL.L'] = ['PNL',	'Personal Assets',					'GBX',		0,		41590,			NO_TARGET_PRICE]
	shareDictMultiAss['RCP.L'] = ['RCP',	'RIT Capital Partners',				'GBX',		0,		 2010,			1800]
	shareDictMultiAss['CGT.L'] = ['CGT',	'Capital Gearing',					'GBX',		0,		 3999,			3800]
	shareDictMultiAss['RICA.L'] = ['RICA',	'Ruffer',							'GBX',		1,		 242,			NO_TARGET_PRICE]
	shareDictMultiAss['BTEM.L'] = ['BTEM',	'British Empire',					'GBX',		0,		 755,			600]
	shareDictMultiAss['CLDN.L'] = ['CLDN',	'Caledonia',						'GBX',		0,		 2907,			2500]
	shareDictMultiAss['HANA.L'] = ['HANA',	'Hansa Trust',						'GBX',		0,		 1030,			800]
	shareDictMultiAss['HAST.L'] = ['HAST',	'Henderson Alternative',			'GBX',		0,		 305,			250]

	shareDictGrowth['SST.L'] =  ['SST',		'Scottish Oriental Smaller Cos',	'GBX',		0,		 1098,			800] 
	shareDictGrowth['AAS.L'] =  ['AAS',		'Aberdeen Asian Smaller Cos',		'GBX',		0,		 1143,			800] 
	shareDictGrowth['BRFI.L'] = ['BRFI',	'Blackrock Frontiers',				'GBX',		0,		 169,			130] 
	shareDictGrowth['AFMC.L'] = ['AFMC',	'Aberdeen Frontiers',				'GBX',		1,		 68.2,			50]
	shareDictGrowth['ANII.L'] = ['ANII',	'Aberdeen New India',				'GBX',		0,		 470,			400]
	shareDictGrowth['JII.L'] =  ['JII',		'JP Morgan Indian',					'GBX',		0,		 786,			600]
	shareDictGrowth['IGC.L'] =  ['IGC',		'India Capital Growth',				'GBX',		0,		 120,			70]
	shareDictGrowth['HRI.L'] =  ['HRI',		'Herald',							'GBX',		0,		 1230,			800] 
	shareDictGrowth['BIOG.L'] = ['BIOG',	'Biotech Growth Trust',				'GBX',		0,		 836,			500]
	shareDictGrowth['PIN.L'] =  ['PIN',		'Pantheon',							'GBX',		0,		 1929,			1200] 
	shareDictGrowth['HGT.L'] =  ['HGT',		'HG Capital',						'GBX',		0,		 1797,			1200] 
	shareDictGrowth['IBTS.L'] = ['IBTS',	'iShares US Treas 1-3',				'GBX',		0,		 109,			85]

def GetTabs(Ticker):
	"""Get the number of tabs depending on length of ticker so stuff lines up"""

	# Bit hackey but doesn't need to be more complicated
	endTab='\t\t'
	if len(Ticker) > 5:
		endTab='\t'

	return endTab


def PrintSharePriceWithDPS(fPrice, v):
	"""Print the share price with DPS as specified in shareDict"""

	# How many tabs to insert after price
	endTab='\t'
	
	if(v[IDX_PRINT_DPS] == 0):
		print("%0.0f"%fPrice, end=endTab ) 
	elif(v[IDX_PRINT_DPS] == 1):
		print("%0.1f"%fPrice, end=endTab ) 
	elif(v[IDX_PRINT_DPS] == 2):
		print("%0.2f"%fPrice, end=endTab ) 
	else:
		print(fPrice, end=endTab)


def PrintPercentOffAllTimeHigh(fPrice, v):
	"""Print the percentage value off of the all time high.  Now in Techni-colour!"""

	# Print amount off of all time high
	percentOff = (1 - (fPrice/v[IDX_ALL_TIME_HIGH])) * 100
	if percentOff > 0:
		print("\033[0;91m -", end='' ) # Turn On Red
	else:
		print("\033[0;92m +", end='' ) # Turn On Green

	print("%0.0f"%percentOff + "%", end='' ) 
	print("\033[00m", end=' ' ) # Turn colour back to normal


def CheckAgainstTargetPrice(fPrice, v):
	"""Checks teh current price against the target price and prints if it is reached"""

	if v[IDX_BUY_PRICE_ALERT] != NO_TARGET_PRICE and fPrice < v[IDX_BUY_PRICE_ALERT]:
		print ("BUY")
	else:
		print('')



def GetAndPrintSharePrices(shareDict):
	"""Fetches the share prices from Yahoo.  Note previous yahoo_finance stopped working and they changed to json"""

	# Yahoo changed to Now output json like:
	# https://query1.finance.yahoo.com/v7/finance/quote?symbols=VOD.L,BARC.L
	yahooQuery = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
	for k,w in shareDict.items():
		yahooQuery=yahooQuery + "," + k

	yahooJSON = requests.get(yahooQuery)
	yahooPriceInfo = json.loads(yahooJSON.text)
	
	# Same order as in URL, where [0] is First item in url, [1] 2nd in url etc.
	pricesList = yahooPriceInfo["quoteResponse"]["result"]

	# For each item, print the price
	for k, v in shareDict.items():

		tabs = GetTabs(v[IDX_ACTUAL_TICKER])
		print("  " + v[IDX_ACTUAL_TICKER] , end=tabs)

		# Get the index in the pricesList and get da price
		index = list(shareDict.keys()).index(k)
		price = pricesList[index]['regularMarketPrice']

		# Assuming we got a price, print it
		if price:
			fPrice = float(price)
			PrintSharePriceWithDPS(fPrice, v)
			PrintPercentOffAllTimeHigh(fPrice, v)
			CheckAgainstTargetPrice(fPrice, v)
			

def GetAndPrintCurrencies(currDict, refreshNeeded):
	"""Fetches the share Currencies from Yahoo!"""
	for k, v in currDict.items():
		item = Currency(k)
		currDict[k][IDX_SHARE_OBJ] = item
		print("  " + v[IDX_ACTUAL_TICKER] + "\t", end='')
		if refreshNeeded:
			v[IDX_SHARE_OBJ].refresh()
		print(v[IDX_SHARE_OBJ].get_rate())


if __name__ == "__main__":


	# Use Ordered dicts to store all shares we're fetching.
	currDict = collections.OrderedDict() 
	shareDictMultiAss = collections.OrderedDict() 
	shareDictGrowth = collections.OrderedDict() 
	shareDictIndexes = collections.OrderedDict()
	pmDict = collections.OrderedDict()
	SetupShareDictionaries(currDict, shareDictMultiAss, shareDictGrowth, shareDictIndexes, pmDict)

	# This runs every half hour or so, just leaving it in a terminal
	while True:
		os.system('cls')


		#print("= Currencies =\n==============")
		#GetAndPrintCurrencies(currDict, NeedRefresh)

		print("\n\n= Indices =\n===========")
		GetAndPrintSharePrices(shareDictIndexes)

		print("\n\n= Commodities =\n==============")
		GetAndPrintSharePrices(pmDict)

		print("\n\n= Multi Asset Portfolio =\n=========================")
		GetAndPrintSharePrices(shareDictMultiAss)

		print("\n\n= Growth Portfolio =\n=====================")
		GetAndPrintSharePrices(shareDictGrowth)


		print("\nLast Runtime: ", end="")
		print(time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()))
		time.sleep(1800)

