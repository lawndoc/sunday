#!/usr/bin/env python3

"""
This file was test code that helped implement Milesplit raw result scraping
before messing with the MongoDB
"""


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",
                          options=chrome_options)


def scrapeRaw(url):
    # load webpage
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # get meet name and date
    meet = soup.select("h1.meetName")[0].get_text().strip()
    print(f"Meet: {meet}")
    rawDate = soup.select("div.date")[0].find_all("time")[0].get_text().strip()
    print(f"Date: {rawDate}")
    # parse result data
    data = soup.select("pre")[0].get_text().strip()
    print("Results:")
    lines = data.split("\n")
    i = 0
    while i < len(lines):
        if not lines[i]:
            pass
        elif "=" in lines[i]:
            pass
        elif "time" in lines[i].lower():
            pass
        elif "points" in lines[i].lower():
            pass
        elif "Team Score" in lines[i]:
            state = "teamscore"
        elif "Boys 5,000 Meter" in lines[i]:
            state = "results"
            gender = "m"
        elif "Girls 5,000 Meter" in lines[i]:
            state = "results"
            gender = "f"
        elif state == "teamscore":
            pass
        elif state == "results":
            name, grade, school, time = parseRawResult(lines[i])
            print(f"Name: {name}\nGrade: {grade}\nSchool: {school}\nTime: {time}")
        else:
            raise ValueError("Reached an unexpected state while parsing raw results.")
        i += 1

def parseRawResult(line):
    place = 0
    name = ""
    nameBuilder = []
    grade = 0
    school = ""
    schoolBuilder = []
    time = ""
    for column in line.split(" "):
        if not column:
            continue
        if place == 0:
            place = int(column)
            continue
        if not name:
            if not column.isnumeric():
                nameBuilder.append(column)
            else:
                name = " ".join(nameBuilder)
                grade = column
            continue
        if not school:
            if ":" not in column:
                schoolBuilder.append(column)
            else:
                school = " ".join(schoolBuilder)
                time = column
    return [name, grade, school, time]




if __name__ == "__main__":
    scrapeRaw("https://ia.milesplit.com/meets/443493-trent-smith-invitational-charles-city-2021/results/758906/raw")
