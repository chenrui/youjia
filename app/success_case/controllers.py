# -*- coding:utf-8 -*-
from datetime import datetime
from flask.ext.security import roles_accepted
from app import RoleType, errorcode
from app.utils.api import BaseResource
from app.utils.validate import StringParam
from .models import SuccessCase


class Case(BaseResource):

    def get(self, action=None):
        if action is None:
            return self.get_list()
        elif action == 'detail':
            return self.get_detail()

    @roles_accepted(RoleType.admin)
    def post(self, action=None):
        parser = self.get_parser()
        case = SuccessCase()
        return self.set_case(parser, case)

    @roles_accepted(RoleType.admin)
    def put(self, action=None):
        parser = self.get_parser()
        parser.add_argument('case_id', type=int, required=True, location='args')
        case_id = self.get_param('case_id')
        case = SuccessCase.get(id=case_id)
        if not case:
            self.bad_request(errorcode.NOT_FOUND)
        return self.set_case(parser, case)

    @roles_accepted(RoleType.admin)
    def delete(self, action=None):
        parser = self.get_parser()
        parser.add_argument('case_id', type=int, required=True, location='args')
        case_id = self.get_param('case_id')
        case = SuccessCase.get(id=case_id)
        if case:
            case.delete()
        return self.ok('ok')

    def set_case(self, parser, case):
        parser.add_argument('chinese_name', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('tag', type=StringParam.check, required=True, location='json', min=1, max=10)
        parser.add_argument('school', type=StringParam.check, required=False, location='json', min=1, max=100)
        parser.add_argument('test1', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('score1', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('test2', type=StringParam.check, required=False, location='json', min=1, max=20)
        parser.add_argument('score2', type=StringParam.check, required=False, location='json', min=1, max=20)
        parser.add_argument('test3', type=StringParam.check, required=False, location='json', min=1, max=20)
        parser.add_argument('score3', type=StringParam.check, required=False, location='json', min=1, max=20)
        parser.add_argument('feeling', type=StringParam.check, required=True, location='json', min=1, max=200)
        parser.add_argument('comment', type=StringParam.check, required=True, location='json', min=1, max=200)
        case.chinese_name = self.get_param('chinese_name')
        case.tag = self.get_param('tag')
        case.school = self.get_param('school')
        case.test1 = self.get_param('test1')
        case.score1 = self.get_param('score1')
        case.test2 = self.get_param('test2')
        case.score2 = self.get_param('score2')
        case.test3 = self.get_param('test3')
        case.score3 = self.get_param('score3')
        case.feeling = self.get_param('feeling')
        case.comment = self.get_param('comment')
        case.update_time = datetime.now()
        case.save()
        return self.ok('ok')

    @roles_accepted(RoleType.admin)
    def get_list(self):
        parser = self.get_parser()
        self.add_pagination_args(parser)
        page, page_size = self.get_params('page', 'page_size')
        total, items = SuccessCase.get_all(page, page_size)
        datas = []
        for item in items:
            data = {
                'id': item.id,
                'chinese_name': item.chinese_name,
                'school': item.school,
                'tag': item.tag,
                'update_time': item.update_time.strftime('%Y-%m-%d'),
            }
            datas.append(data)
        return {
            'total': total,
            'items': datas,
        }

    def get_detail(self):
        parser = self.get_parser()
        self.add_pagination_args(parser)
        parser.add_argument('tag', type=unicode, required=False, location='args')
        parser.add_argument('case_id', type=int, required=False, location='args')
        tag, page, page_size = self.get_params('tag', 'page', 'page_size')
        case_id = self.get_param('case_id')
        if case_id:
            case = SuccessCase.get(id=case_id)
            if not case:
                self.bad_request(errorcode.NOT_FOUND)
            total = 1
            items = [case]
        else:
            total, items = SuccessCase.get_all(page, page_size, tag)
        datas = []
        for item in items:
            data = {
                'id': item.id,
                'chinese_name': item.chinese_name,
                'school': item.school,
                'tag': item.tag,
                'test1': item.test1,
                'test2': item.test2,
                'test3': item.test3,
                'score1': item.score1,
                'score2': item.score2,
                'score3': item.score3,
                'feeling': item.feeling,
                'comment': item.comment,
                'update_time': item.update_time.strftime('%Y-%m-%d'),
            }
            datas.append(data)
        return {
            'total': total,
            'items': datas,
        }

