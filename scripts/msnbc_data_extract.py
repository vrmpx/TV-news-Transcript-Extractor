#!/bin/bash

import sys,re
from subprocess import call
import requests
from bs4 import BeautifulSoup

def get_clean_transcript(inhtml):

	parsed_html = BeautifulSoup(inhtml)
	clean_text = []
	for tag in parsed_html.findAll('p'):
		clean_text.append(tag.text)
	return clean_text


MSNBC_transcripts="http://www.msnbc.com/transcripts/"


# Help screen
if sys.argv[1] == "-h" or sys.argv[1] == "--help":
	print("tcc-download-MSNBC <show name> [<daysago>] [v]")
	print("\n\tDownload transcripts from MSNBC.")
	print("\n\tExamples:")
	print("\n\t\tts-download-MSNBC Hardball_with_Chris_Matthews")
	print("tcc-download-MSNBC Hardball_with_Chris_Matthews 01-23-2018 01-28-2018")
	print("\n\t\tcc-download-MSNBC Hardball_with_Chris_Matthews 2012-10-30 v")
	print("\n\tVerbose output: cc-download-MSNBC Hardball_with_Chris_Matthews v")
	print("\n\tFor the moment, the web pages are simply downloaded.")
	print("\tThe completed files are in /tvspare/transcripts/MSNBC-automated/")
	print("\t/tvspare/transcripts/CNN-automated/Failed-downloads.\n")

showname=sys.argv[1]
showurl=MSNBC_transcripts+showname+"/"

start_date=sys.argv[2]
end_date=sys.argv[3]

available_shows = ["Hardball_with_Chris_Matthew", "Mtp_Daily", "The_Beat_with_Ari_Melber", "The_Rachel_Maddow_Show",
				   "All_In_with_Chris_Hayes", "The_Last_Word_with_Lawrence_ODonnell", "For_the_Record_with_Greta"]

if showname in available_shows: 
	if showname == "Hardball_with_Chris_Matthew":
		URL="http://www.msnbc.com/transcripts/hardball/"
	elif showname == "Mtp_Daily":
		URL="http://www.msnbc.com/transcripts/mtp-daily//"
	elif showname == "The_Beat_with_Ari_Melber":
		URL="http://www.msnbc.com/transcripts/msnbc-live-with-ari-melber/"
	elif showname == "The_Rachel_Maddow_Show":
		URL="http://www.msnbc.com/transcripts/rachel-maddow-show/"
	elif showname == "All_In_with_Chris_Hayes":
		URL="http://www.msnbc.com/transcripts/all-in"
	elif showname == "The_Last_Word_with_Lawrence_ODonnell":
		URL="http://www.msnbc.com/transcripts/the-last-word/"
	elif showname == "For_the_Record_with_Greta":
		URL="http://www.msnbc.com/transcripts/for-the-record-with-greta"
else:
	print("showname should be in :\n")
	print(available_shows)
	exit

# Set temporary working directory
TEMP= "./tmp/MSNBC"

# Create a fresh instance
#rm -rf $TEMP
call("mkdir -p "+TEMP, shell=True)

SHOW_FOLDER="./tmp/MSNBC/"+showname
call("mkdir -p "+SHOW_FOLDER, shell=True)

TRANSCRIPTS=SHOW_FOLDER+"/transcripts/"
call("mkdir -p "+TRANSCRIPTS, shell=True)

# Set log directory
STOR= "./tmp/LOGS"

#create a instance
call("mkdir -p "+STOR, shell=True)
# Define log of failed downlaods
#FAILLOG=$STOR/Failed-downloads

#url="http://www.msnbc.com/transcripts/mtp-daily/2017-06-20"

#get year, month, day
start_year, start_mon, start_day= start_date.split("-")
end_year, end_mon, end_day= end_date.split("-")

end_year = str(int(end_year)+1)
end_mon = str(int(end_mon)+1)
end_day = str(int(end_day)+1)

print("sd",start_day)
print("ed",end_day)
print("sy",start_year)
print("ey",end_year)

for year in range(int(start_year),int(end_year)):
	print("year",year)
	for month in range(int(start_mon), int(end_mon)):
		print(month)
		if month == int(start_mon):
			month_start = start_day
		else:
			month_start = '01'

		if month == int(end_mon)-1:
			month_end = end_day
		else:
			month_end = '30'

		print("month_end ",month_end)
		for day in range(int(month_start), int(month_end)):
			print(day)
			if month < 10:
				month_cl ="0" + str(month)
			else:
				month_cl = str(month)

			if day < 10:
				print(URL+str(year)+"-"+month_cl+"-0"+str(day))
				html_text = requests.get(URL+str(year)+"-"+month_cl+"-0"+str(day)).text
#				print(html_text)
				clean_text = get_clean_transcript(inhtml=html_text)
				file = open(TRANSCRIPTS+str(year)+"-"+month_cl+"-0"+str(day)+".html",'w')
				for line in clean_text:
					file.write(line+"\n")
				file.close()

				
#				curl $URL$year"-"$month_cl"-0"$day > $HTML$year$"-"$month_cl"-0"$day".html"
			else:
				print(URL+str(year)+"-"+month_cl+"-"+str(day))
				html_text = requests.get(URL+str(year)+"-"+month_cl+"-"+str(day)).text
#				print(html_text)
				clean_text = get_clean_transcript(inhtml=html_text)
				file = open(TRANSCRIPTS+str(year)+"-"+month_cl+"-"+str(day)+".html",'w')
				for line in clean_text:
					file.write(line+"\n")
				file.close()
#				print(clean_text.findAll('p'))
#				curl $URL$year"-"$month_cl"-"$day > $HTML$year$"-"$month_cl"-"$day".html"

