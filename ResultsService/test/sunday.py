import sys, os
# add app packages to path
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from app.milesplit import MileSplit
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
    print("TODO: implement function")


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
