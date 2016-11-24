import json

storage = None
MODELS_DIR = None
models_meta = {}


def init_storage(app):
    global storage, MODELS_DIR
    storage_type = app.config.get("STORAGE", "LOCAL")
    if storage_type == "LOCAL":
        storage = LocalStorage()
    elif storage_type == "REDIS":
        # TODO (implement redis storage)
        storage = RedisStorage()
    MODELS_DIR = app.config.get("MODELS_DIR", 'models')


def get_models_meta():
    return models_meta


def get_model(id):
    return storage.get_model(id)


def load_model(name):
    storage.load_model(name)


def delete_model(id):
    storage.delete_model(id)


class Parameter(object):
    def __init__(self, id, name, description, type):
        self.id = id
        self.name = name
        self.description = description
        self.type = type


class ModelMeta(object):
    def __init__(self, id, description, params, sport_id):
        self.id = id
        self.description = description
        self.params = params
        self.sport_id = sport_id


class LocalStorage(object):
    def __init__(self):
        self.models = {}

    def get_model(self, id):
        return self.models[id]

    def delete_model(self, id):
        del self.models[id]

    def load_model(self, name):
        model = json.loads(file("models/%s/%s.json" % (name, name)).read())
        for t in model['stage1'].values():
            if not t.get('values'):
                t['values'] = json.loads(
                        file("%s/%s/outcomes/%s" % (
                            MODELS_DIR, name,
                            t['outcome_type']['code'])).read())
        for t in model.get('stage2', {}).values():
            if not t.get('values'):
                t['values'] = json.loads(
                        file("%s/%s/outcomes/%s" % (
                            MODELS_DIR, name,
                            t['outcome_type']['code'])).read())
        self.models[model['id']] = model
        params = [Parameter(p['id'], p['name'], p['description'], p['type'])
                  for p in model['params']]
        models_meta[model['id']] = ModelMeta(model['id'], model['description'],
                                             params, model['sport_id'])


class RedisStorage(object):
    def __init__(self):
        pass

    def get_model(self, id):
        raise NotImplementedError

    def delete_model(self, id):
        raise NotImplementedError

    def load_model(self, name):
        raise NotImplementedError

