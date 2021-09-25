from .models import *
from api import app
from flask import jsonify, request


@app.route("/meets", methods=["GET"])
def getMeets():
    """ Return all Meet documents """
    page = int(request.args.get('page',1))
    limit = int(request.args.get('limit',0))  # TODO: test to see if this sets no limit
    meets = Meet.objects.exclude("boysResults", "girlsResults").paginate(page=page, per_page=limit)
    return jsonify(meets), 200

@app.route("/meets/<id>", methods=["GET"])
def getOneMeet(id: str):
    """ Return the specified Meet document """
    boysPage = int(request.args.get('boys-page',1))
    boysLimit = int(request.args.get('boys-limit',0))  # TODO: test to see if this sets no limit
    girlsPage = int(request.args.get('girls-page',1))
    girlsLimit = int(request.args.get('girls-limit',0))  # TODO: test to see if this sets no limit
    meet = Meet.objects.filter(id=id).fields(slice__boysResults=[boysPage-1, boysLimit],
                                             slice__girlsResults=[girlsPage-1, girlsLimit]).first()
    return jsonify(meet), 200

@app.route("/schools", methods=["GET"])
def getSchools():
    """ Return all School documents """
    page = int(request.args.get('page',1))
    limit = int(request.args.get('limit',0))  # TODO: test to see if this sets no limit
    meets = School.objects.exclude("boys", "girls").paginate(page=page, per_page=limit)
    return jsonify(meets), 200

@app.route("/schools/<id>", methods=["GET"])
def getOneSchool(id: str):
    """ Return the specified School document """
    meet = School.objects(id=id).first()
    return jsonify(meet), 200