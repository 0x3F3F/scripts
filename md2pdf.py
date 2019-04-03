#!/usr/bin/python3

######################################################################################
# Name:			md2pdf.py
# Author:		Iain Benson
# Description:	Converts markdown to pdf
#				Uses Github CSS which looks nicer than pandoc (default anyway)
# 
# Dependancies:	grip, wkhtmltopdf
#
#####################################################################################

import os, sys
import re
import platform

noParams = len(sys.argv)-1

if noParams !=1 :
	print("One file ony needs to be specified")
else:
	theFile=sys.argv[1]

	if theFile.endswith('md'):
		filenameBase = os.path.splitext(os.path.basename(theFile))[0]
	
		htmlFilename = filenameBase+".html"
		pdfFilename = filenameBase+".pdf"

		#Convert it to html using grip
		print("Running Grip...")
		command = "grip "+theFile+" --export "+htmlFilename
		os.system(command)
		
		# PageBreak: replace two linebeaks with pagebreak
		# Read into array
		print("Adding Page Breaks...")
		with open(htmlFilename, "r") as tempFile:
			fileContents = tempFile.read()
		# do replacement
		pattern = re.compile(r"<hr>\n<hr>", re.MULTILINE)
		updatedContents = pattern.sub("<hr style=\"page-break-after: always\">", fileContents)
		# Write back to file
		with open(htmlFilename, "w") as tempFile:
			tempFile.write(updatedContents)

		# Convert to pdf using wkhtmltopdf
		# Cos windows is crap, I had to use full path - which meants this:
		print("Running wkhtmltopdf ", end="")
		if platform.system() == "Linux":
			print("(Linux)")
			command = r'"wkhtmltopdf" '+htmlFilename + r' ' + pdfFilename
		else:
			print("(Windows)")
			command = r'"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe" '+htmlFilename + r' ' + pdfFilename
		os.system(command)

		# Removing intermediate html file
		os.remove(htmlFilename)
	else:
		print("Need to specify a md file")
	



