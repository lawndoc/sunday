from milesplit import MileSplit

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
    url = ""
    while True:
        print("\nEnter MileSplit meet URL or type 'exit'")
        url = input("MileSplit URL: ")
        if url == "exit":
            break
        else:
            try:
                scraper.addMeetResults(url)
            except Exception as e:
                raise(e)
                print("Invalid URL... Try again please.")
                continue


def exportResults():
    print("TODO: implement function")


if __name__ == "__main__":
    options = {"1": ["Enter meet results", enterResults],
               "2": ["Export results to csv", exportResults],
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