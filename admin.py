import os.path as op
from flask_admin import Admin
from flask_admin.contrib.sqlamodel import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from db import OutcomeType, Sport, db


class MyAdmin(Admin):
    def init_app(self, app):
        super(MyAdmin, self).init_app(app)
        models_dir = app.config.get('MODELS_DIR', 'models')
        admin.add_view(ModelView(OutcomeType, db.session))
        admin.add_view(ModelView(Sport, db.session))
        path = op.join(op.dirname(__file__), models_dir)
        admin.add_view(FileAdmin(path, '/models/', name='Models'))


admin = MyAdmin()
