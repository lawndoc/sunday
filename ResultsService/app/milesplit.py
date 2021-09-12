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
        """ A web scraper that grabs and parses results from MileSplit XC meet result URLs """
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
        """ Parse XC meet results from the given URL and update the mongo database """
        if "raw" in url:
            rawUrl = url[:url.index("raw")+len("raw")]
            return self.scrapeRaw(rawUrl)
        else:
            formattedUrl = url[:url.index("formatted")+len("formatted")]
            return self.scrapeFormatted(formattedUrl)

    def scrapeRaw(self, url):
        """ Parse meet results from a raw text page and save to a mongoDB meet doc """
        # load webpage
        self.driver.get(url)
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
        data = soup.select("pre")[0].get_text().strip()
        print("Results:")
        lines = data.split("\n")
        i = 0
        # keep track of which line we are on
        while i < len(lines):
            if not lines[i]:  # blank line
                pass
            elif "=" in lines[i]:  # part of the column headers -- skip line
                pass
            elif "time" in lines[i].lower():  # results column headers -- skip line
                pass
            elif "points" in lines[i].lower():  # team score column headers -- skip line
                pass
            elif "Team Score" in lines[i]:  # beginning of team scores
                state = "teamscore"
            elif "Boys 5,000 Meter" in lines[i]:  # start parsing boys results
                state = "results"
                gender = "m"
            elif "Girls 5,000 Meter" in lines[i]:  # start parsing girls results
                state = "results"
                gender = "f"
            elif state == "teamscore":  # not reading results -- skip line
                pass
            elif state == "results":
                # parse result and add to school/athlete doc
                result = self.parseRawResult(lines[i], gender, meet)
                # add result to meet doc
                self.updateMeetDoc(result, gender, meetDoc)
            else:
                raise ValueError("Reached an unexpected state while parsing raw results.")
            i += 1
        self.saveMeetDoc(meet, meetDoc)

    def parseRawResult(self, line, gender, meet):
        """ Parse a single result from a line of raw text and save it to a mongoDB school doc """
        # initialize empty fields for keeping track of parsing state
        place = 0
        name = ""
        nameBuilder = []
        grade = 0
        school = ""
        schoolBuilder = []
        time = ""
        for column in line.split(" "):
            if not column:  # blank split -- skip
                continue
            if place == 0:  # first column is athlete's place
                place = int(column)
                continue
            if not name:
                if not column.isnumeric():  # still reading athlete's name
                    nameBuilder.append(column)
                else:  # we've reached the grade column, join all parts of the athlete's name
                    name = " ".join(nameBuilder)
                    grade = column
                continue
            if not school:
                if ":" not in column:  # still reading school name
                    schoolBuilder.append(column)
                else:  # we've reached the time column, join all parts of the school's name
                    school = " ".join(schoolBuilder)
                    time = column
        # create result doc and add to school doc
        result = self.updateSchoolDoc(name, grade, school, time, meet, gender)
        return result

    def scrapeFormatted(self, url):
        """ Parse meet results from a formatted page and save to a mongoDB meet doc """
        # load webpage
        self.driver.get(url)
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
                # parse result and add to school/athlete doc
                result = self.parseFormattedResult(finish, gender, meet)
                # add result to meet doc
                self.updateMeetDoc(result, gender, meetDoc)
            self.saveMeetDoc(meet, meetDoc)

    def parseFormattedResult(self, finish, gender, meet):
        """ Parse a single result from a formatted field and save it to a mongoDB school doc """
        # parse fields from result
        place, name, grade, school, time, points = ((field.get_text() if "data-text" not in field.attrs else (field.get_text() if not field["data-text"] else field["data-text"])) for field in finish.find_all("td"))  # nice
        # create result doc and add to school doc
        result = self.updateSchoolDoc(name, grade, school, time, meet, gender)
        return result


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
    def formatDate(rawDate):
        """ Format the date to match the database schema """
        dtDate = datetime.datetime.strptime(rawDate, "%b %d, %Y")
        date = dtDate.strftime("%Y-%m-%d")
        return date

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
