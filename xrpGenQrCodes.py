#!/usr/bin/python3

import time
import functools
import argparse

# For validation
import sys
import qrcode
from PIL import Image, ImageDraw, ImageFont

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-a', type=str, help='Ripple Address (Public Key)')
	parser.add_argument('-s', type=str, help='Ripple Secret (Private Key)')
	args = parser.parse_args()

	public = args.a
	private = args.s

	if public == None or private == None :
		print("Please supply the address/public key using -a and secret/private key using -s")
		print ("QR Codes NOT GENERATED")
		exit()

	# Now, faf about making a QR code you won't use
	addressQRimg = qrcode.make(public)
	privQRimg = qrcode.make(private)

	#  Create background canvas 
	background = Image.new('RGBA', (1200,480), (220,220,220,255))
	draw = ImageDraw.Draw(background)

	# Now, the text we're gonna use
	fontKeys = ImageFont.truetype( "/usr/share/fonts/truetype/tlwg/TlwgMono.ttf",18, encoding="unic")
	fontTitle = ImageFont.truetype( "/usr/share/fonts/truetype/tlwg/TlwgMono-Bold.ttf",28)
	draw.text((115,2), "Ripple Address", (0,0,0), font=fontTitle)
	draw.text((60,410), public, (0,0,0), font=fontKeys) 
	draw.text((775,2), "Private Key", (0,0,0), font=fontTitle)
	draw.text((732,410), private, (0,0,0), font=fontKeys)

	# Paste in QR Code
	#qr = Image.open(myAddress+".png")
	background.paste(addressQRimg, (60, 35)) 
	background.paste(privQRimg, (700, 35)) 
	background.save(public + ".png")

	# Going to also write into into text files
	fp = open(public + ".txt", "w")
	fp.write("GENERATED RIPPLE WALLET\n\n")
	fp.write("Address     : " + public + "\n")
	fp.write("Private Key : " + private + "\n")
	fp.close()

	print("File generation complete.")
	print("These \033[4mfiles should be encrypted\033[0m and original ones \033[4mdeleted using shred\033[0m")


