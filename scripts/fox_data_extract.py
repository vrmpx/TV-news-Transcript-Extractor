#!/bin/bash

import sys,re
from subprocess import call
import requests
from bs4 import BeautifulSoup

'''
get scripts of last 10 or 18 days
'''
def get_tsanscript_urls(showurl):
	print(showurl)
#	print(show_html)
	show_html = requests.get(showurl).text
	parsed_show_html = BeautifulSoup(show_html)

	transcript_urls = []
	for article in parsed_show_html.find_all('article'):
		try:
			url = article.find('a').get('href')
			if "http://video.foxnews.com/v/" not in url:
				if len(url.split("/")) < 7:
					url = "http://www.foxnews.com"+url
				transcript_urls.append(url)
		except:
			continue

	return transcript_urls

def get_htmls(transcript_urls):

	transcript_htmls = {}
	for url in transcript_urls:
		date = "-".join(url.split("/")[4:7])
		if date in transcript_htmls.keys():
			date = date +"_Part2"
		transcript_htmls[date] = requests.get(url).text

	return transcript_htmls

def get_clean_transcripts(inhtmls):

	transcripts = {}
	for date in inhtmls:
		transcripts[date] = []
		parsed_html = BeautifulSoup(inhtmls[date])
#		print(parsed_html)
		for h1 in parsed_html.find_all('h1'):
			transcripts[date].append(">>heading>>"+h1.text)
			print(h1.text)
		print("hoho")
		for tag in parsed_html.findAll('p'):
			transcripts[date].append(tag.text)
#			print(tag.text)

	return transcripts


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


available_shows = ["The_Five", "The_Story", "Hannity", "The_Ingraham_Angle"]

if showname in available_shows: 
	if showname == "The_Five":
		URL="http://www.foxnews.com/on-air/the-five/transcripts"
	elif showname == "The_Story":
		URL="http://www.foxnews.com/category/shows/the-story/transcript.html/"
	elif showname == "Hannity":
		URL="http://www.foxnews.com/category/shows/hannity/transcript.html/"
	elif showname == "The_Ingraham_Angle":
		URL="http://www.foxnews.com/category/shows/ingraham-angle/transcript.html/"
else:
	print("showname should be in :\n")
	print(available_shows)
	exit

# Set temporary working directory
TEMP= "./tmp/FOX"

# Create a fresh instance
#rm -rf $TEMP
call("mkdir -p "+TEMP, shell=True)

SHOW_FOLDER="./tmp/FOX/"+showname
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

transcript_urls = get_tsanscript_urls(showurl=URL)
print(transcript_urls)
htmls = get_htmls(transcript_urls)
clean_transcripts = get_clean_transcripts(htmls)

for key in clean_transcripts.keys():
	file = open(TRANSCRIPTS+key+".txt",'w')
	for line in clean_transcripts[key]:
		file.write(line+"\n")
	file.close()
'''
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
				
#				curl $URL$year"-"$month_cl"-0"$day > $HTML$year$"-"$month_cl"-0"$day".html"
			else:
				print(URL+str(year)+"-"+month_cl+"-"+str(day))
				html_text = requests.get(URL+str(year)+"-"+month_cl+"-"+str(day)).text
#				print(html_text)
				clean_text = get_clean_transcript(inhtml=html_text)
#				print(clean_text.findAll('p'))
#				curl $URL$year"-"$month_cl"-"$day > $HTML$year$"-"$month_cl"-"$day".html"
'''
