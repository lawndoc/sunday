#!/usr/bin/env python3

"""
File: sortGirls.py
Author: C.J. May
Description:
        Input file: girlClasses.txt
            - This is the list of girl's cross country school classifications from IGHSAU
            - The file is a text file and the contents are copied from the classification document posted by IGHSAU
        Output file: girlClassesFormatted.json
            - This is a formatted list with the schools for each class sorted in alphabetical order on separate lines
"""

a4 = []
a3 = []
a2 = []
a1 = []

with open("girlClasses.txt", "r") as inFile:
    size = "4A"
    for line in inFile:
        if "2021 CROSS COUNTRY" in line:
            continue
        if "CLASS" in line:
            size = line[-3:-1]
            continue
        print(line)
        uncut = line.strip().split(" ")[1:]
        schoolList = []
        index = 0
        while not uncut[index].isnumeric():
            schoolList.append(uncut[index])
            index += 1
        school = " ".join(schoolList)
        if size == "4A":
            a4.append(school.title())
        elif size == "3A":
            a3.append(school.title())
        elif size == "2A":
            a2.append(school.title())
        elif size == "1A":
            a1.append(school.title())

a4.sort()
a3.sort()
a2.sort()
a1.sort()

with open("girlClassesFormatted.json", "w+") as outFile:
    outFile.write('{"4A":[')
    for school in a4[:-1]:
        print(school)
        outFile.write('"' + school + '",')
    outFile.write('"' + a4[-1] + '"],')
    outFile.write('"3A":[')
    for school in a3[:-1]:
        print(school)
        outFile.write('"' + school + '",')
    outFile.write('"' + a3[-1] + '"],')
    outFile.write('"2A":[')
    for school in a2[:-1]:
        print(school)
        outFile.write('"' + school + '",')
    outFile.write('"' + a2[-1] + '"],')
    outFile.write('"1A":[')
    for school in a1[:-1]:
        print(school)
        outFile.write('"' + school + '",')
    outFile.write('"' + a1[-1] + '"]}')
