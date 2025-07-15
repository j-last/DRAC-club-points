import json
import os
import time
import datetime

# constants
timeFormat = "%H.%M.%S"
VALID_AGES = ["MU17", "M17-39", "M40-44", "M45-49", "M50-54", "M55-59", "M60-64", "M65+",
                 "WU17", "W17-34", "W35-39", "W40-44", "W45-49", "W50-54", "W55-59", "W60-64", "W65+"]

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
        if "-" in name:
            name = name.replace("-"+name[name.index("-")+1], "-"+name[name.index("-")+1].upper())
            
        # check if they exist
        if runner_exists(name):
            return name
        # if they dont, promt to create a file for them
        else:
            createNewPerson = input("This person doesn't exist yet. Create a file for them? (y/n) ")
            if createNewPerson.lower() == "y":
                create_new_person(name)
                return name
            else: return name


def getDistFromUser(): # gets valid dist from user or points value
    validDistances = ["5k", "5mi", "10k", "10mi", "half","20mi", "mara"]
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
        ageCat = ageCat[:-1]
        print(name.upper())

        if ageCat == "MU40": ageCat = "M17-39"
        elif ageCat == "WU35": ageCat = "W17-34"

        print(f"This person was {ageCat}.")

        new_age_cat = None
        while new_age_cat not in VALID_AGES + [""]:
            new_age_cat = input("New age category (nothing to keep the same): ")
            new_age_cat = new_age_cat.upper()

        if new_age_cat == "":
            lines[1] = ageCat + "\n"
            new_age_cat = ageCat
        elif new_age_cat== "MU17" or new_age_cat == "WU17":
            lines[1] = new_age_cat + "\n"
            lines.insert(3, "PARKRUNS: 0\n")
        else:
            lines[1] = new_age_cat + "\n"

        f = open(os.path.join("People Files", name + ".txt"), "w")
        f.writelines(lines)
        f.close()
        ageCat = new_age_cat
    
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

    print(f"{points} POINTS added to {name.upper()} (Total: {totalPoints})")


def add_parkrun_to_file(name, date):
    if getAgeCat(name) not in ["MU17", "WU17"]:
        print(f"{name.upper()} is not a junior. No new parkrun added.")
        return

    fileLines = get_filelines(name)

    totalPoints = int(fileLines[2].strip()[6:])
    totalPoints += 1
    fileLines[2] = "TOTAL: " + str(totalPoints) + "\n"

    numParkruns = int(fileLines[3].strip()[9:]) # gets number of parkruns from the file
    if int(numParkruns) >= 10:
        print(f"{name.upper()} Has done 10+ parkruns. No new parkrun added.")
        return
        
    numParkruns += 1
    
    fileLines[3] = "PARKRUNS: " + str(numParkruns) + "\n"
    fileLines.append(f"{date}, parkrun, 1 point\n")

    write_filelines(name, fileLines)
    print(f"1 POINTS added to {name.upper()}.")
    print()


def create_new_person(name):
    print("------------------------------------------------------")
    print(f"CREATE FILE {name.upper()}.")

    ageCat = ""
    while ageCat not in VALID_AGES:
        ageCat = input("Age category: ").upper()
    
    file_lines = ["-----------\n",
                  ageCat + "\n",
                  "TOTAL: 0\n",
                  "-----------\n",
                  "RACES:\n"]

    if ageCat in ["MU17", "WU17"]:
        file_lines.insert(3, "PARKRUNS: 0\n")

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