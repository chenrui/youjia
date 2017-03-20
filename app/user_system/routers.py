# -*- coding:utf-8 -*-
from app.utils.api import RestfulApi
from . import app
from .controllers import Account
from flask_restful.utils import OrderedDict
from flask_restful.representations.json import output_json


RESOURCES = (
    [Account, '/api/account/<string:action>'],
)

api = RestfulApi(app, default_mediatype='application/json; charset=UTF-8')
api.representations = OrderedDict([('application/json; charset=UTF-8',
                                    output_json)])
api.add_resources(RESOURCES)