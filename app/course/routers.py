# -*- coding:utf-8 -*-
from app.utils.api import RestfulApi
from . import app
from .controllers import CourseResource, CourseTB, Feedback, export_course_table, export_studt_feedback
from flask_restful.utils import OrderedDict
from flask_restful.representations.json import output_json


RESOURCES = (
    [CourseResource, '/api/course', '/api/course/<string:action>'],
    [CourseTB, '/api/coursetable', '/api/coursetable/<string:action>'],
    [Feedback, '/api/feedback'],
)

api = RestfulApi(app, default_mediatype='application/json; charset=UTF-8')
api.representations = OrderedDict([('application/json; charset=UTF-8',
                                    output_json)])
api.add_resources(RESOURCES)

app.add_url_rule('/export/user/coursetable',
                 export_course_table.__name__, export_course_table, methods=['GET'])
app.add_url_rule('/export/user/feedback',
                 export_studt_feedback.__name__, export_studt_feedback, methods=['GET'])
