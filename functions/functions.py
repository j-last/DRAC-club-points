import json
import os
import time

# constants
timeFormat = "%H.%M.%S"

def getNameFromUser(): # gets name of person and checks if they exist
    while True:
        name = input("Name: ")
        if name == "": return ""

        name = name.split(" ")
        for i in range(len(name)):
            name[i] = name[i].capitalize()
        
        formattedname = ""
        for subname in name:
            formattedname += subname + " "
        name = formattedname.strip()
        
        # change how this is checked
        try:
            getAgeCat(name)
            return name
        except FileNotFoundError:
            newPerson = input("This person doesn't exist yet. Create a file for them? (y/n) ")
            if newPerson.lower() == "y": 
                createNewPerson(name)
                return name

def getDistFromUser(): # gets valid dist from user or points value
    validDistances = ["5k", "5mi", "10k", "10mi", "half", "mara"]
    while True:
        raceDist = input("Distance (or points num): ")
        if raceDist == "": return ""
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
    if raceName == "": return ""

    raceDist = getDistFromUser()
    if raceDist == "": return ""

    raceDate = input("Date: ")
    if raceDate == "": return ""

    return raceName, raceDist, raceDate


# returns the age category of a person from their name
def getAgeCat(name):
    f = open(os.path.join("People Files", name + ".txt"), "r")
    lines = f.readlines()
    ageCat = lines[1][:-1] # removes newline character
    f.close()

    # changing age categories if not already done so
    f = open(os.path.join("People Files", name + ".txt"), "w")
    if ageCat[-1] == "?":
        print(name.upper())
        print(f"This person was {ageCat[:-1]}. If this has changed enter their new age category below. If not enter nothing.")
        print("Make sure to change all juniors to MU17 or WU17.")
        new_age_cat = input()
        if new_age_cat == "":
            ageCat = ageCat[:-1]
            lines[1] = ageCat + "\n"
        elif new_age_cat.upper() == "MU17" or new_age_cat.upper() == "WU17":
            ageCat = new_age_cat.upper()
            lines[1] = ageCat + "\n"
            lines.insert(2, "PARKRUNS: 0\n")
            # do something here
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

# NEED TO CHANGE
# split into add race and add parkrun seperately
# adds the points to the persons file, along with other data about the race
def addRaceToFile(name, race, dist, date, time, points):
    personFile = open(os.path.join("People Files", name + ".txt"), "r")
    fileLines = personFile.readlines()
    personFile.close()

    totalPoints = int(fileLines[2].strip()[6:])
    totalPoints += points
    fileLines[2] = "TOTAL: " + str(totalPoints) + "\n"

    if dist.isnumeric():
        fileLines.append(f"{date}, {race}, {points} points\n")
    elif race != "parkrun":
        fileLines.append(f"{date}, {race} {dist}, {time}, {points} points\n")
    else:
        if fileLines[2].strip() == "CLUB 100":
            print(f"{name.upper()} is part of 'CLUB 100'. No new parkrun added.")
            return None
        numParkruns = int(fileLines[3].strip()[9:]) # gets number of parkruns from the file
        if int(numParkruns) >= 10:
            print(f"{name.upper()} Has already done 10 parkruns. No new parkrun added.")
            return None
        
        numParkruns += 1
        
        fileLines[3] = "PARKRUNS: " + str(numParkruns) + "\n"
        fileLines.append(f"{date}, {race}, {points} point\n")

    personFile = open(os.path.join("People Files", name + ".txt"), "w")
    personFile.writelines(fileLines)
    personFile.close()

    print(f"{points} POINTS added to {name.upper()}.")
    print(f"{name.upper()} is now on {totalPoints} POINTS.")


# creates a new file for a person (with 0 points & parkruns)
def createNewPerson(name):
    print("------------------------------------------------------")
    print(f"CREATE FILE {name.upper()}.")
    
    validAges = ["MU17", "M17-39", "M40-44", "M45-49", "M50-54", "M55-59", "M60-64", "M65+",
                 "WU17", "W17-34", "W35-39", "W40-44", "W45-49", "W50-54", "W55-59", "W60-64", "W65+"]
    ageCat = ""
    while ageCat not in validAges:
        ageCat = input("Age category: ").upper()

    # NEED TO CHANGE
    club = ""
    while club != "50" and club != "100":
        club = input("CLUB 50 or 100? ")
        if club == "50":
            f = open(os.path.join("People Files", name + ".txt"), "w")
            f.writelines([
            "-----------\n",
            f"{ageCat}\n",
            f"CLUB {club}\n",
            "-----------\n",
            "TOTAL 0\n",
            "-----------\n",
            "PARKRUNS 0\n",
            "-----------\n",
            "RACES:\n"
                    ]) 
            f.close()
            fparkrun = open("Parkruns Todo.txt", "a")
            fparkrun.write(f"{name}\n")
            fparkrun.close()
            break
        elif club == "100":
            f = open(os.path.join("People Files", name + ".txt"), "w")
            f.writelines([
            "-----------\n",
            f"{ageCat}\n",
            f"CLUB {club}\n",
            "-----------\n",
            "TOTAL 0\n",
            "-----------\n",
            "RACES:\n"
                    ]) 
            f.close()
            break

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

#CHANGE
def add_parkrun_to_file(name, raceDate):
    age_cat = getAgeCat(name)
    if age_cat == "MU17" or age_cat == "WU17":
        addRaceToFile(name, "parkrun", "", raceDate, "", 1)

