# -*- coding:utf-8 -*-
import logging
from datetime import timedelta


class Config(object):
    PROJECT_NAME = 'worker'
    USE_X_SENDFILE = False
    CSRF_ENABLED = False
    SECRET_KEY = "92aad4950fcc9144b1e2fe6be6eb3541e36940a6278c13a7"

    # sqlalchemy
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_POOL_RECYCLE = 7200
    SQLALCHEMY_POOL_TIMEOUT = 100

    # LOGGING
    LOG_FILENAME = "/var/log/worker/website_err.log"
    LOG_FILE_LEVEL = logging.WARNING
    LOG_FILE_FORMAT = "%(asctime)s %(name)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"

    INTERNAL_IPS = ['127.0.0.1']

    # session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    # cookie
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # redis
    REDIS_URL = "redis://10.4.5.223:6379/0"

    # output JSON with utf-8
    RESTFUL_JSON = {'ensure_ascii': False, 'encoding': 'utf-8'}

    FILE_STORE_BASE = 'app/static'

    @staticmethod
    def init_app(app):
        pass


class ProductConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    TESTING = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    LOGIN_DISABLED = False

    # DATABASE CONFIGURATION
    DB_USER = 'root'
    DB_PASSWD = '123456'
    DB_HOST = '10.4.5.199'
    DB_PORT = 3306
    DB_NAME = 'yunfang'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
        DB_USER, DB_PASSWD, DB_HOST, DB_PORT, DB_NAME)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    TESTING = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    LOGIN_DISABLED = False

    # DATABASE CONFIGURATION
    DB_NAME = 'worker'
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PASSWD = '123456'
    DB_HOST = '10.4.5.220'
    DB_USER = 'admin'
    # DB_PASSWD = 'swad@APT123'
    DB_HOST = '192.168.25.131'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' % (
        DB_USER, DB_PASSWD, DB_HOST, DB_PORT, DB_NAME)


config = {
    'product': ProductConfig,
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}


