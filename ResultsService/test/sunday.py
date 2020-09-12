import sys, os
# add app packages to path
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from app.milesplit import MileSplit
from app.models import *
from config import Config
from mongoengine import *
import random
from time import sleep

scraper = MileSplit()

print("""
  /$$$$$$                            /$$                    
 /$$__  $$                          | $$                    
| $$  \__/ /$$   /$$ /$$$$$$$   /$$$$$$$  /$$$$$$  /$$   /$$
|  $$$$$$ | $$  | $$| $$__  $$ /$$__  $$ |____  $$| $$  | $$
 \____  $$| $$  | $$| $$  \ $$| $$  | $$  /$$$$$$$| $$  | $$
 /$$  \ $$| $$  | $$| $$  | $$| $$  | $$ /$$__  $$| $$  | $$
|  $$$$$$/|  $$$$$$/| $$  | $$|  $$$$$$$|  $$$$$$$|  $$$$$$$
 \______/  \______/ |__/  |__/ \_______/ \_______/ \____  $$
                                                   /$$  | $$
An automated stat taking program.                 |  $$$$$$/
                                                   \______/ 
                                            author: C.J. May

""")


def enterResults():
    while True:
        print("\nEnter MileSplit meet URL or type 'exit'")
        url = input("MileSplit URL: ")
        if url == "exit":
            break
        else:
            try:
                scraper.addMeetResults(url)
            except Exception as e:
                print("Invalid URL... Try again please.")
                continue


def bulkScrape():
    print("\nEnter path of MileSplit URL list")
    path = input("MileSplit URL list: ")
    with open(path, "r") as urls:
        for url in urls:
            try:
                scraper.addMeetResults(url)
                print("Added a meet...")
                sleep(random.uniform(5.0, 10.0))
            except Exception as e:
                raise e
                print("Invalid URL {}\n Trying next URL...".format(url))
                continue


def exportResults():
    if Config.DB_URI:
        connect(db=Config.DB_NAME,
                username=Config.DB_USER,
                password=Config.DB_PASS,
                host=Config.DB_URI)
    else:
        connect(Config.LOCALDB)
        for classSize in ["1A", "2A", "3A", "4A"]:
            print("Generating stat sheets for {}".format(classSize))
            schools = School.objects(classSize__exact=classSize)
            meets = Meet.objects()

            meetIndexes = {}
            formattedBoysResults = []
            formattedGirlsResults = []
            firstRow = ["School", "Name", "Year"]
            i = 3
            for meet in meets:
                firstRow.append(meet.name+" - "+str(meet.date))
                meetIndexes[meet.name] = i
                i += 1
            formattedBoysResults.append(firstRow)
            formattedGirlsResults.append(firstRow)
            for school in schools:
                schoolName = school.name
                for boy in school.boys:
                    row = [None] * len(firstRow)
                    row[0] = schoolName
                    row[1] = boy.name
                    row[2] = boy.year
                    for result in boy.meets:
                        meetIndex = meetIndexes[result.meet]
                        row[meetIndex] = result.time
                    formattedBoysResults.append(row)
                for girl in school.boys:
                    row = [None] * len(firstRow)
                    row[0] = schoolName
                    row[1] = girl.name
                    row[2] = girl.year
                    for result in girl.meets:
                        meetIndex = meetIndexes[result.meet]
                        row[meetIndex] = result.time
                    formattedGirlsResults.append(row)
            with open("/home/doctormay6/Desktop/boys{}Stats.csv".format(classSize), "w+") as bStats:
                for row in formattedBoysResults:
                    bStats.write(",".join(str(field).replace(",","") for field in row) + "\n")
            with open("/home/doctormay6/Desktop/girls{}Stats.csv".format(classSize), "w+") as bStats:
                for row in formattedGirlsResults:
                    bStats.write(",".join(str(field).replace(",","") for field in row) + "\n")



if __name__ == "__main__":
    options = {"1": ["Scrape results", enterResults],
               "2": ["Bulk scrape results", bulkScrape],
               "3": ["Export results to csv", exportResults],
               "exit": ["Exit program", exit]}
    while True:
        print()
        for option in range(len(options)-1):
            print(str(option+1) + ": " + options[str(option+1)][0])
        print("exit: Exit program")
        choice = input("Please pick an option: ")
        if choice not in options.keys():
            print("Invalid choice.")
            continue
        options[str(choice)][1]()
