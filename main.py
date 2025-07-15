"""



DRAC CLUB POINTS

CLICK PLAY BUTTON (TOP RIGHT) TO START




























"""

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
    to_add = []
    not_added = []
    runnersAdded = 0
    print()
    print("--------------------------------")
    for name, raceTime in runners.items():
        if runner_exists(name):
            ageCat = getAgeCat(name)
            raceTime = time.strptime(raceTime, "%H:%M:%S")
            points = calcPoints(raceTime, raceDist, ageCat)
            raceTime = time.strftime(timeFormat, raceTime)
            to_add.append((name, raceTime, points))
            print(f"{name.upper()} - {raceTime} - {points} points")
        else: not_added.append((name, raceTime))
    print(f"{len(to_add)} RUNNERS ({len(not_added)} unrecognised)")
    answer = input("ADD THESE RESULTS? (y/n) ")
    if answer.lower() == "y":
        for name, raceTime, points in to_add:
            addRaceToFile(name, raceName, raceDist, raceDate, raceTime, points)
            runnersAdded += 1

        for name, raceTime in not_added:
            print("")
            print(f"{name.upper()} ({raceTime}) was not found. Enter their file name below.")
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
    if runnersAdded > 0:
        add_to_history(raceName)


def manualRaceEntry():
    runners_added = 0
    race_details = getRaceDetailsFromUser()
    if race_details is None: return

    raceName, raceDist, raceDate = race_details

    add_to_history(raceName)
    while True:
        print("------------------------------------------------------")
        print(f"{raceName.upper()} {raceDist.upper()} - {raceDate} ({runners_added} added so far)")

        name = getNameFromUser()
        if name is None: return None
        elif name == "": continue
        elif not runner_exists(name): continue

        ageCat = getAgeCat(name)
        print(ageCat)

        if raceDist.isnumeric():
            points = int(raceDist)
            addRaceToFile(name, raceName, raceDist, raceDate, "", points)
            runners_added += 1
        
        else:
            raceTime = getTimeFromUser()
            if raceTime is None: return None
            
            points = calcPoints(raceTime, raceDist, ageCat)

            raceTime = time.strftime(timeFormat, raceTime)
            addRaceToFile(name, raceName, raceDist, raceDate, raceTime, points)
            runners_added += 1


def addParkrunsAuto():
    raceDate = input("Date: ")
    if raceDate == "": return None

    web_text = input("CTRL+A then CTRL+C on the consolodated report website and CTRL+V here: ")
    runners = get_parkrunners(web_text)

    newlines = get_parkrun_dict()
    runners_added = 0
    not_added = []
    with open("don't add to parkrun list.txt") as f:
        dont_add = f.readlines()
        dont_add = list(map(str.upper, map(str.strip, dont_add)))

    for name in runners:
        if name.upper() in dont_add:
            continue
        if newlines.get(name) is not None:
                newlines[name] += 1
        else:
            newlines[name] = 1
        runners_added += 1
        write_parkruns(newlines)
        print(f"{name.upper()} has now done {newlines[name]} parkruns.")
        if runner_exists(name):
            add_parkrun_to_file(name, raceDate)
        else:
            not_added.append(name)

    print("\nNOT ADDED: ")
    for name in not_added:
        print(name)

    while True:
        print("If any of the people in the not added list are U17, enter their file name below: ")
        name = getNameFromUser()
        if name is None: break
        elif runner_exists(name):
            ageCat = getAgeCat(name)
            print(name.upper() + ", " + ageCat)
            add_parkrun_to_file(name, raceDate)
        print("")

    print(f"{runners_added} runners have been added.")

    add_to_history("parkrun")


def addParkruns():
    raceDate = input("Date: ")
    if raceDate == "": return None

    newlines = get_parkrun_dict()

    print("------------------------------------------------------")
    print(f"PARKRUN - {raceDate}")
    print("Write all names as they appear on the parkrun website. Don't create files unless they are u17.")

    while True:
        name = getNameFromUser()
        if name is None: break

        if newlines.get(name) is not None:
            newlines[name] += 1
        else:
            newlines[name] = 1
        write_parkruns(newlines)
        print(f"{name.upper()} has now done {newlines[name]} parkruns.")
        
        if runner_exists(name):
            add_parkrun_to_file(name, raceDate)
        else:
            print(f"If {name.upper()} is U17 enter their file name below: ")
            name = getNameFromUser()
            if name is None:
                print("No new parkrun added to their points file.")
                print()
                continue
            else:
                ageCat = getAgeCat(name)
                print(name.upper() + ", " + ageCat)
                add_parkrun_to_file(name, raceDate)
        print()
    
    write_parkruns(newlines)

    add_to_history("parkrun")


# MENU OPTION S (Summary Sheet)
def summarySheet():
    points_list = []
    
    for name in os.listdir("People Files"):
        print(name[:-4])
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
    
    open(os.path.join("Backups", dateForFile, "1 parkruns.txt"), "w").close()
    shutil.copy("parkruns.txt", 
                os.path.join("Backups", dateForFile, "1 parkruns.txt"))
      
    print(f"Backup made for {dateForFile}")

mainloop()

