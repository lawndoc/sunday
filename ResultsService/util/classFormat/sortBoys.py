#!/usr/bin/env python3

"""
File: sortBoys.py
Author: C.J. May
Description:
    Input file: boyClasses.txt
        - This is the list of boy's cross country school classifications from the IHSAA
        - The file is a text file and the contents are copied from the classification document posted by the IHSAA
    Output file: boyClassesFormatted.json
        - This is a formatted list with the schools for each class sorted in alphabetical order on separate lines
"""

a4 = []
a3 = []
a2 = []
a1 = []

with open("boyClasses.txt", "r") as inFile:
    for line in inFile:
        if not line.strip():
            continue
        split = line.split()
        schoolList = []
        i = 0
        word = split[i].strip()
        while not word.isnumeric():
            schoolList.append(word)
            i += 1
            word = split[i].strip()
        size = split[i+1]
        school = " ".join(schoolList)
        print(school)
        if size == "4A":
            a4.append(school)
        elif size == "3A":
            a3.append(school)
        elif size == "2A":
            a2.append(school)
        elif size == "1A":
            a1.append(school)

with open("boyClassesFormatted.json", "w+") as outFile:
    outFile.write('{"4A":[')
    for school in a4[:-1]:
        outFile.write('"' + school + '",')
    outFile.write('"' + a4[-1] + '"],')
    outFile.write('"3A":[')
    for school in a3[:-1]:
        outFile.write('"' + school + '",')
    outFile.write('"' + a3[-1] + '"],')
    outFile.write('"2A":[')
    for school in a2[:-1]:
        outFile.write('"' + school + '",')
    outFile.write('"' + a2[-1] + '"],')
    outFile.write('"1A":[')
    for school in a1[:-1]:
        outFile.write('"' + school + '",')
    outFile.write('"' + a1[-1] + '"]}')
