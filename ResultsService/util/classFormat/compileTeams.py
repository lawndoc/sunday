#!/usr/bin/env python3

"""
File: compileTeams.py
Author: C.J. May
Description:
    This script is not very useful, it was saved as an attempt to fix an issue, but I decided
    to go a different route. I saved the code in case it can be modified to do something
    useful later.
    
    Input files: boyClassesFormatted.json, girlClassesFormatted.json
        - These are the files outputted by sortBoys.py and sortGirls.py
    Output file: schools.json
        - This is an authoritative list of all school names sorted alphabetically
        - Currently doesn't specify whether it is boys or girls (not very useful)
"""

import json

schoolSet = set()

with open("boyClassesFormatted.json", "r") as bj:
    boysData = json.load(bj)
    print("4A teams: " + str(len(boysData["4A"])))
    for school in boysData["4A"]:
        if school:
            schoolSet.add(school)
    for school in boysData["3A"]:
        if school:
            schoolSet.add(school)
    for school in boysData["2A"]:
        if school:
            schoolSet.add(school)
    for school in boysData["1A"]:
        if school:
            schoolSet.add(school)


with open("girlClassesFormatted.json", "r") as gj:
    girlsData = json.load(gj)
    print("4A teams: " + str(len(girlsData["4A"])))
    for school in girlsData["4A"]:
        if school:
            schoolSet.add(school)
    for school in girlsData["3A"]:
        if school:
            schoolSet.add(school)
    for school in girlsData["2A"]:
        if school:
            schoolSet.add(school)
    for school in girlsData["1A"]:
        if school:
            schoolSet.add(school)

schools = list(schoolSet)
schools.sort()

with open("schools.json", "w+") as of:
    of.write('{\n\t"schools": [\n')
    for school in schools[:-1]:
        of.write('\t\t"' + school + '",\n')
    of.write('\t\t"' + schools[-1] + '"\n\t]\n}')
