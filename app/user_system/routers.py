# -*- coding:utf-8 -*-
from app.utils.api import RestfulApi
from . import app
from .controllers import Account, History, export_user_info, export_all, StaticPng
from flask_restful.utils import OrderedDict
from flask_restful.representations.json import output_json


RESOURCES = (
    [Account, '/api/account', '/api/account/<string:action>'],
    [History, '/api/history'],
    [StaticPng, '/static/<int:user_id>/<string:file>'],
)

api = RestfulApi(app, default_mediatype='application/json; charset=UTF-8')
api.representations = OrderedDict([('application/json; charset=UTF-8',
                                    output_json)])
api.add_resources(RESOURCES)

app.add_url_rule('/export/user/info',
                 export_all.__name__, export_all, methods=['GET'])
