# -*- coding:utf-8 -*-
import httplib
import logging
import json
import logging.config
import uuid
from flask import Flask, Response, request
from flask.ext.migrate import Migrate
from flask.ext.security import Security, current_user
from utils.redis import RedisDB
from utils.enum import BaseEnum
from utils.api import BaseResource

# global
security = Security()
redis = RedisDB()


class RoleType(BaseEnum):
    values = ['admin', 'teacher', 'student']
    admin, teacher, student = values


def configure_blueprints(app):
    from .user_system.routers import app as user_system_app
    app.register_blueprint(user_system_app)
    from .course.routers import app as course_app
    app.register_blueprint(course_app)


def configure_app(app, config):
    """Loads configuration class into flask app"""
    app.config.from_object(config)


def configure_logger(app):
    # 配置app的logger
    if not app.debug:
        file_handler = logging.handlers.WatchedFileHandler(app.config['LOG_FILENAME'], 'a')
        file_formatter = logging.Formatter(app.config.get(
            'LOG_FILE_FORMAT', '%(asctime)s %(name)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(app.config.get('LOG_FILE_LEVEL', logging.ERROR))
        app.logger.addHandler(file_handler)
    app.logger.info('Logger started')


def configure_database(app):
    """Database configuration should be set here"""
    # uncomment for sqlalchemy support
    from database import db
    db.app = app
    db.init_app(app)
    Migrate(app, db)


def config_security(app):
    from user_system.models import user_datastore
    from user_system.controllers import Account
    state = security.init_app(app, user_datastore)

    def unauthrized():
        if not current_user.is_authenticated:
            BaseResource.not_login()
        else:
            BaseResource.unauthorized()

    state.unauthorized_handler(unauthrized)
    state.login_manager.user_loader(Account.user_loader)
    state.login_manager.unauthorized_handler(BaseResource.not_login)


def config_error_hanler(app):
    def func(e):
        return Response(json.dumps(e.data), e.code, mimetype='application/json')
    app.register_error_handler(httplib.BAD_REQUEST, func)
    app.register_error_handler(httplib.UNAUTHORIZED, func)


def set_allow_origin(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


def set_request_id():
    request.request_id = uuid.uuid1().get_hex()


def create_app(config):
    app = Flask(__name__)
    app.before_request(set_request_id)
    app.after_request(set_allow_origin)
    configure_app(app, config)
    configure_logger(app)
    config_error_hanler(app)
    configure_blueprints(app)
    configure_database(app)
    # config redis queue must before config_before_request
    config_security(app)
    redis.init(app)
    return app
