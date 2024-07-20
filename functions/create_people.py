import os


def createNewPerson(name):
    f = open(os.path.join("People Files", name + ".txt"), "w")

    ageCat = input("Age Cat: ").upper()
    club = input("Club: ")
    points = input("Points: ")
    if club == "50":
        parkruns = input("Parkruns: ")
        f.writelines([
        "-----------\n",
        f"{ageCat}\n",
        f"CLUB {club}\n",
        "-----------\n",
        f"TOTAL {points}\n",
        "-----------\n",
        f"PARKRUNS {parkruns}\n",
        "-----------\n",
        "RACES:\n"
                  ]) 
        if parkruns != "10":
            fparkrun = open("Parkruns Todo.txt", "a")
            fparkrun.write(f"{name}\n")
            fparkrun.close()

    elif club == "100":
        f.writelines([
        "-----------\n",
        f"{ageCat}\n",
        f"CLUB {club}\n",
        "-----------\n",
        f"TOTAL {points}\n",
        "-----------\n",
        "RACES:\n"
                  ]) 
    f.close()
    print(f"FILE CREATED for {name.upper()}")
    print("------------------------------------------------------")


name = "temp"
while name != "":
    name = input("Name: ")
    createNewPerson(name)