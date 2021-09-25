import sys, os
# add previous dir to path
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from app.milesplit import MileSplit
from app.models import *
from config import Config
from mongoengine import connect
import xlsxwriter

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
                # raise e
                print("Invalid URL... Try again please.")
                continue


def bulkScrape():
    print("\nEnter path of MileSplit URL list")
    path = input("MileSplit URL list: ")
    with open(path, "r") as urls:
        for url in urls:
            try:
                scraper.addMeetResults(url)
            except Exception as e:
                raise e
                # print("Invalid URL {}\n Trying next URL...".format(url))
                # continue


def exportResults():
    connect(host=Config.MONGODB_SETTINGS["host"])
    boysStats = xlsxwriter.Workbook('/home/doctormay6/Desktop/XCStatSheets/boysStats.xlsx')
    girlsStats = xlsxwriter.Workbook('/home/doctormay6/Desktop/XCStatSheets/girlsStats.xlsx')
    for classSize in ["1A", "2A", "3A", "4A"]:
        print("Generating stat sheets for {}".format(classSize))
        schools = School.objects(classSize__exact=classSize)
        meets = Meet.objects()
        boysSheet = boysStats.add_worksheet("{} Stats".format(classSize))
        girlsSheet = girlsStats.add_worksheet("{} Stats".format(classSize))

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
                row = [""] * len(firstRow)
                row[0] = schoolName
                row[1] = boy.name
                row[2] = boy.year
                for result in boy.meets:
                    meetIndex = meetIndexes[result.meet]
                    row[meetIndex] = result.time
                formattedBoysResults.append(row)
            for girl in school.girls:
                row = [""] * len(firstRow)
                row[0] = schoolName
                row[1] = girl.name
                row[2] = girl.year
                for result in girl.meets:
                    meetIndex = meetIndexes[result.meet]
                    row[meetIndex] = result.time
                formattedGirlsResults.append(row)
        # write stats to boysSheet
        for rowNum, row in enumerate(formattedBoysResults):
            for colNum, data in enumerate(row):
                if "." in str(data) and colNum not in [0, 1] and rowNum != 0:
                    data = data[:data.index(".")]
                if ":" in str(data):
                    data = data.replace(":", ".")
                boysSheet.write(rowNum, colNum, data)
        # write stats to girlsSheet
        for rowNum, row in enumerate(formattedGirlsResults):
            for colNum, data in enumerate(row):
                if "." in str(data) and colNum not in [0, 1] and rowNum != 0:
                    data = data[:data.index(".")]
                if ":" in str(data):
                    data = data.replace(":", ".")
                girlsSheet.write(rowNum, colNum, data)
    boysStats.close()
    girlsStats.close()


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
