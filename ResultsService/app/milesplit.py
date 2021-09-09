from app.models import *
from bs4 import BeautifulSoup
from config import Config
import datetime
from fuzzywuzzy import process
import json
from mongoengine import connect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep


class MileSplit:
    def __init__(self):
        if Config.DB_URI:
            connect(db=Config.DB_NAME,
                    username=Config.DB_USER,
                    password=Config.DB_PASS,
                    host=Config.DB_URI)
        else:
            connect(Config.LOCALDB)
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",
                                       options=self.chrome_options)
        self.boyTeams = self.initBoyTeams()
        self.girlTeams = self.initGirlTeams()
        self.matchCache = {}

    def addMeetResults(self, url):
        formattedUrl = url
        if "raw" in formattedUrl:
            formattedUrl = url[:url.index("raw")] + "formatted"
        else:
            formattedUrl = url[:url.index("formatted")+len("formatted")]
        # load webpage
        self.driver.get(formattedUrl)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        # get meet name and date
        meet = soup.select("h1.meetName")[0].get_text().strip()
        rawDate = soup.select("div.date")[0].find_all("time")[0].get_text().strip()
        date = self.formatDate(rawDate)
        # add meet if not already in db
        meetQuery = Meet.objects(name__exact=meet)
        if not meetQuery.count():
            meetDoc = Meet(name=meet, date=date, boysResults=[], girlsResults=[])
        else:  # meet found, update instead
            meetDoc = meetQuery[0]
        # parse result data
        data = soup.find_all("table")[0]
        headers = data.find_all("thead")
        results = data.find_all("tbody")
        # do for each 5k race
        for sectionNum in range(len(headers)):
            sectionTitle = headers[sectionNum].get_text().strip()
            sectionTitle = sectionTitle[:sectionTitle.index("\n")]
            # check if html section is a boys 5k, girls 5k, or neither
            if "boys 5000" in sectionTitle.lower():
                gender = "m"
            elif "girls 5000" in sectionTitle.lower():
                gender = "f"
            else:
                continue
            # parse every result from this race
            for finish in results[sectionNum].find_all("tr"):
                result = self.generateResult(finish, gender, meet)
                # add result if not already in meet doc
                if gender == "m":
                    foundResult = next((athlete for athlete in meetDoc.boysResults if athlete.name == result.name and athlete.time == result.time), None)
                    if not foundResult:
                        meetDoc.boysResults.append(result)
                elif gender == "f":
                    foundResult = next((athlete for athlete in meetDoc.girlsResults if athlete.name == result.name and athlete.time == result.time), None)
                    if not foundResult:
                        meetDoc.girlsResults.append(result)
        # clear cache and save meet to db
        self.matchCache = {}
        meetDoc.save()  # done!
        print("Added meet '{}'.".format(meet))

    def generateResult(self, finish, gender, meet):
        place, name, grade, school, time, points = ((field.get_text() if "data-text" not in field.attrs else (field.get_text() if not field["data-text"] else field["data-text"])) for field in finish.find_all("td"))  # nice
        # standardize school name
        schoolName = self.search(gender=gender, school=(" ".join(school.split())))
        schoolName = schoolName.strip()
        athleteName = " ".join(name.split())
        time = time.strip()
        if grade.split():
            year = datetime.date.today().year + (13 - (int(" ".join(grade.split()))))
        else:
            year = None
        # create mongo result document
        result = Result(name=athleteName,
                        school=schoolName,
                        meet=meet,
                        time=" ".join(time.split()))
        # update school stats db
        # add school if not already in db
        schoolQuery = School.objects(name__exact=schoolName)
        if not schoolQuery.count():
            schoolDoc = School(name=schoolName,
                               classSize=self.getClass(gender, schoolName),
                               boys=[],
                               girls=[])
        else:
            schoolDoc = schoolQuery[0]
        # add athlete if not already in school doc
        if gender == "m":
            foundAthlete = next((athlete for athlete in schoolDoc.boys if athlete["name"] == athleteName), None)
            if foundAthlete:
                # add meet result if not already in athlete doc
                foundMeet = next((meet for meet in foundAthlete.meets if meet["name"] == meet), None)
                if not foundMeet:
                    foundAthlete.meets.append(result)
                foundAthlete.meets.append(result)
                # add grad year if not already in athlete doc
                if not foundAthlete.year:
                    foundAthlete.year = year
            else:  # athlete not found, create and add meet result
                athleteDoc = Athlete(name=athleteName,
                                     gender=gender,
                                     school=schoolName,
                                     year=year,
                                     meets=[])
                athleteDoc.meets.append(result)
                # add athlete to school doc
                schoolDoc.boys.append(athleteDoc)
        elif gender == "f":
            foundAthlete = next((athlete for athlete in schoolDoc.girls if athlete["name"] == athleteName), None)
            if foundAthlete:
                # add meet result if not already in athlete doc
                foundMeet = next((meet for meet in foundAthlete.meets if meet["name"] == meet), None)
                if not foundMeet:
                    foundAthlete.meets.append(result)
                foundAthlete.meets.append(result)
                # add grad year if not already in athlete doc
                if not foundAthlete.year:
                    foundAthlete.year = year
            else:  # athlete not found, create and add meet result
                athleteDoc = Athlete(name=athleteName,
                                     gender=gender,
                                     school=schoolName,
                                     year=year,
                                     meets=[])
                athleteDoc.meets.append(result)
                # add athlete to school doc
                schoolDoc.girls.append(athleteDoc)
        schoolDoc.save()
        # send result back to update meet stats db
        return result

    def search(self, gender, school=None, conference=None, meet=None):
        if school:
            # trim 'High School' off of school name
            if "High School" in school:
                school = school[:school.index("High School")]
            # try cache first
            try:
                return self.matchCache[school]
            except KeyError:  # school not in cache
                pass
            # otherwise match school to closest standardized school name
            if gender == "m":
                match = process.extract(school, self.boyTeams)[0][0]
            elif gender == "f":
                match = process.extract(school, self.girlTeams)[0][0]
            self.matchCache[school] = match
            return match
        else:
            raise Exception("Made call to search without specifying a valid search query!")

    @staticmethod
    def formatDate(rawDate):
        dtDate = datetime.datetime.strptime(rawDate, "%b %d, %Y")
        date = dtDate.strftime("%Y-%m-%d")
        return date

    @staticmethod
    def getClass(gender, schoolName):
        if gender == "m":
            file = "boy"
        else:
            file = "girl"
        with open("../app/static/"+file+"ClassesFormatted.json", "r") as classesFile:
            classes = json.load(classesFile)
            if schoolName in classes["4A"]:
                return "4A"
            elif schoolName in classes["3A"]:
                return "3A"
            elif schoolName in classes["2A"]:
                return "2A"
            elif schoolName in classes["1A"]:
                return "1A"
            else:
                raise Exception("Could not match school " + schoolName + " to a class size. How did this happen?")

    @staticmethod
    def initBoyTeams():
        standardSchools = set()
        with open("../app/static/boyClassesFormatted.json", "r") as boySchools:
            classes = json.load(boySchools)
            for classSize in classes:
                for team in classes[classSize]:
                    standardSchools.add(team)
        return list(standardSchools)

    @staticmethod
    def initGirlTeams():
        standardSchools = set()
        with open("../app/static/girlClassesFormatted.json", "r") as girlSchools:
            classes = json.load(girlSchools)
            for classSize in classes:
                for team in classes[classSize]:
                    standardSchools.add(team)
        return list(standardSchools)
