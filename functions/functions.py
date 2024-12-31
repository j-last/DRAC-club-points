import json
import os
import time
import datetime

# constants
timeFormat = "%H.%M.%S"

def runner_exists(name):
    people = os.listdir("People Files")
    if name + ".txt" in people:
        return True

def getNameFromUser():
    """Asks the user for a name and checks if they exist.
    If they don't exist, then the user is promted to create a file for them.
    """
    while True:
        # get name
        name = input("Name: ")
        if name == "": return

        # capitalise name
        names = name.split(" ")
        name = ""
        for sub_name in names:
            name += sub_name.capitalize() + " "
        name = name.strip()
        
        # check if they exist
        if runner_exists(name):
            return name
        # if they dont, promt to create a file for them
        else:
            createNewPerson = input("This person doesn't exist yet. Create a file for them? (y/n) ")
            if createNewPerson.lower() == "y": 
                createNewPerson(name)
                return name
            else: return


def getDistFromUser(): # gets valid dist from user or points value
    validDistances = ["5k", "5mi", "10k", "10mi", "half", "mara"]
    while True:
        raceDist = input("Distance (or points num): ")
        if raceDist == "": return
        elif raceDist in validDistances: return raceDist # race dist is a valid distance
        elif raceDist.isnumeric(): return raceDist # race dist is a valid points value
        else: print("This is not a valid distance or points value.")


def getTimeFromUser():
    while True:
        raceTime = input("Time: ")
        if raceTime == "": return ""
        elif raceTime.count(".") == 1:
            raceTime = "0." + raceTime

        try:
            raceTime = time.strptime(raceTime, timeFormat)
            return raceTime
        except ValueError:
            print(f"Invalid time format '{raceTime}'. Please try again.")


def getRaceDetailsFromUser():
    raceName = input("Race Name: ")
    if raceName == "": return

    raceDist = getDistFromUser()
    if raceDist == "": return

    raceDate = input("Date: ")
    if raceDate == "": return

    return raceName, raceDist, raceDate


# returns the age category of a person from their name
def getAgeCat(name):
    f = open(os.path.join("People Files", name + ".txt"), "r")
    lines = f.readlines()
    ageCat = lines[1][:-1] # removes newline character
    f.close()

    # changing age categories if not already done so
    if ageCat[-1] == "?":
        f = open(os.path.join("People Files", name + ".txt"), "w")
        print(name.upper())
        print("Remember to change U40 to 17-39")
        print(f"This person was {ageCat[:-1]}. If this has changed enter their new age category below.")
        new_age_cat = input()
        if new_age_cat == "":
            ageCat = ageCat[:-1]
            lines[1] = ageCat + "\n"
        elif new_age_cat.upper() == "MU17" or new_age_cat.upper() == "WU17":
            ageCat = new_age_cat.upper()
            lines[1] = ageCat + "\n"
            lines.insert(3, "PARKRUNS: 0\n")
        else:
            ageCat = new_age_cat.upper()
            lines[1] = ageCat + "\n"
        f.writelines(lines)
        f.close()
        
    return ageCat


# returns the amount of points a certain time at a cetain distance gets for an age category
def calcPoints(raceTime, dist, ageCat):

    standards = open("Standards.json")
    data = json.load(standards)
    standards.close()

    standards = data[ageCat][dist]

    points = 4
    for standardTime in standards:
        if raceTime <= time.strptime(standardTime, timeFormat):
            points += 1
    if points == 9: points += 1
    return points


def get_filelines(name):
    personFile = open(os.path.join("People Files", name + ".txt"), "r")
    fileLines = personFile.readlines()
    personFile.close()
    return fileLines

def write_filelines(name, lines_to_write):
    personFile = open(os.path.join("People Files", name + ".txt"), "w")
    personFile.writelines(lines_to_write)
    personFile.close()


def addRaceToFile(name, race, dist, date, time, points):
    fileLines = get_filelines(name)

    totalPoints = int(fileLines[2].strip()[6:])
    totalPoints += points
    fileLines[2] = "TOTAL: " + str(totalPoints) + "\n"

    if dist.isnumeric():
        fileLines.append(f"{date}, {race}, {points} points\n")
    else:
        fileLines.append(f"{date}, {race} {dist}, {time}, {points} points\n")

    write_filelines(name, fileLines)

    print(f"{points} POINTS added to {name.upper()}.")
    print(f"{name.upper()} is now on {totalPoints} POINTS.")


def add_parkrun_to_file(name, date):
    if getAgeCat(name) not in ["MU17", "WU17"]:
        print(f"{name.upper()} is not a junior. No new parkrun added.")
        print()
        return

    fileLines = get_filelines(name)

    totalPoints = int(fileLines[2].strip()[6:])
    totalPoints += 1
    fileLines[2] = "TOTAL: " + str(totalPoints) + "\n"

    numParkruns = int(fileLines[3].strip()[9:]) # gets number of parkruns from the file
    if int(numParkruns) >= 10:
        print(f"{name.upper()} Has already done 10 parkruns. No new parkrun added.")
        print()
        return
        
    numParkruns += 1
    
    fileLines[3] = "PARKRUNS: " + str(numParkruns) + "\n"
    fileLines.append(f"{date}, parkrun, 1 point\n")

    write_filelines(name, fileLines)
    print(f"1 POINTS added to {name.upper()}.")
    print()


def createNewPerson(name):
    print("------------------------------------------------------")
    print(f"CREATE FILE {name.upper()}.")
    
    validAges = ["MU17", "M17-39", "M40-44", "M45-49", "M50-54", "M55-59", "M60-64", "M65+",
                 "WU17", "W17-34", "W35-39", "W40-44", "W45-49", "W50-54", "W55-59", "W60-64", "W65+"]
    ageCat = ""
    while ageCat not in validAges:
        ageCat = input("Age category: ").upper()
    
    file_lines = ["-----------\n",
                  ageCat + "\n",
                  "TOTAL: 0\n",
                  "-----------\n",
                  "RACES:\n"]

    if ageCat in ["MU17", "WU17"]:
        file_lines.insert(3, "PARKRUNS: 0")

    write_filelines(name, file_lines)
    print(f"FILE CREATED for {name.upper()}")


def get_parkrun_dict():
    parkrun_file = open("parkruns.txt", "r")
    lines = parkrun_file.readlines()
    parkrun_file.close()

    newlines = {}
    for line in lines:
        name, total = line.split(" - ")
        total = int(total)
        newlines[name] = total
    return newlines

def add_to_history(racename):
    f = open("history.txt", "r")
    filelines = f.readlines()
    f.close()
    date_added = str(datetime.date.strftime(datetime.date.today(), "%d-%m-%Y"))
    filelines.insert(0, f"{date_added}, {racename}\n")
    f = open("history.txt", "w")
    f.writelines(filelines)
    f.close()