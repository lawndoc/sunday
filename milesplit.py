from bs4 import BeautifulSoup
import json
from mongoengine import *
from requests_html import HTMLSession

connect("xcstats20")


class Result(EmbeddedDocument):
    name = StringField(required=True)
    school = StringField(required=True)
    time = StringField(required=True)


class Meet(Document):
    name = StringField(required=True)
    date = DateField()
    boysResults = ListField()
    girlsResults = ListField()


class Athlete(EmbeddedDocument):
    gender = StringField(required=True)
    name = StringField(required=True)
    school = StringField(required=True)
    meets = ListField()


class School(Document):
    boys = ListField(EmbeddedDocumentField(Athlete))
    girls = ListField(EmbeddedDocumentField(Athlete))
    classSize = StringField(required=True)


class MileSplit():
    def __init__(self):
        pass

    def addMeetResults(self, url):
        formattedUrl = url
        if "raw" in formattedUrl:
            formattedUrl = url[url.index("raw")] + "formatted"
        session = HTMLSession()
        page = session.get(formattedUrl)
        page.html.render()
        soup = BeautifulSoup(page.html.html, "html.parser")

        # get meet name
        meet = soup.select("h1.meetName")[0]

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
                place, name, grade, school, time, points = (field.get_text() for field in finish.find_all("td"))  # nice
                result = Result(name=" ".join(name.split()),
                                school=" ".join(school.split()),
                                time=" ".join(time.split()))
                print(json.loads(result.to_json()))
            # print(results[sectionNum].get_text().strip())


