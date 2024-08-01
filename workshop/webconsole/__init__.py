'''Основной модуль'''
import os
from flask import Flask
from . import routes

def create_app(test_config=None):
    '''Создаю приложение'''
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )
    app.app_context()

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(routes.bp)

    return app