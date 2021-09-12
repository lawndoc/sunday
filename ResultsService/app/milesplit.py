from app.models import *
from bs4 import BeautifulSoup
from app.interfaces import Scraper
import datetime


class MileSplit(Scraper):
    def __init__(self):
        """ A web scraper that grabs and parses results from MileSplit XC meet result URLs """
        super().__init__()

    def addMeetResults(self, url):
        """ Parse XC meet results from the given URL and update the mongo database

        Scraper class usage:
        - [object] self.driver (selenium.webdriver.Chrome)
        - [method] self.updateSchoolDoc(name, grade, school, time, meet, gender) -> Result
        - [method] self.updateMeetDoc(result, gender, meetDoc) -> None
        - [method] self.saveMeetDoc(meet, meetDoc) -> None

        Raw input accepted:
            - name
            - school
            - meet

        Formatted input needed:
            - grade -> int range 9-12
            - time -> str "XX:XX.XX"
            - gender -> str ("m"|"f")
        
        """
        if "raw" in url:
            rawUrl = url[:url.index("raw")+len("raw")]
            self.scrapeRaw(rawUrl)
        else:
            formattedUrl = url[:url.index("formatted")+len("formatted")]
            self.scrapeFormatted(formattedUrl)

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
            print(f"Adding new meet: {meet}")
            meetDoc = Meet(name=meet, date=date, boysResults=[], girlsResults=[])
        else:  # meet found, update instead
            print(f"Updating meet {meet}")
            meetDoc = meetQuery[0]
        # parse result data
        data = soup.select("pre")[0].get_text().strip()
        lines = data.split("\n")
        i = 0
        state = "skip"  # skip until we find results
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
                state = "skip"
            elif "Boys 5,000 Meter" in lines[i] or "Boys 3.1 Mile" in lines[i]:  # start parsing boys results
                state = "results"
                gender = "m"
            elif "Girls 5,000 Meter" in lines[i] or "Girls 3.1 Mile" in lines[i]:  # start parsing girls results
                state = "results"
                gender = "f"
            elif state == "skip":  # not reading results -- skip line
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
                if not column.isnumeric() and column not in ["-", "FR"]:  # still reading athlete's name
                    nameBuilder.append(column)
                else:  # we've reached the grade column, join all parts of the athlete's name
                    name = " ".join(nameBuilder)
                    if column in ["-", "FR"]:
                        grade = ""
                    else:
                        grade = column
                continue
            if not school:
                if ":" not in column:  # still reading school name
                    schoolBuilder.append(column)
                else:  # we've reached the time column, join all parts of the school's name
                    school = " ".join(schoolBuilder)
                    time = column
        # create result doc and add to school doc
#        print([place, name, grade, school, time])
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
            print(f"Adding new meet: {meet}")
            meetDoc = Meet(name=meet, date=date, boysResults=[], girlsResults=[])
        else:  # meet found, update instead
            print(f"Updating meet {meet}")
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

    @staticmethod
    def formatDate(rawDate):
        """ Format the date to match the database schema """
        dtDate = datetime.datetime.strptime(rawDate, "%b %d, %Y")
        date = dtDate.strftime("%Y-%m-%d")
        return date
