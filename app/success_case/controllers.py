# -*- coding:utf-8 -*-
from flask.ext.security import roles_accepted
from app import RoleType
from app.utils.api import BaseResource
from app.utils.validate import StringParam
from .models import SuccessCase


class Case(BaseResource):

    def get(self):
        parser = self.get_parser()
        self.add_pagination_args(parser)
        parser.add_argument('tag', type=unicode, required=False, location='args')
        tag, page, page_size = self.get_params('tag', 'page', 'page_size')
        total, items = SuccessCase.get_all(page, page_size, tag)
        datas = []
        for item in items:
            data = {
                'title': item.title,
                'tag': item.tag,
                'background': item.background,
                'strategy': item.strategy,
                'experience': item.experience,
                'create_time': item.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            datas.append(data)
        return {
            'total': total,
            'items': datas,
        }

    @roles_accepted(RoleType.admin)
    def post(self):
        parser = self.get_parser()
        parser.add_argument('title', type=unicode, required=True, location='json')
        parser.add_argument('tag', type=StringParam.check, required=True, location='json', min=1, max=10)
        parser.add_argument('background', type=StringParam.check, required=True, location='json', min=1, max=1000)
        parser.add_argument('strategy', type=StringParam.check, required=True, location='json', min=1, max=1000)
        parser.add_argument('experience', type=StringParam.check, required=True, location='json', min=1, max=1000)
        case = SuccessCase()
        case.title = self.get_param('title')
        case.tag = self.get_param('tag')
        case.background = self.get_param('background')
        case.strategy = self.get_param('strategy')
        case.experience = self.get_param('experience')
        case.save()
        return self.ok('ok')
