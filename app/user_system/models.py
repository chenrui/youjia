# -*- coding:utf-8 -*-
from datetime import datetime
from sqlalchemy import or_
from flask import current_app
from flask.ext.security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
from app.database import db, BaseModel
from app import RoleType, errorcode
from app.utils.api import BaseResource


role_user_relationship = db.Table('role_user_relationship',
                                  db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                                  db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(BaseModel, db.Model, RoleMixin):
    __tablename__ = 'role'
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(80), unique=True)

    def __init__(self, name, description):
        self.name = name
        self.description = description


class User(BaseModel, db.Model, UserMixin):
    __tablename__ = 'user'
    phone = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(48))
    chinese_name = db.Column(db.String(20))
    english_name = db.Column(db.String(20))
    photo_path = db.Column(db.String(255))
    update_time = db.Column(db.DateTime, default=datetime.now)
    create_time = db.Column(db.DateTime, default=datetime.now)
    verify_token = db.Column(db.String(32), default='')
    status = db.Column(db.String(10))
    roles = db.relationship('Role', secondary=role_user_relationship,
                            backref=db.backref('users', lazy='dynamic'))
    teacher = db.relationship('TeacherInfo', backref='user', uselist=False,
                              cascade="all, delete-orphan")
    student = db.relationship('StudentInfo', backref='user', uselist=False,
                              cascade="all, delete-orphan")

    def __init__(self, chinese_name='', englisth_name='', phone='', password=''):
        self.chinese_name = chinese_name
        self.english_name = englisth_name
        self.phone = phone
        self.password = password
        self.photo_path = ''
        self.status = 'enabled'

    @property
    def is_active(self):
        return True

    def get_id(self):
        return self.id


class TeacherInfo(BaseModel, db.Model):
    __tablename__ = 'teacher_info'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    # 毕业学校
    graduated = db.Column(db.String(20))
    # 专业
    major = db.Column(db.String(20))
    country = db.Column(db.String(10))
    weichat = db.Column(db.String(20), default='')
    introduce = db.Column(db.String(200))
    success_case = db.Column(db.String(200))
    feature = db.Column(db.String(500))
    show = db.Column(db.Boolean)

    course_tables = db.relationship('CourseTable', backref='teacher_info', cascade="all, delete-orphan")


class StudentInfo(BaseModel, db.Model):
    __tablename__ = 'student_info'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    sexual = db.Column(db.String(10), default='')
    location = db.Column(db.String(10))
    age = db.Column(db.String(5), default='')
    school = db.Column(db.String(20))
    grade = db.Column(db.String(20))
    study_country = db.Column(db.String(10))
    enrollment_time = db.Column(db.String(10), default='')
    major = db.Column(db.String(20))
    course_name = db.Column(db.String(20))
    learn_range = db.Column(db.String(40))
    weichat = db.Column(db.String(20), default='')
    parent_phone = db.Column(db.String(16))
    remark = db.Column(db.String(100), default='')

    # file
    test1 = db.Column(db.String(20), default='')
    score1 = db.Column(db.String(10), default='')
    test2 = db.Column(db.String(20), default='')
    score2 = db.Column(db.String(10), default='')
    test3 = db.Column(db.String(20), default='')
    score3 = db.Column(db.String(10), default='')
    test4 = db.Column(db.String(20), default='')
    score4 = db.Column(db.String(10), default='')
    test5 = db.Column(db.String(20), default='')
    score5 = db.Column(db.String(10), default='')
    admission_school = db.Column(db.String(20), default='')
    admission_major = db.Column(db.String(20), default='')

    course_tables = db.relationship('CourseTable', backref='student_info', cascade="all, delete-orphan")
    feedbacks = db.relationship('StudyFeedback', backref='student_info', cascade="all, delete-orphan")


class UserDatastore(SQLAlchemyUserDatastore):
    def commit(self, **kwargs):
        try:
            self.db.session.commit()
        except Exception, e:
            current_app.logger.error(e)
            db.session.rollback()
            if 'Duplicate' in e.message:
                BaseResource.server_error(errorcode.DUPLICATE, **kwargs)
            BaseResource.server_error(errorcode.DATABASE_ERROR, **kwargs)

    def get_users(self, role_name, page, page_size, status=None, key=None, only_show_teacher=False,
                  order_by=None):
        q = User.query.join(role_user_relationship, Role)
        try:
            q = q.filter(Role.name == role_name)
            if status:
                q = q.filter(User.status == status)
            if key:
                q = q.filter(or_(User.phone.like('%'+key+'%'),
                                 User.chinese_name.like('%'+key+'%'),
                                 User.english_name.like('%'+key+'%')))
            if only_show_teacher and role_name == RoleType.teacher:
                q = q.join(TeacherInfo).filter(TeacherInfo.show == only_show_teacher)
            total = q.count()
            if not order_by:
                order_by = User.update_time.desc()
            pagination = q.order_by(order_by).paginate(page, page_size)
            return total, pagination.items
        except Exception as e:
            current_app.logger.error(e)
        return 0, []


user_datastore = UserDatastore(db, User, Role)
