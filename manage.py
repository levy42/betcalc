from flask.ext.script import Manager
from main import app
from db import db

manager = Manager(app)


@manager.command
def initdb():
    """Creates all database tables."""
    db.create_all()


@manager.command
def dropdb():
    """Drops all database tables."""
    db.drop_all()


@manager.command
def create_outcomes():
    from db import OutcomeType
    import json
    outcomes = json.loads(open("analitics/outcomes.json").read())
    outcomes_type = []
    for o in outcomes:
        ot = OutcomeType()
        ot.code = o['code']
        ot.name = o['name']
        ot.sport_id = 1
        outcomes_type.append(ot)
    for o in outcomes_type:
        db.session.merge(o)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
