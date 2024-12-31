import os
import time
import datetime
import shutil
import requests
from functions.functions import *
from bs4 import BeautifulSoup as bs

# constants
timeFormat = "%H.%M.%S"

# main code
def mainloop():
    while True:
        print("""------------------------------------------------------
T: TotalRaceTiming Link
P: Parkrun Website
              
R: Manual race results
M: Add parkruns manually
              
S: Produce Summary Sheet
E: Make a Backup & Exit
------------------------------------------------------""")
        action = input().upper()
        if action == "R":
            manualRaceEntry()
        elif action == "T":
            urlRaceEntry()
        elif action == "M":
            addParkruns()
        elif action == "P":
            addParkrunsAuto()
        elif action == "S":
            summarySheet()
        elif action == "E":
            backup()
            break
        else: print("Not a valid option. Please try again.")

# MENU OPTION R (Manual Race Results)
def manualRaceEntry():
    raceName = input("Race Name: ")
    if raceName == "": return None

    raceDist = getDistFromUser()
    if raceDist == "": return None

    raceDate = input("Date: ")
    if raceDate == "": return None

    while True:
        print("------------------------------------------------------")
        print(f"{raceName.upper()} {raceDist.upper()} - {raceDate}")

        name = getNameFromUser()
        if name == "": return None

        ageCat = getAgeCat(name)
        print(ageCat)

        valid = False
        if raceDist.isnumeric():
            points = int(raceDist)
            addRaceToFile(name, raceName, raceDist, raceDate, "", points)
        
        else:
            raceTime = getTimeFromUser()
            if raceTime == "": return None
                
            points = calcPoints(raceTime, raceDist, ageCat)
            addRaceToFile(name, raceName, raceDist, raceDate, time.strftime(timeFormat, raceTime), points)

# MENU OPTION T (Automatic TotalRaceTiming Results)
def urlRaceEntry():
    raceName, raceDist, raceDate = getRaceDetailsFromUser()

    if raceName == "" or raceDist == "" or raceDate == "": return None

    url = input("Copy and paste the totalRaceTiming URL: ")
    if url == "": return None

    page = requests.get(url)
    soup = bs(page.content, "html.parser")
    runners = soup.find("tbody") # gets all 

    notAdded = []
    runnersAdded = 0
    for runner in runners:
        runnerstring : str = runner.decode_contents()
        if "<td>Dereham Runners AC</td>" in runnerstring:
            runnerstring = runnerstring.split("<td")
            name = runnerstring[2][1:-5] + " " + runnerstring[3][1:-5]
            raceTime = runnerstring[-2][2:-8]
            try:
                ageCat = getAgeCat(name)
            except FileNotFoundError:
                notAdded.append((name, raceTime))
                continue
            print(name.upper() + "," + ageCat + "," + raceTime)
            raceTime = time.strptime(raceTime, "%H:%M:%S")
            points = calcPoints(raceTime, raceDist, ageCat)

            addRaceToFile(name, raceName, raceDist, raceDate, time.strftime(timeFormat, raceTime), points)

            runnersAdded += 1
            print("")
    print("NOT ADDED: ")
    for name, raceTime in notAdded:
        print("")
        print(f"{name.upper()} ({raceTime}) not found. Enter their file name below.")
        name = getNameFromUser()
        if name == "":
            print("No new race added.")
        else:
            ageCat = getAgeCat(name)
            print(name.upper() + "," + ageCat + "," + raceTime)
            raceTime = time.strptime(raceTime, "%H:%M:%S")
            points = calcPoints(raceTime, raceDist, ageCat)
            addRaceToFile(name, raceName, raceDist, raceDate, time.strftime(timeFormat, raceTime), points)
            runnersAdded += 1
    print("")
    print(f"{runnersAdded} runners have been added.")
        
# MENU OPTION M (Parkruns)
def addParkruns():
    raceDate = input("Date: ")
    if raceDate == "": return None

    newlines = get_parkrun_dict()

    while True:
        print("------------------------------------------------------")
        print(f"PARKRUN - {raceDate}")
        valid = False
        while not valid:
            name = getNameFromUser()
            if name == "": break
            valid = True
        if not valid: break
        add_parkrun_to_file(name, raceDate)
        if name in newlines.keys():
            newlines[name] += 1
        else:
            newlines[name] = 1

    open("parkruns.txt", "w").close()
    parkrun_file = open("parkruns.txt", "a")
    for key, value in newlines.items():
        parkrun_file.write(f"{key} - {value}\n")
    parkrun_file.close()

        

# MENU OPTION P (Parkruns - auto)
def addParkrunsAuto():
    raceDate = input("Date: ")
    if raceDate == "": return None

    notAdded = []
    web_text = input("CTRL+A then CTRL+C on the consolodated report website and CTRL+V here: ")
    endindex = web_text.find("Dereham Runners AC")

    newlines = get_parkrun_dict()

    runnersAdded = 0
    while endindex != -1:
        index = endindex
        spacesfound = 0
        while spacesfound != 2:
            index -= 1
            if web_text[index] == "	":
                spacesfound += 1
        name = web_text[index:endindex].strip()
        name = name.split(" ")
        if len(name) >= 2:
            newname = name[0]
            for i in range(1, len(name)):
                name[i] = name[i].lower().capitalize()
                newname += " " + name[i]
            name = newname
            if name in newlines.keys():
                newlines[name] += 1
            else:
                newlines[name] = 1
            try:
                add_parkrun_to_file(name, raceDate)
                runnersAdded += 1
            except FileNotFoundError:
                if name not in [""]:
                    notAdded.append(name)

        web_text = web_text[endindex + 1 :]
        endindex = web_text.find("Dereham Runners AC")
        print("")

    open("parkruns.txt", "w").close()
    parkrun_file = open("parkruns.txt", "a")
    for key, value in newlines.items():
        parkrun_file.write(f"{key} - {value}\n")
    parkrun_file.close()
    
    print("NOT ADDED: ")
    for name in notAdded:
        print("")
        print(f"{name.upper()} not found. Enter their file name below.")
        name = getNameFromUser()
        if name == "":
            print("No new parkrun added.")
        else:
            ageCat = getAgeCat(name)
            print(name.upper() + ", " + ageCat)
            add_parkrun_to_file(name, raceDate)
            runnersAdded += 1
    
    print("")
    print(f"{runnersAdded} runners have been added.")

# MENU OPTION S (Summary Sheet)
def summarySheet():
    club50List = []
    club100List = []
    
    for name in os.listdir("People Files"):
        print(name)
        f = open(os.path.join("People Files", name), "r")
        fileLines = f.readlines()
        points = int(fileLines[2].strip()[6:])
        club = fileLines[2].strip()
        f.close()

        if club == "CLUB 50":
            for i in range(len(club50List)):
                item = club50List[i]
                if points > int(item[item.strip().find(" - ") + 3:]):
                    club50List.insert(i, f"{name[:-4]} - {points}\n")
                    break
                elif i == len(club50List) - 1:
                    club50List.append(f"{name[:-4]} - {points}\n")
            if len(club50List) == 0:
                club50List.append(f"{name[:-4]} - {points}\n")

        elif club == "CLUB 100":
            for i in range(len(club100List)):
                item = club100List[i]
                if points > int(item[item.strip().find(" - ") + 3:]):
                    club100List.insert(i, f"{name[:-4]} - {points}\n")
                    break
                elif i == len(club100List) - 1:
                    club100List.append(f"{name[:-4]} - {points}\n")
            if len(club100List) == 0:
                club100List.append(f"{name[:-4]} - {points}\n")

    dateForFile = str(datetime.date.strftime(datetime.date.today(), "%d-%m-%Y"))
    if not os.path.exists(os.path.join("Summary Sheets", dateForFile)):
        os.makedirs(os.path.join("Summary Sheets", dateForFile))
        
    summary50 = open(os.path.join("Summary Sheets", dateForFile, "CLUB 50" + ".txt"), "w")
    summary100 = open(os.path.join("Summary Sheets", dateForFile, "CLUB 100" + ".txt"), "w")
    summary50.writelines(club50List)
    summary100.writelines(club100List)
    summary50.close()
    summary100.close()
    print(f"Summary sheets for {dateForFile} made.")

# MENU OPTION E (Backup & Exit)
def backup():
    dateForFile = str(datetime.date.strftime(datetime.date.today(), "%d-%m-%Y"))

    if not os.path.exists(os.path.join("Backups", dateForFile)):
        os.makedirs(os.path.join("Backups", dateForFile))

    for file in os.listdir("People Files"):
        open(os.path.join("Backups", dateForFile, file), "w").close()
        shutil.copy(os.path.join("People Files", file), 
                    os.path.join("Backups", dateForFile, file))
        
    print(f"Backup made for {dateForFile}")

mainloop()

