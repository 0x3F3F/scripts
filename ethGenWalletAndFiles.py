#!/usr/bin/python3

import time
import functools

# For Initial wallet generation
from ecdsa import SigningKey, SECP256k1
import sha3

# For validation
import sys
from web3 import Web3
from eth_keys import keys
import codecs
import qrcode
from PIL import Image, ImageDraw, ImageFont

def checksum_encode(addr_str): # Takes a hex (string) address as input
    keccak = sha3.keccak_256()
    out = ''
    addr = addr_str.lower().replace('0x', '')
    keccak.update(addr.encode('ascii'))
    hash_addr = keccak.hexdigest()
    for i, c in enumerate(addr):
        if int(hash_addr[i], 16) >= 8:
            out += c.upper()
        else:
            out += c
    return '0x' + out


if __name__ == "__main__":

	# sleep not workingas should due to output buffering
	print = functools.partial(print, flush=True)

	##############################################################################################
	# Phase 1 : Generate Wallet. Essentially copy from ethereum-wallet-generator
	###############################################################################################
	keccak = sha3.keccak_256()

	priv = SigningKey.generate(curve=SECP256k1)
	pub = priv.get_verifying_key().to_string()

	keccak.update(pub)
	address = keccak.hexdigest()[24:]

	phase1PrivKeyStr = priv.to_string().hex()
	phase1PubKeyStr = "0x"+pub.hex()
	phase1AddressStr = checksum_encode(address)

	print("\033[1mPhase 1: Generating Ethereum Wallet\033[0m")
	time.sleep(2)
	print("Private key : \033[0;92m" , phase1PrivKeyStr + "\033[00m")
	print("Public key  : ", phase1PubKeyStr)
	print("Address     : \033[0;92m" , phase1AddressStr + "\033[00m")

	##############################################################################################
	# Phase 2 : Validate generated address using a differnet library
	###############################################################################################

	print("\n\033[1mPhase 2: Verifying Generated Address\033[0m")
	time.sleep(3)
	isValidAddress = Web3.isAddress(phase1AddressStr)
	if isValidAddress:
		print("The generated address looks valid")
		print("Note that the mixed case in the hex address implied it has a checksum")
	else:
		print("ADDRESS IS NOT VALID")
		exit()
	
	##############################################################################################
	# Phase 3 : Validate can get back to pulic address from the private key above using alt method
	#          https://ethereum.stackexchange.com/questions/29476/generating-an-address-from-a-public-key
	###############################################################################################

	print("\n\033[1mPhase 3: Verifying Private key matches phase 1 Address / Pub Key using alternate derivation method \033[0m")
	time.sleep(3)

	# Convert suplied private key string into bytes object
	privKey_bytes = Web3.toBytes(hexstr=phase1PrivKeyStr)
	
	# Determine the corresponding Public key
	pk = keys.PrivateKey(privKey_bytes)
	phase3PubKeyStr = str(pk.public_key)

	# Determine the corresponding address from Public key
	pubKey_bytes = Web3.toBytes(hexstr=phase3PubKeyStr)	
	phase3AddressStr = keys.PublicKey(pubKey_bytes).to_address()

	if phase1PubKeyStr == phase3PubKeyStr:
		print("\033[0;92mGenerated Public Key matches\033[00m")
	else:
		print("\033[0;91mGenerated Public Key is NOT VALID\033[00m")
		exit()


	# Generated phase 1 address has mixed case, this is a checksum and we should use that one
	# The phase3 address is lower case, so we need to do a case insensitive comparison
	if phase1AddressStr.lower() == phase3AddressStr.lower():
		print("\033[0;92mGenerated Address matches\033[00m")
	else:
		print("\033[0;91mGenerated Address is NOT VALID\033[00m")
		exit()


	##############################################################################################
	# Phase 4 : Generate txt file and QR Codes of info 
	###############################################################################################
	print("\n\033[1mPhase 4: Generating QR Codes and Txt file\033[0m")
	time.sleep(3)

	# Now, faf about making a QR code you won't use
	addressQRimg = qrcode.make(phase1AddressStr)
	privQRimg = qrcode.make(phase1PrivKeyStr)

	#  Create background canvas 
	background = Image.new('RGBA', (1200,540), (220,220,220,255))
	draw = ImageDraw.Draw(background)

	# Now, the text we're gonna use
	fontKeys = ImageFont.truetype( "/usr/share/fonts/truetype/tlwg/TlwgMono.ttf",18, encoding="unic")
	fontTitle = ImageFont.truetype( "/usr/share/fonts/truetype/tlwg/TlwgMono-Bold.ttf",28)
	draw.text((115,2), "Ethereum Address", (0,0,0), font=fontTitle)
	draw.text((10,404), phase1AddressStr, (0,0,0), font=fontKeys) 
	draw.text((840,2), "Private Key", (0,0,0), font=fontTitle)
	draw.text((745,485), phase1PrivKeyStr[:32], (0,0,0), font=fontKeys)
	draw.text((745,505), phase1PrivKeyStr[32:], (0,0,0), font=fontKeys)

	# Paste in QR Code
	#qr = Image.open(myAddress+".png")
	background.paste(addressQRimg, (60, 35)) 
	background.paste(privQRimg, (700, 35)) 
	background.save(phase1AddressStr + ".png")

	# Going to also write into into text files
	fp = open(phase1AddressStr + ".txt", "w")
	fp.write("GENERATED ETHEREUM WALLET\n\n")
	fp.write("Address     : " + phase1AddressStr + "\n")
	fp.write("Public Key  : " + phase1PubKeyStr + "\n")
	fp.write("Private Key : " + phase1PrivKeyStr + "\n")
	fp.close()

	print("File generation complete.")
	print("These \033[4mfiles should be encrypted\033[0m and original ones \033[4mdeleted using shred\033[0m")


