from functools import wraps
from flask import Blueprint, jsonify, make_response
from flask_cache import Cache

LOG = None
cache = Cache(
    config={'CACHE_TYPE': 'simple'})


def init_app(app):
    global cache, LOG
    # cache = Cache(
    #     config={'CACHE_TYPE': app.config.get('CACHE_TYPE', 'simple')})
    LOG = app.logger


class MyException(Exception):
    pass


class Rest(Blueprint):
    def __init__(self, name, module, use_cache=True):
        super(Rest, self).__init__(name, module)
        if use_cache:
            self.cache = cache

    def route(self, rule, cached=False, timeout=None, **options):
        def decorator(f):
            endpoint = options.pop("endpoint", f.__name__)
            decorated = self.rest(f, cached, timeout)
            self.add_url_rule(rule, endpoint, decorated, **options)
            return f

        return decorator

    def rest(self, func, cached=False, timeout=None):
        @self.cache.cached(timeout=timeout)
        @wraps(func)
        def wrapped_with_cached(*args, **kwargs):
            try:
                data = func(*args, **kwargs)
                if data is None:
                    return make_response()
                if isinstance(data, (
                        dict, list, tuple, set, str, int, float, unicode)):
                    return jsonify(data)
                else:
                    return jsonify(data.__dict__)
            except Exception as e:
                LOG.error(e)
                res = make_response()
                res.data = str(e)
                res.status = '201'
                return res

        @wraps(func)
        def wrapped(*args, **kwargs):
            try:
                data = func(*args, **kwargs)
                if data is None:
                    return make_response()
                if isinstance(data, (
                        dict, list, tuple, set, str, int, float, unicode)):
                    return jsonify(data)
                else:
                    return jsonify(data.__dict__)
            except MyException as e:
                LOG.error(e)
                res = make_response()
                res.data = str(e)
                res.status = '201'
                return res

        return wrapped_with_cached if cached else wrapped
