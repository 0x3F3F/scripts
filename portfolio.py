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


def	SetupShareDictionaries(currDict, shareDictMultiAss, shareDictGrowth, shareDictIndexes, pmDict):
	"""Setup Ordered Dictionaries of shares / rates"""


	#				Yahoo Tkr	Ticker		FullName							Currency	Dps		AllTimeHigh		TargetPrice
	shareDictIndexes['^FTSE']	= ['FTSE 100',	'FTSE 100',							'GBX',		0,		7792,			NO_TARGET_PRICE]
	shareDictIndexes['^GSPC']	= ['S&P 500',	'S&P 500',							'USD',		0,		2900,			NO_TARGET_PRICE]
	shareDictIndexes['EEM']		= ['EM USD',	'iShares Emerging ETF USD',			'USD',		1,		52.08,			NO_TARGET_PRICE] 
	shareDictIndexes['VFEM.L']	= ['EM GBP',	'Vanguard Emergin ETF GBP',			'GBX',		1,		48.57,			NO_TARGET_PRICE] 

	pmDict['GC=F'] =			['Gold',	'Gold',								'USD',		0,		1838,			NO_TARGET_PRICE] 
	pmDict['SI=F'] =			['Silvr',	'Silver',							'USD',		2,		46.4,			NO_TARGET_PRICE]

	shareDictMultiAss['PNL.L'] = ['PNL',	'Personal Assets',					'GBX',		0,		41508,			NO_TARGET_PRICE]
	shareDictMultiAss['RCP.L'] = ['RCP',	'RIT Capital Partners',				'GBX',		0,		2135,			1800]
	shareDictMultiAss['CGT.L'] = ['CGT',	'Capital Gearing',					'GBX',		0,		4190,			3800]
	shareDictMultiAss['RICA.L'] = ['RICA',	'Ruffer',							'GBX',		1,		242,			NO_TARGET_PRICE]
	shareDictMultiAss['BTEM.L'] = ['BTEM',	'British Empire',					'GBX',		0,		768,			600]
	shareDictMultiAss['CLDN.L'] = ['CLDN',	'Caledonia',						'GBX',		0,		2907,			2500]
	shareDictMultiAss['HAST.L'] = ['HAST',	'Henderson Alternative',			'GBX',		0,		305,			250]

	shareDictGrowth['SST.L'] =  ['SST',		'Scottish Oriental Smaller Cos',	'GBX',		0,		1098,			800] 
	shareDictGrowth['AAS.L'] =  ['AAS',		'Aberdeen Asian Smaller Cos',		'GBX',		0,		1143,			800] 
	shareDictGrowth['BRFI.L'] = ['BRFI',	'Blackrock Frontiers',				'GBX',		0,		169,			130] 
	shareDictGrowth['JII.L'] =  ['JII',		'JP Morgan Indian',					'GBX',		0,		786,			600]
	shareDictGrowth['HRI.L'] =  ['HRI',		'Herald',							'GBX',		0,		1380,			800] 
	shareDictGrowth['BIOG.L'] = ['BIOG',	'Biotech Growth Trust',				'GBX',		0,		836,			500]
	shareDictGrowth['PIN.L'] =  ['PIN',		'Pantheon',							'GBX',		0,		2179,			1200] 
	shareDictGrowth['HGT.L'] =  ['HGT',		'HG Capital',						'GBX',		0,		2030,			1200] 
	shareDictGrowth['IBTS.L'] = ['IBTS',	'iShares US Treas 1-3',				'GBX',		2,		109,			85]
	shareDictGrowth['IBTM.L'] = ['IBTM',	'iShares US Treas 7-10',			'GBX',		2,		169,			140]
	shareDictGrowth['IBTL.L'] = ['IBTL',	'iShares US Treas 20+',				'GBX',		2,		412,			330]
	shareDictGrowth['TP05.L'] = ['TP05',	'iShares US TIPs 0-5',				'GBX',		2,		389,			350]
	shareDictGrowth['YCA.L'] =  ['YCA',		'Yellowcake',						'GBX',		0,		250,			210] 
	shareDictGrowth['GCL.L'] =  ['GCL',		'Geiger Counter',					'GBX',		1,		130,			18] 
	shareDictGrowth['NXE.TO'] =  ['NXE',	'Nexgen Energy',					'CAD',		2,		3.8,			2.39] 
	shareDictGrowth['CCO.TO'] =  ['CCO',	'Cameco',							'CAD',		2,		55,				12.00] 
	shareDictGrowth['URE.TO'] =  ['URE',	'UR-Energy',						'CAD',		2,		2.00,			1.10] 
	shareDictGrowth['EFR.TO'] =  ['EFR',	'Energy Fuels',						'CAD',		2,		8.65,			4.50] 
	shareDictGrowth['DML.TO'] =  ['DML',	'Denison Mines',					'CAD',		2,		3.75,			0.6] 
	shareDictGrowth['FCU.TO'] =  ['FCU',	'Fission Uranium Corp',				'CAD',		2,		1.6,			0.54] 
	shareDictGrowth['LAM.TO'] =  ['LAM',	'Laramide Resources',				'CAD',		3,		2.6,			0.34] 
	shareDictGrowth['GXU.V'] =  ['GXU',		'Goviex',							'CAD',		3,		0.38,			0.10] 
	shareDictGrowth['FSY.TO'] =  ['FSY',	'Forsys Metals',					'CAD',		3,		2.2,			0.17] 
	shareDictGrowth['UEX.TO'] =  ['UEX',	'UEX Corporation',					'CAD',		3,		2.2,			0.12] 
	shareDictGrowth['GJGB.L'] =  ['GJGB',	'VanEc Juniot Gold Miners',			'GBX',		1,		24,				18] 

	currDict['GBPEUR=X']	 =	['GBPEUR',	'GBP to EUR XRate',					'',			4,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	currDict['GBPUSD=X']	=	['GBPUSD',	'GBP to USD XRate',					'',			4,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]
	currDict['GBPCAD=X']	=	['GBPCAD',	'GBP to CAD XRate',					'',			4,		NO_ALL_TIME_HIGH, NO_TARGET_PRICE]

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

	try:
		yahooJSON = requests.get(yahooQuery)
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
		os.system('clear')

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


