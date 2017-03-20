# -*- coding:utf-8 -*-
from datetime import datetime
from sqlalchemy import or_
from flask import current_app
from app.database import db, BaseModel
from app import RoleType, errorcode
from app.utils.api import BaseResource


class Course(BaseModel, db.Model):
    __tablename__ = 'course'
    name = db.Column(db.String(20), unique=True)

    applies = db.relationship('CourseApply', backref='course', cascade="all, delete-orphan")


class CourseApply(BaseModel, db.Model):
    __tablename__ = 'course_apply'
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
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
