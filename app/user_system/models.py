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
    email = db.Column(db.VARBINARY(255), unique=True)
    phone = db.Column(db.String(16), unique=True)
    password = db.Column(db.String(48))
    photo_path = db.Column(db.String(255))
    last_login_time = db.Column(db.DateTime, default=datetime.now)
    create_time = db.Column(db.DateTime, default=datetime.now)
    roles = db.relationship('Role', secondary=role_user_relationship,
                            backref=db.backref('users', lazy='dynamic'))
    teacher = db.relationship('TeacherInfo', backref='user', uselist=False,
                              cascade="all, delete-orphan")
    student = db.relationship('StudentInfo', backref='user', uselist=False,
                              cascade="all, delete-orphan")

    def __init__(self, email, phone, password):
        self.email = email
        self.phone = phone
        self.password = password

    @property
    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def to_dict(self):
        return {'id': self.id,
                'email': self.email,
                'phone': self.phone,
                'role': self.roles[0].name,
                'last_login_time': self.last_login_time.strftime('%Y-%m-%d %H:%M:%S'),
                'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S')
                }


class TeacherInfo(BaseModel, db.Model):
    __tablename__ = 'teacher_info'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    graduated = db.Column(db.String(1000))
    introduce = db.Column(db.String(1000))


class StudentInfo(BaseModel, db.Model):
    __tablename__ = 'student_info'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user_name = db.Column(db.String(20), unique=True)
    first_name = db.Column(db.String(10), default='')
    second_name = db.Column(db.String(10), default='')
    sexual = db.Column(db.String(10), default='')
    birthday = db.Column(db.Date)
    qq = db.Column(db.String(20), default='')
    skype = db.Column(db.String(20), default='')
    weichat = db.Column(db.String(20), default='')


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

    def get_users(self, role_name, page, page_size):
        q = User.query.join(role_user_relationship, Role)
        try:
            q = q.filter(Role.name == role_name)
            total = q.count()
            pagination = q.order_by(User.id).paginate(page, page_size)
            return total, pagination.items
        except Exception as e:
            current_app.logger.error(e)
        return 0, []

    def get_users_by_role(self, role, exclude, page, page_size):
        try:
            q = User.query.join(role_user_relationship, Role)
            if role:
                q = q.filter(Role.name==role)
            if exclude:
                q = q.filter(Role.name!=exclude)
            total = q.count()
            pagination = q.order_by('user_id').paginate(page, page_size)
            return total, pagination.items
        except Exception, e:
            current_app.logger.error(e)
        return 0, []

    def get_children(self, parent_id, page, page_size, status=None, exclude=None):
        try:
            q = User.query.filter(or_(User.id==parent_id, User.parent_id==parent_id))
            if status:
                q = q.filter_by(status=status)
            if exclude:
                q = q.filter(User.status!=exclude)
            total = q.count()
            pagination = q.order_by(User.id).paginate(page, page_size)
            return total, pagination.items
        except Exception, e:
            current_app.logger.error(e)
        return 0, []

user_datastore = UserDatastore(db, User, Role)
