# -*- coding:utf-8 -*-
import hashlib
from datetime import datetime, timedelta
from flask import current_app
from flask.ext.script import Command
from database import create_all, drop_all, db
from app import RoleType
from app.user_system.models import user_datastore, User, TeacherInfo


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
        # self.add_role()
        self.add_admin()

    def add_role(self):
        user_datastore.create_role(name=RoleType.admin, description='管理员')
        user_datastore.create_role(name=RoleType.teacher, description='老师')
        user_datastore.create_role(name=RoleType.student, description='学生')
        user_datastore.commit()

    def add_admin(self):
        teacher = TeacherInfo()
        user = User()
        user.teacher = teacher
        user.chinese_name = '杨世新'
        user.english_name = 'Alex'
        user.phone = '15882408557'
        user.password = hashlib.md5('Alex2017').hexdigest().upper()
        user.id = 1000
        user.teacher.id = user.id
        user.teacher.graduated = '四川大学/纽约州立/南京大学-JHU'
        user.teacher.major = '国际关系'
        user.teacher.country = '中国'
        user.teacher.weichat = 'Alex-Yangshixin'
        user.teacher.introduce = '''优加教育总经理兼首席培训师，以第一名的成绩被南京大学-约翰霍普金斯大学中美研究中心录取，哈佛大学国际与亚洲关系论坛杰出代表，教育部全额奖学金留学纽约州立大学。托福117，阅读30，听力30；SAT成绩2320，阅读790，写作730。'''
        user.teacher.success_case = '山西学生王某（学习SAT),语法词汇知识扎实，之前在北京参加过一段时间训练，但是分数始终不理想。经过和学生的沟通，发现学生问题在于“逻辑同一律”的认知完全缺乏。因此，制定的学习计划围绕“认识逻辑同一律和它在SAT题目中的运用”展开。经过10个小时的训练，学生在大量的练习中掌握了“同一律”。12月的SAT考试中一举拿下了1530（英文730）的优异成绩。'
        user.teacher.feature = '09年开始从事教育培训行业，截止2017年1月，累积上课小时3756，约等于公立学校5634节英文课。知识渊博，上课大量采用逻辑规律讲授知识。对SAT、GRE逻辑同一律有较深的研究，也是为数不多的能教LSAT的老师，擅长带高水平优生出成绩。仅2016年，SAT学生的最低成绩为1450，其中大部分成绩在1500左右；2015年，SAT阅读满分2人。'
        user.teacher.show = True
        user_datastore.add_role_to_user(user, RoleType.admin)
        user_datastore.add_role_to_user(user, RoleType.teacher)
        user_datastore.commit()
