import random
import sys
import os
import glob
import base64
import requests
from difflib import SequenceMatcher
from hammock import Hammock as GendreAPI

gendre = GendreAPI("http://api.namsor.com/onomastics/api/json/gendre")

# Created by Tushar Singhal

race_dict = {}                      #stores all the names of celebs as keys and their race as values
celeb_names_dict = {}               #stores unique celeb names as keys and race as value
gender_dict = {}                    #stores unique celeb names as keys and gender as value

def readgit():

    url = 'https://api.github.com/repos/usc-sail/mica-race-from-face/contents/actor_race.txt'
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        req = req.json()  # the response is a JSON
        # req is now a dict with keys: name, encoding, url, size ...
        # and content. But it is encoded with base64.
        content = base64.b64decode(req['content']).decode('utf-8')
        info = content.split("\n")
        global race_dict                        #declared global for later use

        for i in range(len(info)-1):
            namesplit = info[i].split(":")
            race_dict[namesplit[0]] = namesplit[1]

    else:
        print('Content was not found.')


directories = ["transcript_data/FOX/Hannity/",
               "transcript_data/FOX/The_Five/",
               "transcript_data/FOX/The_Ingraham_Angle/",
               "transcript_data/FOX/The_Story/",
               "transcript_data/MSNBC/All_In_with_Chris_Hayes/",
               "transcript_data/MSNBC/The_Beat_with_Ari_Melber/",
               "transcript_data/MSNBC/The_Last_Word_with_Lawrence_ODonnell/",
               "transcript_data/MSNBC/The_Rachel_Maddow_Show/",
               "transcript_data/CNN/Anderson_Cooper_360/",
               "transcript_data/CNN/CNN_Tonight/",
               "transcript_data/CNN/Erin_Burnett_OutFront/",
               "transcript_data/CNN/The_Lead_with_Jake_Tapper/"]

outputdirec = ["output_clean/FOX/Hannity/",
               "output_clean/FOX/The_Five/",
               "output_clean/FOX/The_Ingraham_Angle/",
               "output_clean/FOX/The_Story/",
               "output_clean/MSNBC/All_In_with_Chris_Hayes/",
               "output_clean/MSNBC/The_Beat_with_Ari_Melber/",
               "output_clean/MSNBC/The_Last_Word_with_Lawrence_ODonnell/",
               "output_clean/MSNBC/The_Rachel_Maddow_Show/",
               "output_clean/CNN/Anderson_Cooper_360/",
               "output_clean/CNN/CNN_Tonight/",
               "output_clean/CNN/Erin_Burnett_OutFront/",
               "output_clean/CNN/The_Lead_with_Jake_Tapper/"]


def main():
    readgit()
    readfiles()


def readfiles():
    for i in range(len(directories)):
        for filename in glob.glob(os.path.join(directories[i] + "transcripts/", '*.txt')):
            textfilename = filename.split("/")
            output_filename = outputdirec[i] + textfilename[len(textfilename)-1]
            file_out = open(output_filename, "w")
            file_cur = open(filename, "r")
            lines_of_text = []
            for line in file_cur:
                lines_of_text.append(line)
            if i < 4:
                    lines_of_text = cleanfox(lines_of_text)
                    file_out.writelines(lines_of_text)
            elif i < 8:
                lines_of_text = cleanmsnbc(lines_of_text)
                file_out.writelines(lines_of_text)
            else:
                lines_of_text = cleancnn(lines_of_text)
                file_out.writelines(lines_of_text)


def similar(a, b):                              #returns similarity between strings
    return SequenceMatcher(None, a, b).ratio()


def getgender(name):
    namesplit = name.split(" ")
    if len(namesplit) > 2 or name == "":
        gender = "N.A"
    elif len(namesplit) == 2:
        resp = gendre(namesplit[0], namesplit[1]).GET()
        gender = resp.json().get('gender')
    elif len(namesplit) == 1:               #handles edge case of precolons beginning with brackets which give empty names
        resp = gendre(namesplit[0], 'a').GET()
        gender = resp.json().get('gender')

    return gender


def addgenderace(precolon):                            #find most similar name in the dictionary
    name = getname(precolon).lower().rstrip()

    maxsimilarity = 0.0
    race = ""
    gender = "N.A"
    global celeb_names_dict
    global gender_dict

    if name in celeb_names_dict:                # if key name exists in celeb_names_dict
        race = celeb_names_dict[name]
    else:
        for key in race_dict.keys():
            similarity = similar(key.lower(), name)
            if similarity >= 0.5 and similarity > maxsimilarity:
                maxsimilarity = similarity
                race = race_dict[key]
        if race != "":                          #if race found
            celeb_names_dict[name] = race

    if name in gender_dict:
        gender = gender_dict[name]
    else:
        gender = getgender(name)
        gender_dict[name] = gender

    if maxsimilarity != 0.0 or race != "":
        race2 = race
    else:
        race2 = "N.A"

    precolon = "Name: " + precolon + " ; Gender: " + gender + " ; Race: " + race2

    return precolon


def getname(precolon):
    index = precolon.find("(")
    if index >= 0:
        name = precolon[:index].rstrip()
    else:
        name = precolon.rstrip()
    name = name.lstrip()
    return name


def cleanprecolon(precolon):
    words = precolon.split(" ")
    precolon = ""
    if words[0].endswith("."):
        del words[0]
    for i in range(len(words)):
        if words[i].startswith("(") and words[i].endswith(","):
            words[i] = words[i][len(words[i])-1:]                   #keep comma
        elif words[i].endswith(")"):
            words[i] = ""
        if i != len(words)-1:
            precolon += words[i] + " "
        else:
            precolon += words[i]

    return precolon


def cleanspeakernames(lines_of_text, startindex, endindex):
    i = startindex + 1

    while i < endindex:
        colonindex = lines_of_text[i].find(":")
        if colonindex != -1:
            precolon = lines_of_text[i][:colonindex]
            precolon = cleanprecolon(precolon)
            postcolon = lines_of_text[i][colonindex + 1:]
            commaindex = precolon.find(",")
            checklowercase = any(c.islower() for c in precolon)
            if commaindex != -1 and checklowercase != 1:
                precolon = precolon[:commaindex] + " (" + precolon[commaindex + 1:] + ")"
                precolon = addgenderace(precolon)
                lines_of_text[i] = precolon + " ; Dialogue: " + postcolon
            elif checklowercase != 1:                               # save modified pre colon text
                precolon = addgenderace(precolon)
                lines_of_text[i] = precolon + " ; Dialogue: " + postcolon
        i += 1
    return lines_of_text


def cleanfox(lines_of_text):

    endline = "END\n"
    footer1 = "Content and Programming Copyright 2018 Fox News Network, LLC. ALL RIGHTS RESERVED"   #footer type in most files
    footer2 = "Copy: Content and Programming Copyright 2018 Fox News Network, LLC. ALL RIGHTS RESERVED"  # footer type in two ingraham & story files
    startline = "START\n"
    header = "This copy may not be in its final form and may be updated."
    startindex = 0
    endindex = 0

    for i in range(len(lines_of_text)):                             #find header end, and put start label

        exceptindex = lines_of_text[i].find(header[:len(header)-2])       #Hannity/2018-02-12 doesn't have a full stop at the end of the header, to accomodate this case

        if exceptindex != -1 and lines_of_text[i][exceptindex + len(header)-1] != ".":
            lines_of_text[i] = lines_of_text[i][:exceptindex + len(header)-1]+"."       #add period to the end of the line

        j = lines_of_text[i].find(header)
        if j != -1:
            lines_of_text[i] = lines_of_text[i].rstrip()            #remove extra space on the right
            if lines_of_text[i].endswith(header):
                lines_of_text.insert(i+1, "\n###" + startline)
                startindex = i+1
                break
            else:
                line = lines_of_text[i]
                line1 = line[0: j + len(header)] + "\n"             #content from beginning and including header
                line2 = line[j + len(header):] + "\n"               #content after header which should go after start

                lines_of_text[i] = line1
                lines_of_text.insert(i + 1, "###" + startline)
                startindex = i+1
                lines_of_text.insert(i + 2, line2)
                break

    for i in range(len(lines_of_text)):                             #if some text preceeds footer, push footer to next line
        j = lines_of_text[i].find(footer2)                          #first check for footer 2 as footer1 is subset of footer 2
        footerNum = 2                                               #keep track of which footer found
        if j == -1:
            j = lines_of_text[i].find(footer1)
            footerNum = 1
        if j != -1:
            line = lines_of_text[i].lstrip()
            if footerNum == 2:
                index = line.find(footer2)
            else:
                index = line.find(footer1)
            if index > 0:
                line1 = line[0:index-1] + "\n"
                line2 = line[index:]
                lines_of_text[i] = line1
                lines_of_text.insert(i + 1, line2)

    for line in lines_of_text:                                       #remove multiple "END"
        if line.rstrip() == "END":
            lines_of_text.remove(line)

    for i in range(len(lines_of_text)-1):
        if lines_of_text[i].find(endline) == -1 and lines_of_text[i+1].find(footer1) != -1:
            lines_of_text.insert(i+1, "###" + endline)
            endindex = i+1
            lines_of_text[i+2] = lines_of_text[i+2].lstrip()         #removing leading white space from footer

    lines_of_text = cleanspeakernames(lines_of_text, startindex, endindex)

    return lines_of_text


def cleanmsnbc(lines_of_text):

    endline = "END\n"
    footer1 = "THIS IS A RUSH TRANSCRIPT."
    footer2 = "Copy: Content and programming copyright 2018 MSNBC."
    startline = "START\n"
    header1 = "Show:"
    header2 = "Date:"
    headerexcept = "MSNBC:"                                         #exception case in The_Beat 2018-01-22
    startindex = 0
    endindex = 0

    for i in range(len(lines_of_text)):                             #find header words, and put start label

        j = lines_of_text[i].find(header1)
        k = lines_of_text[i].find(header2)
        excep = lines_of_text[i].find(headerexcept)

        if j != -1 and k != -1 and excep != -1:                       #exception case
            line = lines_of_text[i][:excep - 1] + "\n"
            line2 = lines_of_text[i][excep:]
            del lines_of_text[i]
            lines_of_text.insert(i, line)
            lines_of_text.insert(i + 1, "\n###" + startline)
            startindex = i+1
            lines_of_text.insert(i + 2, line2)
            break
        elif j != -1 and k != -1:
            lines_of_text.insert(i+1, "\n###" + startline)
            startindex = i+1
            break

    for line in lines_of_text:                                       #remove multiple "END"
        if line.rstrip() == "END":
            lines_of_text.remove(line)

    for i in range(len(lines_of_text)-1):
        check1 = lines_of_text[i].find(endline) == -1 and (lines_of_text[i+1].find(footer1) != -1 or lines_of_text[i+1].find(footer2) != -1)
        if check1 == 1:
            lines_of_text.insert(i+1,  "###" + endline)
            endindex = i+1
            lines_of_text[i+2] = lines_of_text[i+2].lstrip()         #removing leading white space from footer
            break

    lines_of_text = cleanspeakernames(lines_of_text, startindex, endindex)

    return lines_of_text


def cleancnn(lines_of_text):

    endline = "END\n"
    footer = "</p>"
    startline = "START\n"
    header = "<br/>"
    startindex = 0
    endindex = 0

    for i in range(len(lines_of_text)):
        j = lines_of_text[i].find(header)
        if j != -1:
            lines_of_text[i] = lines_of_text[i].rstrip()  # remove extra space on the right

            squarelineindex = -1                        #line index with timestamp
            if lines_of_text[i].find("[") != -1:
                squarelineindex = i
            elif lines_of_text[i+1].find("[") != -1:
                squarelineindex = i+1
            elif lines_of_text[i+2].find("[") != -1:
                squarelineindex = i+2

            if squarelineindex != -1:
                startstamp = lines_of_text[squarelineindex].find("[")
                endstamp = lines_of_text[squarelineindex].find("]")
                lines_of_text[squarelineindex] = (lines_of_text[squarelineindex][:startstamp] + lines_of_text[squarelineindex][endstamp + 1:]).lstrip()  # remove timestamp

            if lines_of_text[i].find(":") != -1:            #find colon and then remove any ( ) expressions before :
                startbracket = lines_of_text[i].find("(")
                if startbracket != -1 and startbracket < lines_of_text[i].find(":"):
                    endbracket = lines_of_text[i].find(")")
                    lines_of_text[i] = lines_of_text[i][:startbracket] + lines_of_text[i][endbracket+1:]
                    lines_of_text[i].lstrip()

                header = lines_of_text[i][:lines_of_text[i].find(header)+len(header)]       #add start line
                lines_of_text[i] = header + "\n"
                lines_of_text.insert(i + 1, "\n###" + startline)
                startindex = i + 1
                dialogue = lines_of_text[i][lines_of_text[i].find(header) + len(header):].lstrip()
                lines_of_text.insert(i+2, dialogue)

            elif lines_of_text[i + 1].find(":") != -1:
                startbracket = lines_of_text[i].find("(")
                startbracket2 = lines_of_text[i+1].find("(")

                if startbracket != -1:
                    endbracket = lines_of_text[i].find(")")
                    lines_of_text[i] = lines_of_text[i][:startbracket] + lines_of_text[i][endbracket + 1:]
                    lines_of_text[i].lstrip()

                if startbracket2 != -1 and startbracket2 < lines_of_text[i + 1].find(":") :
                    endbracket = lines_of_text[i+1].find(")")
                    lines_of_text[i+1] = lines_of_text[i+1][:startbracket] + lines_of_text[i+1][endbracket + 1:]
                    lines_of_text[i+1].lstrip()

                lines_of_text[i] = lines_of_text[i] + "\n"
                lines_of_text.insert(i + 1, "\n###" + startline)
                startindex = i + 1

            elif lines_of_text[i + 2].find(":") != -1:                  #specific case for this batch of transcripts
                lines_of_text[i+1] = lines_of_text[i+1] + "\n"
                lines_of_text.insert(i + 2, "\n###" + startline)
                startindex = i + 2
            break

    for i in range(len(lines_of_text)):                                       #check extra parantheses before footer
        if lines_of_text[i].rstrip() == footer:
            if lines_of_text[i-2].find("(") != -1 and lines_of_text[i-2].find(":") == -1 and lines_of_text[i-1].find(":") == -1:       #edge case for end line
                lines_of_text.insert(i-2, "###" + endline)
                endindex = i-2
            elif lines_of_text[i-1].find("(") != -1:
                lines_of_text.insert(i-1, "###" + endline)
                endindex = i-1
            else:
                lines_of_text.insert(i, "###" + endline)
                endindex = i

    for i in range(len(lines_of_text)):                                 #remove timestamps from the front of lines
        lines_of_text[i] = lines_of_text[i].lstrip()
        if lines_of_text[i].find("[") == 0:
            lines_of_text[i] = lines_of_text[i][lines_of_text[i].find("]")+1:].lstrip()

    lines_of_text = cleanspeakernames(lines_of_text, startindex, endindex)

    return lines_of_text


if __name__ == "__main__":
    main()
