from .models import *
from api import app
from flask import jsonify


@app.route("/meets", methods=["GET"])
def getMeets():
    pass
