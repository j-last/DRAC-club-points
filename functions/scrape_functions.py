import requests
from bs4 import BeautifulSoup as bs

def get_runners_and_times(url):
    race_runners = {}

    page = requests.get(url)
    soup = bs(page.content, "html.parser")
    runners = soup.find("tbody") # gets all 

    for runner in runners:
        runnerstring = runner.decode_contents()
        if "<td>Dereham Runners AC</td>" in runnerstring:
            runnerstring = runnerstring.split("<td")
            name = runnerstring[2][1:-5] + " " + runnerstring[3][1:-5]
            raceTime = runnerstring[-2][2:-8]

            race_runners[name] = raceTime
    
    return race_runners


def get_parkrunners(web_text):
    endindex = web_text.find("Dereham Runners AC")
    runners = []

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
            runners.append(name)
        web_text = web_text[endindex + 1 :]
        endindex = web_text.find("Dereham Runners AC")

    return runners


def write_parkruns(parkrun_dict):
    sorted_parkruns = []
    for name, number in parkrun_dict.items():
        sorted_parkruns.append((number, name))
    sorted_parkruns.sort(reverse=True)

    open("parkruns.txt", "w").close()
    parkrun_file = open("parkruns.txt", "a")
    for number, name in sorted_parkruns:
        parkrun_file.write(f"{name} - {number}\n")
    parkrun_file.close()
        