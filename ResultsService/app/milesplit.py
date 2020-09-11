from app.models import *
from bs4 import BeautifulSoup
from fuzzywuzzy import process
import json
from mongoengine import connect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class MileSplit:
    def __init__(self):
        connect("xcstats20")
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",
                                       options=self.chrome_options)
        self.boyTeams = list(self.initBoyTeams())
        self.girlTeams = list(self.initGirlTeams())
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
        date = soup.select("div.date")[0].find_all("time")[0].get_text().strip()
        # create empty mongo meet document
        meetDoc = Meet(name=meet, date=date, boysResults=[], girlsResults=[])
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
                # print(sectionTitle)
                gender = "m"
            elif "girls 5000" in sectionTitle.lower():
                # print(sectionTitle)
                gender = "f"
            else:
                continue
            # parse every result from this race
            for finish in results[sectionNum].find_all("tr"):
                result = self.generateResult(finish, gender, meet)
                # add result to mongo meet document
                if gender == "m":
                    meetDoc.boysResults.append(result)
                elif gender == "f":
                    meetDoc.girlsResults.append(result)
        # clear cache and save meet to db
        self.matchCache = {}
        meetDoc.save()  # done!

    def generateResult(self, finish, gender, meet):
        place, name, grade, school, time, points = ((field.get_text() if "data-text" not in field.attrs else (field.get_text() if not field["data-text"] else field["data-text"])) for field in finish.find_all("td"))  # nice
        # standardize school name
        schoolName = self.search(gender=gender, school=(" ".join(school.split())))
        athleteName = " ".join(name.split())
        # create mongo result document
        result = Result(name=athleteName,
                        school=schoolName,
                        meet=meet,
                        time=" ".join(time.split()))
        # update school stats db
        # add school if not already in db
        schoolQuery = School.objects(name__exact=schoolName)
        if not schoolQuery.count():
            schoolDoc = School(name=schoolName, classSize=self.getClass(gender, schoolName), boys=[], girls=[])
        else:
            schoolDoc = schoolQuery[0]
        # add athlete if not already in school doc
        if gender == "m":
            try:  # update existing athlete
                athleteDoc = School.objects(boys__name=athleteName)[0]
                athleteDoc.meets.append(result)
            except IndexError:  # athlete not in School doc yet
                athleteDoc = Athlete(name=athleteName, gender=gender, school=schoolName, meets=[])
                athleteDoc.meets.append(result)
                # add athlete to school doc
                schoolDoc.boys.append(athleteDoc)
        elif gender == "f":
            try:  # update existing athlete
                athleteDoc = School.objects(girls__name=athleteName)[0]
                athleteDoc.meets.append(result)
            except IndexError:  # athlete not in School doc yet
                athleteDoc = Athlete(name=athleteName, gender=gender, school=schoolName, meets=[])
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
            if self.matchCache:
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
        if gender == "m":
            file = "boy"
        else:
            file = "girl"
        with open("static/"+file+"ClassesFormatted.json", "r") as classesFile:
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
        with open("static/boyClassesFormatted.json", "r") as boySchools:
            classes = json.load(boySchools)
            for classSize in classes:
                for team in classSize:
                    standardSchools.add(team)
        return standardSchools

    @staticmethod
    def initGirlTeams():
        standardSchools = set()
        with open("static/girlClassesFormatted.json", "r") as girlSchools:
            classes = json.load(girlSchools)
            for classSize in classes:
                for team in classSize:
                    standardSchools.add(team)
        return standardSchools
