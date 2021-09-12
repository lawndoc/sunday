from abc import ABC, abstractmethod
from app.models import *
from config import Config
import datetime
from fuzzywuzzy import process
import json
from mongoengine import connect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Scraper(ABC):
    def __init__(self):
        """ A web scraper that grabs and parses results from <website> meet result URLs """
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

    @abstractmethod
    def addMeetResults(self, url):
        """ Parse XC meet results from the given URL and update the mongo database

        Scraper class usage:
        - [object] self.driver (selenium.webdriver.Chrome)
        - [method] self.updateSchoolDoc(name, grade, school, time, meet, gender) -> Result
        - [method] self.updateMeetDoc(result, gender, meetDoc) -> None
        - [method] self.saveMeetDoc(meet, meetDoc) -> None
        
        """
        pass

    def updateSchoolDoc(self, name, grade, school, time, meet, gender):
        """ Update an athlete's doc with their result, and optionally create the school or athlete if they don't exist yet """
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

    def updateMeetDoc(self, result, gender, meetDoc):
        """ Add a result to the given meet doc """
        # add result if not already in meet doc
        if gender == "m":
            foundResult = next((athlete for athlete in meetDoc.boysResults if athlete.name == result.name and athlete.time == result.time), None)
            if not foundResult:
                meetDoc.boysResults.append(result)
        elif gender == "f":
            foundResult = next((athlete for athlete in meetDoc.girlsResults if athlete.name == result.name and athlete.time == result.time), None)
            if not foundResult:
                meetDoc.girlsResults.append(result)

    def saveMeetDoc(self, meet, meetDoc):
        """ Save the meet doc's changes to the remote database """
        # clear cache and save meet to db
        self.matchCache = {}
        meetDoc.save()  # done!
        print("Added meet '{}'.".format(meet))

    def search(self, gender, school=None, conference=None, meet=None):
        """ Match a result's school name to its standard name in the database """
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
    def getClass(gender, schoolName):
        """ Match a school to its class size """
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
        """ Initialize the list of standaridized boys school names """
        standardSchools = set()
        with open("../app/static/boyClassesFormatted.json", "r") as boySchools:
            classes = json.load(boySchools)
            for classSize in classes:
                for team in classes[classSize]:
                    standardSchools.add(team)
        return list(standardSchools)

    @staticmethod
    def initGirlTeams():
        """ Initialize the list of standaridized girls school names """
        standardSchools = set()
        with open("../app/static/girlClassesFormatted.json", "r") as girlSchools:
            classes = json.load(girlSchools)
            for classSize in classes:
                for team in classes[classSize]:
                    standardSchools.add(team)
        return list(standardSchools)