import json
import os
import time

# constants
timeFormat = "%H.%M.%S"

# returns the age category of a perosn from their name
def getAgeCat(name):
    f = open(os.path.join("People Files", name + ".txt"), "r")
    lines = f.readlines()
    ageCat = lines[1][:-1] # removes newline character
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


# adds the points to the persons file, along with other data about the race
def addRaceToFile(name, race, dist, date, time, points):
    personFile = open(os.path.join("People Files", name + ".txt"), "r")
    fileLines = personFile.readlines()
    personFile.close()

    totalPoints = int(fileLines[4].strip()[6:])
    totalPoints += points
    fileLines[4] = "TOTAL " + str(totalPoints) + "\n"

    if dist.isnumeric():
        fileLines.append(f"{date}, {race}, {points} points\n")
    elif race != "parkrun":
        fileLines.append(f"{date}, {race} {dist}, {time}, {points} points\n")
    else:
        numParkruns = fileLines[6].strip()[9:]
        if fileLines[2].strip() == "CLUB 100":
            print(f"{name.upper()} is part of 'CLUB 100'. No new parkrun added.")
            return None
        if int(numParkruns) >= 10:
            print(f"{name.upper()} Has already done 10 parkruns. No new parkrun added.")
            return None
        numParkruns = int(numParkruns)
        numParkruns += 1
        if numParkruns >= 10: removeFromParkrunToDo(name)
        fileLines[6] = "PARKRUNS " + str(numParkruns) + "\n"
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
    ageCat = input("Age category: ")
    club = ""
    while club != "50" or club != "100":
        club = input("CLUB 50 or 100? ")
    f = open(os.path.join("People Files", name + ".txt"), "w")
    if club == "50":
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
    elif club == "100":
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

    print(f"FILE CREATED for {name.upper()}")


def removeFromParkrunToDo(name):
    f = open("Parkruns Todo.txt", "r")
    fileData = f.readlines()
    f.close()

    for i in range(len(fileData)):
        if fileData[i].strip() == name:
            fileData[i] = ""

    f = open("Parkruns Todo.txt", "w")
    f.writelines(fileData)
    f.close()
    print(f"{name.upper()} has now done 10 parkruns. Removed from 'Parkruns Todo'.")
