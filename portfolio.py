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

import requests
import collections
import os
import time, datetime

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
NO_TARGET_PRICE	 =  -1
NO_ALL_TIME_HIGH =  -1

REFRESH_SECONDS = 300

def clear(): 
	if os.name == 'nt':	# Windows
		os.system('cls') 
	else:				#Linux
		os.system('clear') 

def	SetupShareDictionaries(currDict, shareDictMultiAss, shareDictGrowth, shareDictIndexes, pmDict):
	"""Setup Ordered Dictionaries of shares / rates"""


	#				Yahoo Tkr	Ticker		FullName							Currency	Dps		AllTimeHigh		TargetPrice
	shareDictIndexes['^FTSE']	= ['FTSE 100',	'FTSE 100',							'GBX',		0,		7792,			NO_TARGET_PRICE]
	shareDictIndexes['^GSPC']	= ['S&P 500',	'S&P 500',							'USD',		0,		4128,			NO_TARGET_PRICE]
	#shareDictIndexes['EEM']		= ['EM USD',	'iShares Emerging ETF USD',			'USD',		1,		57.96,			NO_TARGET_PRICE] 
	#shareDictIndexes['VFEM.L']	= ['EM GBP',	'Vanguard Emergin ETF GBP',			'GBX',		1,		48.57,			NO_TARGET_PRICE] 

	pmDict['GC=F'] =			['Gold',	'Gold',								'USD',		0,		1838,			NO_TARGET_PRICE] 
	pmDict['SI=F'] =			['Silvr',	'Silver',							'USD',		2,		46.4,			NO_TARGET_PRICE]
	pmDict['CL=F'] =			['WTI',		'Crude',							'USD',		1,		140,			NO_TARGET_PRICE]
	pmDict['OR.TO'] =			['OR',		'Osisko',							'CAD',		2,		18.40,			NO_TARGET_PRICE]
	pmDict['CNQ.TO'] =			['CNQ',		'Suncor',							'CAD',		2,		55.19,			NO_TARGET_PRICE]
	#pmDict['PSK.TO'] =			['PSK',		'Prarie Sky Royalty',				'CAD',		2,		40.90,			NO_TARGET_PRICE]

	shareDictMultiAss['CGT.L']  = ['CGT',	'Capital Gearing',					'GBX',		0,		5150,			NO_TARGET_PRICE]
	shareDictMultiAss['PNL.L']  = ['PNL',	'Personal Assets',					'GBX',		0,		51166,			NO_TARGET_PRICE]
	shareDictMultiAss['RCP.L']  = ['RCP',	'RIT Capital Partners',				'GBX',		0,		2760,			1200]
	#shareDictMultiAss['HANA.L'] = ['HANA',	'Hansa',							'GBX',		0,		215,			NO_TARGET_PRICE]
	#shareDictMultiAss['AGT.L'] = ['AGT',	'AVI Growth Trust',					'GBX',		0,		1010,			460]

	shareDictGrowth['SST.L']   =  ['SST',	'Scottish Oriental Smaller Cos',	'GBX',		0,		1292,			600] 
	shareDictGrowth['0P00012PN5.L']  =  ['LTG',	'Lindsell Train Global D',		'GBX',		0,		304,			NO_TARGET_PRICE ]
	shareDictGrowth['BATS.L']  =  ['BATS',	'British American Tobacco',			'GBX',		0,		5530,			NO_TARGET_PRICE ]
	shareDictGrowth['DB1.DE']  =  ['DB1',	'Deutsche Borse',					'EUR',		1,		172.55,			NO_TARGET_PRICE ]
	shareDictGrowth['X.TO']    =  ['X',		'TMX',								'CAD',		1,		140.85,			NO_TARGET_PRICE ]
	shareDictGrowth['AJOT.L']  =  ['AJOT',	'AVI Japan Global Ops',				'GBX',		1,		127,			NO_TARGET_PRICE]
	shareDictGrowth['SU.TO']   =  ['SU',	'Suncor',							'CAD',		2,		53.5,			NO_TARGET_PRICE]
	shareDictGrowth['FRU.TO']  =  ['FRU',	'Freehold Royalties',				'CAD',		2,		27.78,			NO_TARGET_PRICE]
	shareDictGrowth['PSK.TO']  =  ['PSK',	'Prarie Sky',						'CAD',		2,		42.39,			NO_TARGET_PRICE]
	shareDictGrowth['ALS.TO']  =  ['ALS',	'Altius Minerals',					'CAD',		2,		28.8,			4]
	shareDictGrowth['APF.L']   =  ['APF',	'Anglo Pacific',					'GBX',		1,		350,			66] 
	shareDictGrowth['GLEN.L']  =  ['GLEN',	'Glencore',							'GBX',		1,		475,			NO_TARGET_PRICE]
	shareDictGrowth['ADT1.L']  =  ['ADT',	'ADT',								'GBX',		1,		172,			NO_TARGET_PRICE]
	#shareDictGrowth['IMB.L']  = ['IMB'	,	'Imperial Brands',					'GBX',		0,		4005,			NO_TARGET_PRICE ]
	#shareDictGrowth['CKN.L']  = ['CKN',		'Clarksons',						'GBX',		0,		3420,			NO_TARGET_PRICE ]
	#shareDictGrowth['LSEG.L']  = ['LSEG',	'LSEG'		,						'GBX',		0,		9900,			NO_TARGET_PRICE ]
	#shareDictGrowth['ENX.PA']  = ['ENX',	'Euronext',							'EUR',		2,		105.7,			NO_TARGET_PRICE ]
	#shareDictGrowth['FGT.L']   = ['FGT',	'FGT',								'GBX',		0,		958,			NO_TARGET_PRICE ]
	#shareDictGrowth['ULVR.L']  = ['ULVR',	'ULVR',								'GBX',		0,		5196,			NO_TARGET_PRICE ]
	#shareDictGrowth['DGE.L']   = ['DGE',	'DGE',								'GBX',		0,		3503,			NO_TARGET_PRICE ]


	currDict['GBPEUR=X']	 =	['GBPEUR',	'GBP to EUR XRate',					'',			4,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	currDict['GBPUSD=X']	=	['GBPUSD',	'GBP to USD XRate',					'',			4,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	currDict['GBPCAD=X']	=	['GBPCAD',	'GBP to CAD XRate',					'',			4,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	#currDict['GBPAUD=X']	=	['GBPAUD',	'GBP to AUD XRate',					'',			4,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	#currDict['BTC-USD']		=	['BTC',		'BITCOIN',							'',			0,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	#currDict['ETH-USD']		=	['ETH',		'ETHER',							'',			0,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]

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



def GetAndPrintSharePrices(shareDict):
	"""Fetches the share prices from Yahoo.  Note previous yahoo_finance stopped working and they changed to json"""


	# Was getting 403 forbidden error.  Putting in USer Agent stopped this
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0'}

	# Yahoo changed to Now output json like:
	# https://query1.finance.yahoo.com/v7/finance/quote?symbols=VOD.L,BARC.L
	yahooQuery = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
	for k,w in shareDict.items():
		yahooQuery=yahooQuery + "," + k

	try:
		yahooJSON = requests.get(yahooQuery,headers=headers)
		#print(yahooJSON)
		yahooPriceInfo = json.loads(yahooJSON.text)
	except:
		print("Issue fetching prices")
		return

	# Same order as in URL, where [0] is First item in url, [1] 2nd in url etc.
	pricesList = yahooPriceInfo["quoteResponse"]["result"]

	# For each item, print the price
	for k, v in shareDict.items():

		tabs = GetTabs(v[IDX_ACTUAL_TICKER])
		print("  " + v[IDX_ACTUAL_TICKER].ljust(10) , end='')

		# Get the index in the pricesList and get da price
		index = list(shareDict.keys()).index(k)

		# At times it appears regularMarketPrice might not be there, giving index out of range error
		try:
			price = pricesList[index]['regularMarketPrice']
		except:
			print("Issue fetching prices")
			return

		# Assuming we got a price, print it
		if price:
			fPrice = float(price)
			PrintSharePriceWithDPS(fPrice, v)
			PrintPercentOffAllTimeHigh(fPrice, v)
			CheckAgainstTargetPrice(fPrice, v)
			


if __name__ == "__main__":

	# As running at startup, enter a pause to give internet time to come up	
	time.sleep(5)

	# Use Ordered dicts to store all shares we're fetching.
	currDict = collections.OrderedDict() 
	shareDictMultiAss = collections.OrderedDict() 
	shareDictGrowth = collections.OrderedDict() 
	shareDictIndexes = collections.OrderedDict()
	pmDict = collections.OrderedDict()
	SetupShareDictionaries(currDict, shareDictMultiAss, shareDictGrowth, shareDictIndexes, pmDict)

	# This runs every half hour or so, just leaving it in a terminal
	while True:
		clear()

		#print("= Currencies =")
		GetAndPrintSharePrices(currDict)

		print("\n= Indices =")
		GetAndPrintSharePrices(shareDictIndexes)

		print("\n= Commodities =")
		GetAndPrintSharePrices(pmDict)

		print("\n= Multi Asset Portfolio =")
		GetAndPrintSharePrices(shareDictMultiAss)

		print("\n= Growth Portfolio =")
		GetAndPrintSharePrices(shareDictGrowth)


		print("\nLast Runtime: ", end="")
		print(time.strftime("%H:%M",time.localtime()))
		
		# Check if weekend
		if datetime.datetime.today().weekday() < 5:
			# run frequently
			time.sleep(REFRESH_SECONDS)
		else:
			# IF pause display refreshes, so just set big time.
			time.sleep(18000)



