#!/usr/bin/env python3

################################################################################
#
#	Script: 		tagmp3
#	Version:		1.1
#	Description:	tag mp3s
################################################################################

# Reference specific libraries required
import argparse
import eyed3
import os, sys, glob, re
import os.path, time
import csv
import collections
import urllib.request
from datetime import datetime, timedelta
from argparse import RawTextHelpFormatter




#####################################################
#Add functions here, can call them from the main code
######################################################
	
	
	
# Process parameters supplied by the user
def GetUserOptions():
	"""
	Process the command line arguments / set program help
	"""

	DescText = "Tags MP3s using eyeD3"

	parser = argparse.ArgumentParser(description=DescText, formatter_class=RawTextHelpFormatter )

	requiredNamed = parser.add_argument_group('required arguments')
	requiredNamed.add_argument('-a','--artist', help='Mandatory. artist', required=True)
	requiredNamed.add_argument('-A','--album', help='Mandatory. album', required=True)
     
	args = parser.parse_args()
	
	#if no value specified then stop
	if args.artist == None:
		print("Please specify artist using -a flag.")
		sys.exit()

	#if no value specified then stop
	if args.album == None:
		print("Please specify album file using -A flag.")
		sys.exit()

	return args.album,args.artist




##############################################################################
# This is the main entry point to the script 
##############################################################################
if __name__ == "__main__":

	# Process user supplied arguments
	album, artist = GetUserOptions()

	files = glob.glob("*.mp3")
	files.sort()

	trackCount = 1

	for currFile in files:

		# Trim first 4 characters "01. " and last 3 ".mp3"
		trimmedName = currFile[:-4] 
		#command = r'/usr/bin/eyeD3 -a ' + r'"' + artist + '"' + r' -A ' + r'"' + album + '"' + r' -t ' + r'"' + trimmedName + r'"'  
		#print(command)
		#os.system(command)
		

		audiofile = eyed3.load(currFile)
		audiofile.tag.artist = artist
		audiofile.tag.album = album
		#audiofile.tag.album_artist = "Various Artists"
		audiofile.tag.title = trimmedName
		audiofile.tag.track_num = trackCount
		audiofile.tag.save()
		trackCount+=1


