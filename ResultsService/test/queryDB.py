import sys, os
# add api packages to path
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from api.models import *
from config import Config
from mongoengine import connect

if Config.DB_URI:
    connect(db=Config.DB_NAME,
            username=Config.DB_USER,
            password=Config.DB_PASS,
            host=Config.DB_URI)
else:
    connect(Config.LOCALDB)

meets = Meet.objects()

for meet in meets:
    print(meet["name"])
    print(meet["date"])
    print("\tBoys Results:")
    for result in meet["boysResults"]:
        print("\t\t", result["name"], ":", result["time"])
    print("\tGirls Results:")
    for result in meet["girlsResults"]:
        print("\t\t", result["name"], ":", result["time"])
