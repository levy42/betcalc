from flask import Flask, render_template, request
from api import api
from admin import admin
from db import db, Sport
import storage
import common
import betcalc

app = Flask(__name__)
app.config.from_pyfile("betcalc.conf")

db.init_app(app)
admin.init_app(app)
common.init_app(app)
# init storage
storage.init_storage(app)

app.register_blueprint(api)


@app.route('/')
def index():
    sports = Sport.query.all()
    return render_template('index.html', context='home', sports=sports)


@app.route('/<int:id>')
def sport(id):
    models = storage.get_models_meta().values()
    sport = Sport.query.get(id)
    return render_template('index.html', context='sport', models=models,
                           sport=sport)


@app.route('/<int:sport_id>/<int:id>')
def model(sport_id, id):
    model = storage.get_models_meta()[id]
    sport = Sport.query.get(sport_id)
    params_inputs = model.params
    params = {i: v for i, v in enumerate(request.args.values())}
    for i, p in params.items():
        setattr(params_inputs[i], "value", p)
    outcomes = None
    exception = None
    if params:
        try:
            outcomes = sorted(betcalc.calculate(model.id, params),
                              key=lambda x: x['outcome_type_id'])
        except Exception as e:
            exception = e.message
    return render_template('index.html', context='model', model=model,
                           sport=sport, params=params_inputs,
                           params_values=params.values(),
                           outcomes=outcomes, exeption=exception)


@app.route('/about')
def about_page():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(port=20000, host='0.0.0.0')
