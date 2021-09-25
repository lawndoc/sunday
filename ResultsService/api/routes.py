from .models import *
from app import app
from flask import jsonify


@app.route("/meets", methods=["GET"])
def getMeets():
    pass
