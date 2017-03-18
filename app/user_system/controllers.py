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
from .models import user_datastore, User, Role, or_
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
            return self.set_user_info()
        elif action == 'reset_password':
            return self.reset_password()
        elif action == 'verify_password':
            return self.verify_password()
        elif action == 'change_status':
            return self.change_user_status()
        elif action == 'delete_users':
            return self.delete_users()
        self.bad_request(errorcode.BAD_REQUEST)

    def get(self, action):
        if action == 'is_login':
            return self.is_login()
        elif action == 'logout':
            return self.logout()
        elif action == 'photo':
            return self.get_photo()
        elif action == 'profile':
            return self.get_user_info()
        elif action == 'user_list':
            return self.get_user_list()
        elif action == 'tenant_list':
            return self.get_admin_and_tenant()
        elif action == 'search':
            return self.search()
        self.bad_request(errorcode.BAD_REQUEST)

    def put(self, action):
        if action == 'setting':
            return self.set_user_info()
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
        return user.to_dict()

    def signup(self):
        parser = self.get_parser()
        parser.add_argument('email', type=EmailParam.check, required=True, location='json')
        parser.add_argument('phone', type=PhoneParam.check, required=True, location='json')
        parser.add_argument('user_name', type=StringParam.check, required=True, location='json', min=1, max=15)
        parser.add_argument('password', type=StringParam.check, required=True, location='json', min=1, max=15)
        parser.add_argument('role', type=str, required=True, location='json',
                            choices=(RoleType.teacher, RoleType.student))
        self.get_param('user_name')
        email, phone, user_name, password, role = \
            self.get_params('email', 'phone', 'user_name', 'password', 'role')
        password = hashlib.md5(password).hexdigest().upper()
        user = User(user_name, email, phone, password)
        user_datastore.add_role_to_user(user, role)
        user_datastore.commit()
        return self.ok('ok')

    @login_required
    def logout(self):
        logout_user()
        return self.ok('ok')

    @login_required
    def get_photo(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        user_id = self.get_param('user_id')
        user = current_user
        if user_id != current_user.id:
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
        file = request.files['file']
        user_id = self.get_param('user_id')
        user = current_user
        if user_id != current_user.id:
            if current_user.has_role(RoleType.student):
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
    def set_user_info(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        user_id = self.get_param('user_id')
        user = current_user
        if user_id != current_user.id:
            if current_user.has_role(RoleType.student):
                self.unauthorized(errorcode.UNAUTHORIZED)
            user = user_datastore.find_user(id=user_id)
            if not user:
                self.bad_request(errorcode.NOT_FOUND)

    @login_required
    def get_user_info(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        user_id = self.get_param('user_id')
        user = current_user
        if user_id != current_user.id:
            if current_user.has_role(RoleType.student):
                self.unauthorized(errorcode.UNAUTHORIZED)
            user = user_datastore.find_user(id=user_id)
            if not user:
                self.bad_request(errorcode.NOT_FOUND)
        return {
            'email': user.email,
            'user_name': user.name,
            'phone': user.phone,
        }



