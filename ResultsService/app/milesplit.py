from bs4 import BeautifulSoup
import difflib
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

    def addMeetResults(self, url):
        formattedUrl = url
        if "raw" in formattedUrl:
            formattedUrl = url[:url.index("raw")] + "formatted"
        else:
            formattedUrl = url[:url.index("formatted")+len("formatted")]
        self.driver.get(formattedUrl)
        # page = self.driver.execute_script("return document.body")
        # sleep(10)
        # soup = BeautifulSoup(page.get_attribute("innerHTML"), "html.parser")
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        # get meet name and date
        meet = soup.select("h1.meetName")[0].get_text().strip()
        date = soup.select("div.date")[0].find_all("time")[0].get_text().strip()
        # create mongo meet document
        meetDoc = Meet(name=meet, date=date, boysResults=[], girlsResults=[])

        # parse result data
        data = soup.find_all("table")[0]
        headers = data.find_all("thead")
        results = data.find_all("tbody")
        # do for each 5k race
        for sectionNum in range(len(headers)):
            sectionTitle = headers[sectionNum].get_text().strip()
            sectionTitle = sectionTitle[:sectionTitle.index("\n")]
            if ("boys 5000" in sectionTitle.lower()):
                print(sectionTitle)
                gender = "m"
            elif ("girls 5000" in sectionTitle.lower()):
                print(sectionTitle)
                gender = "f"
            else:
                continue
            # parse every result from this race
            for finish in results[sectionNum].find_all("tr"):
                place, name, grade, school, time, points = ((field.get_text() if "data-text" not in field.attrs else (field.get_text() if not field["data-text"] else field["data-text"])) for field in finish.find_all("td"))  # nice
                result = Result(name=" ".join(name.split()),
                                school=" ".join(school.split()),
                                time=" ".join(time.split()))
                # add result to mongo meet document
                if gender == "m":
                    meetDoc.boysResults.append(result)
                elif gender == "f":
                    meetDoc.girlsResults.append(result)
                else:
                    raise Exception("Tried to add result without gender... How did this happen?")
                # add school if not already in db
                schoolExists = School.objects(name=school).count()
                if not schoolExists:
                    schoolDoc = School(name=school, classSize=self.getClass(gender, school), boys=[], girls=[])
                else:
                    schoolDoc = School.objects

                # TODO: add athlete according to gender if not already in db
                # TODO: add meet to athlete's meets
                print(json.loads(result.to_json()))
        print(meet)
        print(date)

    def getClass(self, gender, schoolName):
        if gender == "m":
            list = "boy"
        else:
            list = "girl"
        with open("static/"+gender+"ClassesFormatted.json", "r") as classesFile:
            classes = json.load(classesFile)
            # TODO: write this better when I am more awake
            matches4a = difflib.get_close_matches(schoolName, classes["4A"], n=1, cutoff=.7)
            matches3a = difflib.get_close_matches(schoolName, classes["3A"], n=1, cutoff=.7)
            matches2a = difflib.get_close_matches(schoolName, classes["2A"], n=1, cutoff=.7)
            matches1a = difflib.get_close_matches(schoolName, classes["1A"], n=1, cutoff=.7)
            found = ""
            if len(matches4a) > max(len(matches1a), len(matches2a), len(matches3a)):
                found = "4A"
            if len(matches3a) > max(len(matches1a), len(matches2a), len(matches4a)):
                found = "3A"
            if len(matches2a) > max(len(matches1a), len(matches3a), len(matches4a)):
                found = "2A"
            if len(matches1a) > max(len(matches2a), len(matches3a), len(matches4a)):
                found = "1A"
            if not found:
                raise Exception("Could not match school " + schoolName + " to a class size. No match found or a match in multiple classes was found.")
            return found
