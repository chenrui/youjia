# -*- coding:utf-8 -*-
from datetime import datetime
from sqlalchemy import or_
from flask import current_app
from app.database import db, BaseModel


class Course(BaseModel, db.Model):
    __tablename__ = 'course'
    name = db.Column(db.String(20), unique=True)

    tables = db.relationship('CourseTable', backref='course', cascade="all, delete-orphan")


class CourseApply(BaseModel, db.Model):
    __tablename__ = 'course_apply'
    phone = db.Column(db.String(16))
    create_time = db.Column(db.DateTime, default=datetime.now)

    @classmethod
    def get_all(cls, page, page_size):
        try:
            q = cls.query
            total = q.count()
            pagination = q.order_by(cls.create_time.desc()).paginate(page, page_size)
            return total, pagination.items
        except Exception, e:
            current_app.logger.error(e)
        return 0, []


class CourseTable(BaseModel, db.Model):
    __tablename__ = 'course_talbe'
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_info.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.id'))
    day = db.Column(db.Integer)
    start_time = db.Column(db.Integer)
    stop_time = db.Column(db.Integer)

    @classmethod
    def delete_all(cls, ids):
        conn = db.engine.connect()
        try:
            with conn.begin():
                conn.execute('delete from %s where `id` in (%s)' % (
                    CourseTable.__tablename__,
                    ','.join(map(lambda x: str(x), ids))))
        except Exception, e:
            current_app.logger.error(e)
            return False

        return True
