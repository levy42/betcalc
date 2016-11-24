from flask import request

from common import Rest
from db import OutcomeType, Sport, to_dict
import storage as s
from betcalc import calculate as calc

api = Rest("api", __name__)


@api.route("/sports", cached=True)
def get_sports():
    return to_dict(Sport.query.all())


@api.route("/outcomes", cached=True)
def get_outcome_types():
    return to_dict(OutcomeType.query.all())


@api.route("/models")
def get_models():
    return s.get_models_meta()


@api.route("/calculate/<int:id>")
def calculate(id):
    return calc(id, {i: v for (i, v) in
                     enumerate(request.args['params'].split(','))})


@api.route("/load/<name>")
def add_model(name):
    s.load_model(name)


@api.route("/free/<id>")
def del_model(id):
    s.delete_model(id)
