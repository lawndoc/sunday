from bs4 import BeautifulSoup
import difflib
from fuzzywuzzy import process
import json
from mongoengine import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

connect("xcstats20")


class Result(EmbeddedDocument):
    name = StringField(required=True)
    school = StringField(required=True)
    time = StringField(required=True)


class Meet(Document):
    name = StringField(required=True)
    date = DateField(required=True)
    boysResults = ListField(EmbeddedDocumentField(Result))
    girlsResults = ListField(EmbeddedDocumentField(Result))


class Athlete(EmbeddedDocument):
    gender = StringField(required=True)
    name = StringField(required=True)
    school = StringField(required=True)
    meets = ListField()


class School(Document):
    name = StringField(required=True)
    classSize = StringField(required=True)
    boys = ListField(EmbeddedDocumentField(Athlete))
    girls = ListField(EmbeddedDocumentField(Athlete))


class MileSplit():
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",
                                       options=self.chrome_options)
        self.boyTeams = list(self.initBoyTeams())
        self.girlTeams = list(self.initGirlTeams())

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
        # initialize school name matching cache
        matchCache = {}
        # do for each 5k race
        for sectionNum in range(len(headers)):
            sectionTitle = headers[sectionNum].get_text().strip()
            sectionTitle = sectionTitle[:sectionTitle.index("\n")]
            # check if html section is a boys 5k, girls 5k, or neither
            if ("boys 5000" in sectionTitle.lower()):
                # print(sectionTitle)
                gender = "m"
            elif ("girls 5000" in sectionTitle.lower()):
                # print(sectionTitle)
                gender = "f"
            else:
                continue
            # parse every result from this race
            for finish in results[sectionNum].find_all("tr"):
                place, name, grade, school, time, points = ((field.get_text() if "data-text" not in field.attrs else (field.get_text() if not field["data-text"] else field["data-text"])) for field in finish.find_all("td"))  # nice
                # standardize school name
                schoolName = self.search(gender=gender, school=(" ".join(school.split())), cache=matchCache)
                # TODO: standardize athlete name
                # create mongo result document
                result = Result(name=" ".join(name.split()),
                                school=schoolName,
                                time=" ".join(time.split()))
                # add result to mongo meet document
                if gender == "m":
                    meetDoc.boysResults.append(result)
                elif gender == "f":
                    meetDoc.girlsResults.append(result)
                else:
                    raise Exception("Tried to add result without gender... How did this happen?")
                # add school if not already in db
                schoolMatch = School.objects(name__exact=schoolName)
                if not schoolMatch.count():
                    schoolDoc = School(name=schoolName, classSize=self.getClass(gender, schoolName), boys=[], girls=[])
                else:
                    schoolDoc = schoolMatch[0]
                # TODO: add athlete if not already in db
                # TODO: add meet to athlete's meets
                print(json.loads(result.to_json()))
        print(meet)
        print(date)

    def getClass(self, gender, schoolName):
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

    def search(self, gender, school=None, conference=None, meet=None, cache=None):
        if school:
            # trim 'High School' off of school name
            if "High School" in school:
                school = school[:school.index("High School")]
            # try cache first
            if cache:
                try:
                    return cache[school]
                except KeyError:  # school not in cache
                    pass
            # otherwise match school to closest standardized school name
            if gender == "m":
                return process.extract(school, self.boyTeams)[0][0]
            elif gender == "f":
                return process.extract(school, self.girlTeams)[0][0]
            else:
                raise Exception("Tried to match a school with an invalid gender... How did this happen?")
        else:
            raise Exception("Made call to search without specifying any search query!")

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
