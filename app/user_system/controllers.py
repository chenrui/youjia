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
from .models import user_datastore, User, StudentInfo, TeacherInfo
from . import task
from app.utils.validate import EmailParam, PhoneParam, DateParam, StringParam, ListParam


class Account(BaseResource):

    @classmethod
    def user_loader(cls, user_id):
        return user_datastore.find_user(id=user_id)

    def post(self, action=None):
        if action == 'login':
            return self.login()
        elif action == 'verify':
            return self.verify()
        elif action == 'reset_password':
            return self.reset_password()
        elif action == 'photo':
            return self.upload_photo()
        elif action == 'add_teacher':
            return self.add_teacher()
        elif action == 'add_student':
            return self.add_student()
        self.bad_request(errorcode.BAD_REQUEST)

    def get(self, action=None):
        if action == 'is_login':
            return self.is_login()
        elif action == 'logout':
            return self.logout()
        elif action == 'photo':
            return self.get_photo()
        elif action == 'students':
            return self.get_users(RoleType.student, 'enabled')
        elif action == 'teachers':
            return self.get_users(RoleType.teacher, 'enabled')
        elif action == 'profile':
            return self.get_profile()
        self.bad_request(errorcode.BAD_REQUEST)

    def put(self, action=None):
        if action == 'profile':
            return self.set_profile()
        self.bad_request(errorcode.BAD_REQUEST)

    def delete(self, action=None):
        return self.delete_user()

    @login_required
    def is_login(self):
        return self.ok('ok')

    def login(self):
        parser = self.get_parser()
        parser.add_argument('phone', type=str, required=True, location='json')
        parser.add_argument('password', type=StringParam.check, required=True, location='json', min=6, max=20)
        phone, password = self.get_params('phone', 'password')
        password = hashlib.md5(password).hexdigest().upper()
        user = user_datastore.find_user(phone=phone)
        if not user or user.password != password:
            self.bad_request(errorcode.INVALID_USER)
        login_user(user, True)
        user.last_login_time = datetime.now()
        user.save()
        return {
            'id': user.id,
            'role': user.roles[0].name,
        }

    def verify(self):
        parser = self.get_parser()
        parser.add_argument('phone', type=str, required=True, location='json')
        parser.add_argument('parent_phone', type=str, required=True, location='json')
        parser.add_argument('study_country', type=unicode, required=True, location='json')
        user = User.get(phone=self.get_param('phone'))
        if not user:
            self.bad_request(errorcode.INVALID_USER)
        if not user.has_role(RoleType.student):
            self.bad_request(errorcode.INVALID_USER)
        if user.student.study_country != self.get_param('study_country') or \
                        user.student.parent_phone != self.get_param('parent_phone'):
            self.bad_request(errorcode.INVALID_USER)
        user.verify_token = uuid.uuid1().get_hex()
        user.save()
        return {'token': user.verify_token}

    def reset_password(self):
        parser = self.get_parser()
        parser.add_argument('password', type=StringParam.check, required=True, location='json', min=6, max=20)
        if not current_user.get_id():
            parser.add_argument('token', type=str, required=True, location='json', min=6, max=20)
            token, pwd = self.get_params('token', 'password')
            user = User.get(verify_token=token)
            if not user:
                self.bad_request(errorcode.BAD_REQUEST)
            user.password = hashlib.md5(pwd).hexdigest().upper()
            user.verify_token = ''
        else:
            user = current_user
            pwd = self.get_param('password')
            user.password = hashlib.md5(pwd).hexdigest().upper()
        user.save()
        return self.ok('ok')

    @roles_accepted(RoleType.admin)
    def delete_user(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        user = user_datastore.find_user(id=self.get_param('user_id'))
        if user:
            user.delete()
            try:
                if user.photo_path:
                    os.remove(os.path.join(current_app.config['FILE_STORE_BASE'], user.photo_path))
            except:
                pass
        return self.ok('ok')

    @roles_accepted(RoleType.admin)
    def add_teacher(self):
        parser = self.get_parser()
        user = User()
        teacher = TeacherInfo()
        teacher.id = user.id
        user.teacher = teacher
        user_datastore.add_role_to_user(user, RoleType.teacher)
        return self._set_teacher_profile(parser, user)

    @roles_accepted(RoleType.admin)
    def add_student(self):
        parser = self.get_parser()
        user = User()
        student = StudentInfo()
        student.id = user.id
        user.student = student
        user_datastore.add_role_to_user(user, RoleType.student)
        return self._set_student_profile(parser, user)

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
        user.update_time = datetime.now()
        if user.has_role(RoleType.student):
            return self._set_student_profile(parser, user)
        elif user.has_role(RoleType.teacher):
            return self._set_teacher_profile(parser, user)

    @login_required
    def get_profile(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        user_id = self.get_param('user_id')
        user = current_user
        if user_id != current_user.id:
            if not current_user.has_role(RoleType.admin):
                self.unauthorized(errorcode.UNAUTHORIZED)
            user = user_datastore.find_user(id=user_id)
            if not user:
                self.bad_request(errorcode.NOT_FOUND)
        if user.has_role(RoleType.student):
            return self._get_student_profile(user)
        elif user.has_role(RoleType.teacher):
            return self._get_teacher_profile(user)
        return self.bad_request(errorcode.BAD_REQUEST)

    @login_required
    def get_users(self, role_name, status):
        parser = self.get_parser()
        self.add_pagination_args(parser)
        parser.add_argument('key', type=StringParam.check, required=False, location='args', min=1, max=20)
        page, page_size = self.get_params('page', 'page_size')
        total, users = user_datastore.get_users(role_name, page, page_size, status, self.get_param('key'))
        items = []
        if role_name == RoleType.teacher:
            for user in users:
                info = {
                    'id': user.id,
                    'chinese_name': user.chinese_name,
                    'english_name': user.english_name,
                    'graduated': user.teacher.graduated,
                    'major': user.teacher.major,
                    'country': user.teacher.country,
                    'phone': user.phone,
                    'update_time': user.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                items.append(info)
        else:
            if not current_user.has_role(RoleType.admin):
                self.unauthorized(errorcode.UNAUTHORIZED)
            for user in users:
                info = {
                    'id': user.id,
                    'chinese_name': user.chinese_name,
                    'sexual': user.student.sexual,
                    'age': user.student.age,
                    'school': user.student.school,
                    'location': user.student.location,
                    'course_name': user.student.course_name,
                    'phone': user.phone,
                    'update_time': user.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                items.append(info)
        return {
            'total': total,
            'items': items,
        }

    def _get_student_profile(self, user):
        return {
            'id': user.id,
            'phone': user.phone,
            'chinese_name': user.chinese_name,
            'english_name': user.english_name,
            'sexual': user.student.sexual,
            'location': user.student.location,
            'age': user.student.age,
            'school': user.student.school,
            'grade': user.student.grade,
            'study_country': user.student.study_country,
            'enrollment_time': user.student.enrollment_time,
            'major': user.student.major,
            'course_name': user.student.course_name,
            'learn_range': user.student.learn_range,
            'wechat': user.student.weichat,
            'parent_phone': user.student.parent_phone,
            'remark': user.student.remark,
        }

    def _get_teacher_profile(self, user):
        return {
            'id': user.id,
            'phone': user.phone,
            'chinese_name': user.chinese_name,
            'english_name': user.english_name,
            'graduated': user.teacher.graduated,
            'major': user.teacher.major,
            'country': user.teacher.country,
            'wechat': user.teacher.weichat,
            'introduce': user.teacher.introduce,
            'success_case': user.teacher.success_case,
            'feature': user.teacher.feature,
        }

    def _set_student_profile(self, parser, user):
        parser.add_argument('chinese_name', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('english_name', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('sexual', type=unicode, required=False, location='json', choices=(u'男', u'女'))
        parser.add_argument('location', type=StringParam.check, required=True, location='json', min=1, max=10)
        parser.add_argument('age', type=str, required=False, location='json')
        parser.add_argument('school', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('grade', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('study_country', type=StringParam.check, required=True, location='json', min=1, max=10)
        parser.add_argument('enrollment_time', type=DateParam.check, required=False, location='json')
        parser.add_argument('major', type=StringParam.check, required=False, location='json', min=1, max=20)
        parser.add_argument('course_name', type=StringParam.check, required=True, location='json')
        parser.add_argument('learn_range', type=StringParam.check, required=True, location='json', min=1, max=40)
        parser.add_argument('wechat', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('phone', type=PhoneParam.check, required=True, location='json')
        parser.add_argument('parent_phone', type=PhoneParam.check, required=True, location='json')
        parser.add_argument('remark', type=StringParam.check, required=False, location='json', min=1, max=100)

        user.phone = self.get_param('phone')
        user.chinese_name = self.get_param('chinese_name')
        user.english_name = self.get_param('english_name')
        user.student.sexual = self.get_param('sexual', '')
        user.student.location = self.get_param('location')
        user.student.age = self.get_param('age', '')
        user.student.school = self.get_param('school')
        user.student.grade = self.get_param('grade')
        user.student.study_country = self.get_param('study_country')
        user.student.enrollment_time = self.get_param('enrollment_time', '')
        user.student.major = self.get_param('major', '')
        user.student.course_name = self.get_param('course_name')
        user.student.learn_range = self.get_param('learn_range')
        user.student.weichat = self.get_param('wechat')
        user.student.parent_phone = self.get_param('parent_phone')
        user.student.remark = self.get_param('remark', '')
        if user.password == '':
            user.password = hashlib.md5(user.english_name + '2017').hexdigest().upper()
        user.save()
        return self.ok('ok')

    def _set_teacher_profile(self, parser, user):
        parser.add_argument('chinese_name', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('english_name', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('graduated', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('major', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('country', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('phone', type=PhoneParam.check, required=True, location='json')
        parser.add_argument('wechat', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('introduce', type=StringParam.check, required=True, location='json', min=1, max=200)
        parser.add_argument('success_case', type=StringParam.check, required=True, location='json', min=1, max=200)
        parser.add_argument('feature', type=StringParam.check, required=True, location='json', min=1, max=500)

        user.phone = self.get_param('phone')
        user.chinese_name = self.get_param('chinese_name')
        user.english_name = self.get_param('english_name')
        user.teacher.graduated = self.get_param('graduated')
        user.teacher.major = self.get_param('major')
        user.teacher.country = self.get_param('country')
        user.teacher.weichat = self.get_param('wechat')
        user.teacher.introduce = self.get_param('introduce')
        user.teacher.success_case = self.get_param('success_case')
        user.teacher.feature = self.get_param('feature')
        if user.password == '':
            user.password = hashlib.md5(user.english_name + '2017').hexdigest().upper()
        user.save()
        return self.ok('ok')


class File(Account):
    def post(self, action=None):
        return self.file_student()

    def get(self, action=None):
        if action is None:
            return self.get_users(RoleType.student, 'filed')
        elif action == 'profile':
            return self.get_profile()
        self.bad_request(errorcode.BAD_REQUEST)

    @roles_accepted(RoleType.admin)
    def get_profile(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        user = User.get(id=self.get_param('user_id'), status='filed')
        if not user or not user.has_role(RoleType.student):
            self.bad_request(errorcode.BAD_REQUEST)
        data = self._get_student_profile(user)
        del data['remark']
        data['test1'] = user.student.test1
        data['test2'] = user.student.test2
        data['test3'] = user.student.test3
        data['test4'] = user.student.test4
        data['test5'] = user.student.test5
        data['score1'] = user.student.score1
        data['score2'] = user.student.score2
        data['score3'] = user.student.score3
        data['score4'] = user.student.score4
        data['score5'] = user.student.score5
        data['admission_school'] = user.student.admission_school
        data['admission_major'] = user.student.admission_major
        return data

    @roles_accepted(RoleType.admin)
    def file_student(self):
        parser = self.get_parser()
        parser.add_argument('user_id', type=int, required=True, location='args')
        parser.add_argument('test1', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('test2', type=StringParam.check, required=False, location='json', min=1, max=20)
        parser.add_argument('test3', type=StringParam.check, required=False, location='json', min=1, max=20)
        parser.add_argument('test4', type=StringParam.check, required=False, location='json', min=1, max=20)
        parser.add_argument('test5', type=StringParam.check, required=False, location='json', min=1, max=20)
        parser.add_argument('score1', type=str, required=True, location='json')
        parser.add_argument('score2', type=str, required=False, location='json')
        parser.add_argument('score3', type=str, required=False, location='json')
        parser.add_argument('score4', type=str, required=False, location='json')
        parser.add_argument('score5', type=str, required=False, location='json')
        parser.add_argument('admission_school', type=StringParam.check, required=True, location='json', min=1, max=20)
        parser.add_argument('admission_major', type=StringParam.check, required=False, location='json', min=1, max=20)
        user_id = self.get_param('user_id')
        user = User.get(id=user_id)
        if not user.has_role(RoleType.student):
            self.bad_request(errorcode.BAD_REQUEST)
        user.status = 'filed'
        user.update_time = datetime.now()
        user.student.test1 = self.get_param('test1')
        user.student.test2 = self.get_param('test2', '')
        user.student.test3 = self.get_param('test3', '')
        user.student.test4 = self.get_param('test4', '')
        user.student.test5 = self.get_param('test5', '')
        user.student.score1 = self.get_param('score1')
        user.student.score2 = self.get_param('score2', '')
        user.student.score3 = self.get_param('score3', '')
        user.student.score4 = self.get_param('score4', '')
        user.student.score5 = self.get_param('score5', '')
        user.student.admission_school = self.get_param('admission_school')
        user.student.admission_major = self.get_param('admission_major', '')
        user.save()
        return self.ok('ok')

