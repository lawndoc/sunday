from .models import *
from api import app
from flask import jsonify, request


@app.get("/meets")
def getMeets():
    """ Return all Meet documents (no results) with optional pagination """
    page = int(request.args.get('page',1))
    limit = int(request.args.get('limit',0))
    offset = (page-1) * limit
    print(limit)
    meets = Meet.objects.exclude("boysResults", "girlsResults").skip(offset).limit(limit)
    return jsonify(meets), 200

@app.get("/meets/<id>")
def getOneMeet(id: str):
    """ Return the specified Meet document with optional pagination for results """
    boysPage = int(request.args.get('boys_page',1))
    boysLimit = int(request.args.get('boys_limit',0))
    boysOffset = (boysPage-1) * boysLimit
    boysLast = boysOffset + boysLimit
    girlsPage = int(request.args.get('girls_page',1))
    girlsLimit = int(request.args.get('girls_limit',0))
    girlsOffset = (girlsPage-1) * girlsLimit
    girlsLast = girlsOffset + girlsLimit
    meet = Meet.objects.filter(id=id).fields(slice__boysResults=[boysOffset, boysLast],
                                             slice__girlsResults=[girlsOffset, girlsLast]).first()
    return jsonify(meet), 200

@app.get("/schools")
def getSchools():
    """ Return all School documents (no athlete list) with optional pagination """
    page = int(request.args.get('page',1))
    limit = int(request.args.get('limit',0))
    offset = (page-1) * limit
    meets = School.objects.exclude("boys", "girls").skip(offset).limit(limit)
    return jsonify(meets), 200

@app.get("/schools/<id>")
def getOneSchool(id: str):
    """ Return the specified School document """
    meet = School.objects(id=id).first()
    return jsonify(meet), 200