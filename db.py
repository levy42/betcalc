from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class OutcomeType(db.Model):
    __tablename__ = 'outcome_types'
    column_searchable_list = ('id', 'name')
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)
    code = db.Column(db.String)
    sport_id = db.Column(db.Integer)


class Sport(db.Model):
    __tablename__ = 'sports'
    column_searchable_list = ('id', 'name')
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)


def to_dict(result):
    if isinstance(result, list):
        _list = []
        for row in result:
            _list.append({x.name: getattr(row, x.name) for x in
                          row.__table__.columns})
        return _list
    else:
        return {x.name: getattr(result, x.name) for x in
                result.__table__.columns}
