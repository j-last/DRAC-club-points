import time
import datetime
from functions.functions import *
import shutil
from bs4 import BeautifulSoup as bs
import requests
# constants
timeFormat = "%H.%M.%S"

# main code
def mainloop():
    while True:
        print("""------------------------------------------------------
A: Enter race results
L: Enter link of TotalRaceTiming Results
P: Add Parkruns
S: Produce Summary Sheet
E: Make a Backup & Exit
------------------------------------------------------""")
        action = input().upper()
        if action == "A":
            manualRaceEntry()
        elif action == "L":
            urlRaceEntry()
        elif action == "P":
            addParkruns()
        elif action == "S":
            summarySheet()
        elif action == "E":
            backup()
            break
        else: print("Not a valid option. Please try again.")

# MENU OPTION A (Manual Race Results)
def manualRaceEntry():
    raceName = input("Race Name: ")
    if raceName == "": return None

    validDistances = ["5k", "5mi", "10k", "10mi", "half", "mara"]
    valid = False
    while not valid:
        raceDist = input("Distance: ")
        if raceDist == "": return None
        elif raceDist in validDistances: valid = True
        elif raceDist.isnumeric(): valid = True
        else: print("This is not a valid distance or points value.")

    raceDate = input("Date: ")
    if raceDate == "": return None

    while True:
        print("------------------------------------------------------")
        print(f"{raceName.upper()} {raceDist.upper()} - {raceDate}")
        valid = False
        while not valid:
            name = input("Name: ")
            if name == "": return None
            try:
                ageCat = getAgeCat(name)
                valid = True
            except FileNotFoundError:
                newPerson = input("This person doesn't exist yet. Create a file for them? (y/n) ")
                if newPerson.lower() == "y": 
                    createNewPerson(name)
                    ageCat = getAgeCat(name)
                    valid = True

        print(ageCat)

        valid = False
        if not raceDist.isnumeric():
            while not valid:
                raceTime = input("Time: ")
                if raceTime.count(".") == 1:
                    raceTime = "0." + raceTime
                try:
                    raceTime = time.strptime(raceTime, timeFormat)
                    valid = True
                except ValueError:
                    print(f"Invalid time format '{raceTime}'. Please try again.")

            points = calcPoints(raceTime, raceDist, ageCat)
            addRaceToFile(name, raceName, raceDist, raceDate, time.strftime(timeFormat, raceTime), points)
        else:
            points = int(raceDist)
            addRaceToFile(name, raceName, raceDist, raceDate, "", points)

# MENU OPTION L (Automatic TotalRaceTiming Results)
def urlRaceEntry():
    raceName = input("Race Name: ")
    if raceName == "": return None

    validDistances = ["5k", "5mi", "10k", "10mi", "half", "mara"]
    valid = False
    while not valid:
        raceDist = input("Distance: ")
        if raceDist == "": return None
        elif raceDist in validDistances: valid = True
        else: print("This is not a valid distance.")

    raceDate = input("Date: ")
    if raceDate == "": return None

    url = input("Copy and paste the totalRaceTiming URL: ")
    if url == "": return None

    page = requests.get(url)
    soup = bs(page.content, "html.parser")
    runners = soup.find("tbody") # gets all runners

    notAdded = []
    for runner in runners:
        runnerstring : str = runner.decode_contents()
        if "<td>Dereham Runners AC</td>" in runnerstring:
            runnerstring = runnerstring.split("<td")
            name = runnerstring[2][1:-5] + " " + runnerstring[3][1:-5]
            raceTime = runnerstring[-2][2:-8]
            try:
                ageCat = getAgeCat(name)
                valid = True
            except FileNotFoundError:
                notAdded.append((name, raceTime))
                continue
            print(raceTime)
            raceTime = time.strptime(raceTime, "%H:%M:%S")
            points = calcPoints(raceTime, raceDist, ageCat)

            addRaceToFile(name, raceName, raceDist, raceDate, time.strftime(timeFormat, raceTime), points)
    
    print("NOT ADDED: ")
    for person in notAdded:
        print(person)
        
# MENU OPTION P (Parkruns)
def addParkruns():
    raceDate = input("Date: ")
    if raceDate == "": return None

    while True:
        print("------------------------------------------------------")
        print(f"PARKRUN - {raceDate}")
        valid = False
        while not valid:
            name = input("Name: ")
            if name == "": return None
            try:
                ageCat = getAgeCat(name)
                valid = True
            except FileNotFoundError:
                newPerson = input("This person doesn't exist yet. Create a file for them? (y/n) ")
                if newPerson.lower() == "y": 
                    createNewPerson(name)
                    ageCat = getAgeCat(name)
                    valid = True
        
        addRaceToFile(name, "parkrun", "", raceDate, "", 1)

# MENU OPTION S (Summary Sheet)
def summarySheet():
    club50List = []
    club100List = []
    
    for name in os.listdir("People Files"):
        f = open(os.path.join("People Files", name), "r")
        fileLines = f.readlines()
        points = int(fileLines[4].strip()[6:])
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
        
    summary50 = open(os.path.join("Summary Sheets", dateForFile, " CLUB 50" + ".txt"), "w")
    summary100 = open(os.path.join("Summary Sheets", dateForFile, " CLUB 100" + ".txt"), "w")
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
