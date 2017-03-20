# -*- coding:utf-8 -*-
import hashlib
import os.path
import uuid
from datetime import datetime, date, timedelta
from flask import current_app, request, Response
from flask.ext.security import login_user, logout_user, current_user, login_required, \
    roles_required, roles_accepted
from app import RoleType, errorcode
from app.utils.api import BaseResource
from .models import user_datastore, User, StudentInfo, TeacherInfo, Role, or_
from . import task
from app.utils.validate import EmailParam, PhoneParam, DateParam, StringParam, ListParam, PasswordParm


class Account(BaseResource):

    @classmethod
    def user_loader(cls, user_id):
        return user_datastore.find_user(id=user_id)

    def post(self, action):
        if action == 'login':
            return self.login()
        elif action == 'signup':
            return self.signup()
        elif action == 'photo':
            return self.upload_photo()
        elif action == 'profile':
            return self.set_profile()
        elif action == 'delete':
            return self.delete_user()
        self.bad_request(errorcode.BAD_REQUEST)

    def get(self, action):
        if action == 'is_login':
            return self.is_login()
        elif action == 'logout':
            return self.logout()
        elif action == 'photo':
            return self.get_photo()
        elif action == 'profile':
            return self.get_profile()
        self.bad_request(errorcode.BAD_REQUEST)

    @login_required
    def is_login(self):
        return self.ok('ok')

    def login(self):
        parser = self.get_parser()
        parser.add_argument('identifier', type=str, required=True, location='json')
        parser.add_argument('password', type=StringParam.check, required=True, location='json', min=6, max=20)
        identifier, password = self.get_params('identifier', 'password')
        password = hashlib.md5(password).hexdigest().upper()
        if '@' in identifier:
            user = user_datastore.find_user(email=identifier)
        else:
            user = user_datastore.find_user(phone=identifier)
        if not user or user.password != password:
            self.bad_request(errorcode.INVALID_USER)
        login_user(user, True)
        user.last_login_time = datetime.now()
        user.save()
        return {
            'id': user.id,
            'role': user.roles[0].name,
        }

    def signup(self):
        """student signup"""
        parser = self.get_parser()
        parser.add_argument('email', type=EmailParam.check, required=True, location='json')
        parser.add_argument('phone', type=PhoneParam.check, required=True, location='json')
        parser.add_argument('user_name', type=StringParam.check, required=True, location='json', min=1, max=15)
        parser.add_argument('password', type=StringParam.check, required=True, location='json', min=1, max=15)
        email, phone, user_name, password, = \
            self.get_params('email', 'phone', 'user_name', 'password')
        self._add_student(user_name, email, phone, password)
        return self.ok('ok')

    @roles_accepted(RoleType.admin)
    def delete_user(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        user = user_datastore.find_user(id=self.get_param('user_id'))
        if not user:
            self.bad_request(errorcode.NOT_FOUND)
        user.delete()
        return self.ok('ok')

    @roles_accepted(RoleType.admin)
    def add_teacher(self):
        parser = self.get_parser()
        parser.add_argument('email', type=EmailParam.check, required=True, location='json')
        parser.add_argument('phone', type=PhoneParam.check, required=True, location='json')
        parser.add_argument('user_name', type=StringParam.check, required=True, location='json', min=1, max=15)
        parser.add_argument('password', type=StringParam.check, required=False, location='json',
                            default='12345678', min=1, max=15)
        email, phone, user_name, password, = \
            self.get_params('email', 'phone', 'user_name', 'password')
        self._add_teacher(user_name, email, phone, password)
        return self.ok('ok')

    @login_required
    def logout(self):
        logout_user()
        return self.ok('ok')

    def get_photo(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        user_id = self.get_param('user_id')
        user = current_user
        if user_id != current_user.get_id():
            user = user_datastore.find_user(id=user_id)
            if not user:
                self.bad_request(errorcode.NOT_FOUND)
        path = os.path.join(current_app.config['FILE_STORE_BASE'], user.photo_path)
        try:
            data = open(path, 'rb').read()
            return Response(data, mimetype='image/png')
        except:
            self.bad_request(errorcode.NOT_FOUND)

    @login_required
    def upload_photo(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        try:
            file = request.files['file']
        except:
            self.bad_request(errorcode.BAD_REQUEST)
        user_id = self.get_param('user_id')
        user = current_user
        if user_id != current_user.id:
            if not current_user.has_role(RoleType.admin):
                self.unauthorized(errorcode.UNAUTHORIZED)
            user = user_datastore.find_user(id=user_id)
            if not user:
                self.bad_request(errorcode.NOT_FOUND)
        path = os.path.join('profile_photo',
                            str(user.id) + '-' + uuid.uuid1().get_hex() + '.' + file.filename.rsplit('.', 1)[1])
        full_path = os.path.join(current_app.config['FILE_STORE_BASE'], path)
        try:
            os.makedirs(os.path.dirname(full_path))
        except:
            pass
        file.save(full_path)
        old_path = user.photo_path
        user.photo_path = path
        user.save()
        try:
            if old_path:
                os.remove(os.path.join(current_app.config['FILE_STORE_BASE'], old_path))
        except:
            pass
        return self.ok('ok')

    @login_required
    def set_profile(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        user_id = self.get_param('user_id')
        user = current_user
        if user_id != current_user.id:
            user = user_datastore.find_user(id=user_id)
            if not user:
                self.bad_request(errorcode.NOT_FOUND)
        if user.has_role(RoleType.student):
            return self._set_student_profile(parser, user)
        elif user.has_role(RoleType.teacher):
            pass

    @login_required
    def get_profile(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        user_id = self.get_param('user_id')
        user = current_user
        if user_id != current_user.id:
            user = user_datastore.find_user(id=user_id)
            if not user:
                self.bad_request(errorcode.NOT_FOUND)
        if user.has_role(RoleType.student):
            return self._get_student_profile(user)
        elif user.has_role(RoleType.teacher):
            pass

    @login_required
    def get_users(self):
        parser = self.get_parser()
        self.add_pagination_args(parser)
        parser.add_argument('role', type=str, required=True, location='json',
                            choices=(RoleType.teacher, RoleType.student))
        role_name = self.get_param('role')
        page, page_size = self.get_params('page', 'page_size')
        total, users = user_datastore.get_users(role_name, page, page_size)
        items = []
        if role_name == RoleType.teacher:
            for user in users:
                info = {
                    'real_name': user.name,
                    'school': user.teacher.school,
                    'major': user.teacher.major,
                    'detail': user.teacher.detail,
                }
                items.append(info)
        else:
            pass
        return {
            'total': total,
            'items': items,
        }

    def _add_student(self, user_name, email, phone, password):
        password = hashlib.md5(password).hexdigest().upper()
        user = User(email, phone, password)
        student = StudentInfo()
        student.id = user.id
        student.user_name = user_name
        user.student = student
        user_datastore.add_role_to_user(user, RoleType.student)
        user_datastore.commit()
        return user

    def _add_teacher(self, user_name, email, phone, password):
        password = hashlib.md5(password).hexdigest().upper()
        user = User(email, phone, password)
        teacher = TeacherInfo()
        teacher.id = user.id
        user.teacher = teacher
        user_datastore.add_role_to_user(user, RoleType.teacher)
        user_datastore.commit()

    def _get_student_profile(self, user):
        profile = {
            'id': user.id,
            'email': user.email,
            'phone': user.phone,
            'user_name': user.student.user_name,
            'first_name': user.student.first_name,
            'second_name': user.student.second_name,
            'sexual': user.student.sexual,
            'birthday': '',
            'qq': user.student.qq,
            'skype': user.student.skype,
            'weichat': user.student.weichat,
        }
        if user.student.birthday:
            profile['birthday'] = user.student.birthday.strftime('%Y-%m-%d')
        return profile

    def _set_student_profile(self, parser, user):
        if current_user.id != user.id and not current_user.has_role(RoleType.admin):
            self.unauthorized(errorcode.UNAUTHORIZED)
        parser.add_argument('first_name', type=StringParam.check, required=True, location='json', min=1, max=10)
        parser.add_argument('second_name', type=StringParam.check, required=True, location='json', min=1, max=10)
        parser.add_argument('user_name', type=StringParam.check, required=True, location='json', min=1, max=10)
        parser.add_argument('email', type=EmailParam.check, required=True, location='json')
        parser.add_argument('phone', type=PhoneParam.check, required=True, location='json')
        parser.add_argument('sexual', type=unicode, required=True, location='json', choices=(u'男', u'女'))
        parser.add_argument('birthday', type=DateParam.check, required=False, location='json')
        parser.add_argument('qq', type=str, required=False, location='json', default='')
        parser.add_argument('skype', type=str, required=False, location='json', default='')
        parser.add_argument('weichat', type=str, required=False, location='json', default='')
        user.email = self.get_param('email')
        user.phone = self.get_param('phone')
        user.student.user_name = self.get_param('user_name')
        user.student.first_name = self.get_param('first_name')
        user.student.second_name = self.get_param('second_name')
        user.student.sexual = self.get_param('sexual')
        user.student.birthday = self.get_param('birthday')
        user.student.qq = self.get_param('qq')
        user.student.skype = self.get_param('skype')
        user.student.weichat = self.get_param('weichat')
        user.save()
        return self.ok('ok')








