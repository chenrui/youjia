# -*- coding:utf-8 -*-
import hashlib
from datetime import datetime, timedelta
from flask import current_app
from flask.ext.script import Command
from database import create_all, drop_all, db
from app import RoleType
from app.user_system.models import user_datastore, User


class CreateDB(Command):
    """Creates sqlalchemy database"""

    def run(self):
        create_all()


class DropDB(Command):
    """Drops sqlalchemy database"""

    def run(self):
        drop_all()


class InitData(Command):
    """initial data"""

    def run(self):
        self.add_role()
        self.add_admin('系统管理员', 'superadmin', '13800138000', '123456', 1000)

    def add_role(self):
        user_datastore.create_role(name=RoleType.admin, description='管理员')
        user_datastore.create_role(name=RoleType.teacher, description='老师')
        user_datastore.create_role(name=RoleType.student, description='学生')
        user_datastore.commit()

    def add_admin(self, chinese_name, englisth_name, phone, password, uid=None):
        password = hashlib.md5(password).hexdigest().upper()
        user = User(chinese_name, englisth_name, phone, password)
        if uid:
            user.id = uid
        user_datastore.add_role_to_user(user, RoleType.admin)
        user_datastore.commit()
