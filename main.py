import os
import time
import datetime
import shutil
from functions.functions import *
from functions.scrape_functions import *

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


def urlRaceEntry():
    race_details = getRaceDetailsFromUser()
    if race_details is None: return

    raceName, raceDist, raceDate = race_details

    url = input("Copy and paste the totalRaceTiming URL: ")
    if url == "": return

    runners = get_runners_and_times(url)
    not_added = []
    runnersAdded = 0
    
    for name, raceTime in runners.items():
        if runner_exists(name):
            ageCat = getAgeCat(name)
            print(name.upper() + ", " + ageCat + ", " + raceTime)

            raceTime = time.strptime(raceTime, "%H:%M:%S")
            points = calcPoints(raceTime, raceDist, ageCat)

            raceTime = time.strftime(timeFormat, raceTime)
            addRaceToFile(name, raceName, raceDist, raceDate, raceTime, points)
            runnersAdded += 1
        else: not_added.append((name, raceTime))
        print("")

    print("NOT ADDED: ")
    for name, raceTime in not_added:
        print("")
        print(f"{name.upper()} ({raceTime}) not found. Enter their file name below.")
        name = getNameFromUser()
        if name is None:
            print("No new race added.")
        else:
            ageCat = getAgeCat(name)
            print(name.upper() + "," + ageCat + "," + raceTime)
            raceTime = time.strptime(raceTime, "%H:%M:%S")
            points = calcPoints(raceTime, raceDist, ageCat)

            raceTime = time.strftime(timeFormat, raceTime)
            addRaceToFile(name, raceName, raceDist, raceDate, raceTime, points)
            runnersAdded += 1
    print("")

    print(f"{runnersAdded} runners have been added.")
    add_to_history(raceName)


def manualRaceEntry():
    race_details = getRaceDetailsFromUser()
    if race_details is None: return

    raceName, raceDist, raceDate = race_details

    add_to_history(raceName)
    while True:
        print("------------------------------------------------------")
        print(f"{raceName.upper()} {raceDist.upper()} - {raceDate}")

        name = getNameFromUser()
        if name is None: return None

        ageCat = getAgeCat(name)
        print(ageCat)

        if raceDist.isnumeric():
            points = int(raceDist)
            addRaceToFile(name, raceName, raceDist, raceDate, "", points)
        
        else:
            raceTime = getTimeFromUser()
            if raceTime is None: return None
            
            points = calcPoints(raceTime, raceDist, ageCat)

            raceTime = time.strftime(timeFormat, raceTime)
            addRaceToFile(name, raceName, raceDist, raceDate, raceTime, points)


def addParkrunsAuto():
    raceDate = input("Date: ")
    if raceDate == "": return None

    web_text = input("CTRL+A then CTRL+C on the consolodated report website and CTRL+V here: ")
    runners = get_parkrunners(web_text)

    newlines = get_parkrun_dict()
    runners_added = 0
    not_added = []

    for name in runners:
        if runner_exists(name):
            add_parkrun_to_file(name, raceDate)
            if newlines.get(name) is not None:
                newlines[name] += 1
            else:
                newlines[name] = 1
            runners_added += 1
        else:
            not_added.append(name)

    write_parkruns(newlines)
    
    print("NOT ADDED: ")
    for name in not_added:
        print("")
        print(f"{name.upper()} not found. If they are U17 enter their file name below.")
        name = getNameFromUser()
        if name is None:
            print("No new parkrun added.")
        else:
            ageCat = getAgeCat(name)
            print(name.upper() + ", " + ageCat)
            add_parkrun_to_file(name, raceDate)
            runnersAdded += 1
    print("")
    print(f"{runners_added} runners have been added.")

    add_to_history("parkrun")


def addParkruns():
    raceDate = input("Date: ")
    if raceDate == "": return None

    newlines = get_parkrun_dict()

    print("------------------------------------------------------")
    print(f"PARKRUN - {raceDate}")

    while True:
        name = getNameFromUser()
        if name is None: break

        add_parkrun_to_file(name, raceDate)

        if newlines.get(name) is not None:
            newlines[name] += 1
        else:
            newlines[name] = 1
        print(f"{name.upper()} has now done {newlines[name]} parkruns.")
    
    write_parkruns(newlines)

    add_to_history("parkrun")


# MENU OPTION S (Summary Sheet)
def summarySheet():
    points_list = []
    
    for name in os.listdir("People Files"):
        f = open(os.path.join("People Files", name), "r")
        fileLines = f.readlines()
        points = int(fileLines[2].strip()[6:])
        f.close()

        points_list.append((points, name[:-4]))

    points_list.sort(reverse=True)

    lines_to_write = []
    for number, name in points_list:
        if number != 0:
            lines_to_write.append(f"{name} - {number}\n")

    dateForFile = str(datetime.date.strftime(datetime.date.today(), "%d-%m-%Y"))
    summary_sheet = open(os.path.join("Summary Sheets", dateForFile+".txt"), "w")
    summary_sheet.writelines(lines_to_write)
    print(f"Summary sheets for {dateForFile} made.")


def backup():
    dateForFile = str(datetime.date.strftime(datetime.date.today(), "%d-%m-%Y"))

    if not os.path.exists(os.path.join("Backups", dateForFile)):
        os.makedirs(os.path.join("Backups", dateForFile))

    for file in os.listdir("People Files"):
        open(os.path.join("Backups", dateForFile, file), "w").close()
        shutil.copy(os.path.join("People Files", file), 
                    os.path.join("Backups", dateForFile, file))
    
    open(os.path.join("Backups", dateForFile, "aaa parkruns.txt"), "w").close()
    shutil.copy("parkruns.txt", 
                os.path.join("Backups", dateForFile, "aaa parkruns.txt"))
      
    print(f"Backup made for {dateForFile}")

mainloop()

