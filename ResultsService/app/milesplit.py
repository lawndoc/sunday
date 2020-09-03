from bs4 import BeautifulSoup
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
    boysResults = ListField()
    girlsResults = ListField()


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
        meet = soup.select("h1.meetName")[0]
        # TODO: get meet date
        # TODO: create meet document

        # parse result data
        data = soup.find_all("table")[0]
        headers = data.find_all("thead")
        results = data.find_all("tbody")
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
            for finish in results[sectionNum].find_all("tr"):
                place, name, grade, school, time, points = ((field.get_text() if "data-text" not in field.attrs else (field.get_text() if not field["data-text"] else field["data-text"])) for field in finish.find_all("td"))  # nice
                result = Result(name=" ".join(name.split()),
                                school=" ".join(school.split()),
                                time=" ".join(time.split()))
                # TODO: add result to meet according to gender

                # TODO: add school if not already in db
                # TODO: add athlete according to gender if not already in db
                # TODO: add meet to athlete's meets
                print(json.loads(result.to_json()))


