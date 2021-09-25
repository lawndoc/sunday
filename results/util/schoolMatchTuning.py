#!/usr/bin/env python3

"""
File: schoolMatchtuning.py
Author: C.J. May
Description: This script is to be used to tune the score threshold when matching
    school names. This is important for determining when a school is not in Iowa
    so their athletes don't get added to an Iowa team with the most similar
    school name.

    Input files: boyClassesFormatted.json girlClassesFormatted.json
        - These should be the official lists from the ../app/static directory
"""

from fuzzywuzzy import process
import json

# out of state schools
outOfState = [("Onalaska", "m"),
              ("Riverdale High School", "m"),
              ("La Crosse Central", "m"),
              ("Minneapolis Washburn", "m"),
              ("Bloomington Jefferson", "m"),
              ("Aquinas", "m"),
              ("Liberty", "m"),
              ("Champlin Park", "m"),
              ("Saint Charles", "m"),
              ("Platteville", "m"),
              ("Rochester Century", "m"),
              ("Rochester John Marshall", "m"),
              ("Westby", "m"),
              ("Chatfield", "m")]

# in-state schools with weird formatting (ex. hyphens, abbreviations, etc.)
inStateTest =[("A-D-M", "m"),
              ("B-H-R-V", "m"),
              ("AGWSR", "m")]

def search(boyTeams, girlTeams, gender="m", school=None, conference=None, meet=None):
    """ Match a result's school name to its standard name in the database """
    if school:
        # trim 'High School' off of school name
        if "High School" in school:
            school = school[:school.index("High School")]
        # try cache first
        try:
            return matchCache[school]
        except KeyError:  # school not in cache
            pass
        # otherwise match school to closest standardized school name
        if gender == "m":
            match = process.extract(school, boyTeams)[0]
        elif gender == "f":
            match = process.extract(school, girlTeams)[0]
        print(match)
    else:
        raise Exception("Made call to search without specifying a valid search query!")

def initBoyTeams():
    """ Initialize the list of standaridized boys school names """
    standardSchools = set()
    with open("../app/static/boyClassesFormatted.json", "r") as boySchools:
        classes = json.load(boySchools)
        for classSize in classes:
            for team in classes[classSize]:
                standardSchools.add(team)
    return list(standardSchools)

def initGirlTeams():
    """ Initialize the list of standaridized girls school names """
    standardSchools = set()
    with open("../app/static/girlClassesFormatted.json", "r") as girlSchools:
        classes = json.load(girlSchools)
        for classSize in classes:
            for team in classes[classSize]:
                standardSchools.add(team)
    return list(standardSchools)

if __name__ == "__main__":
    matchCache = dict()
    boysTeams = initBoyTeams()
    girlsTeams = initGirlTeams()

    print("<---Out of state tests--->")
    for team in outOfState:
        search(boysTeams, girlsTeams, gender=team[1], school=team[0])
    print("\n<---Formatting tests--->")
    for team in inStateTest:
        search(boysTeams, girlsTeams, gender=team[1], school=team[0])