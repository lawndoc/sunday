#!/usr/bin/env python3

"""
File: wipeSchools.py
Author: C.J. May
Description: This script is to be used to delete all school documents from the
    database. This was initially necessary to rebuild the data after having an
    issue with out of state schools being matched to in-state teams. It is
    easier to rebuild the database than to selectively remove athletes who are
    not supposed to be on each team.
"""
import sys, os
# add app packages to path
sys.path.insert(1, os.path.join(sys.path[0], '../..'))

from app.models import *
from config import Config
from mongoengine import connect

if Config.DB_URI:
    connect(db=Config.DB_NAME,
            username=Config.DB_USER,
            password=Config.DB_PASS,
            host=Config.DB_URI)
    print("Connected to remote database.")
else:
    connect(Config.LOCALDB)
    print("Connected to local database.")

for school in School.objects:
    print(f"Deleting {school.name}...", end=" ", flush=True)
    school.delete()
    print("Done.")
