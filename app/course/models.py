# -*- coding:utf-8 -*-
from datetime import datetime
from sqlalchemy import or_
from flask import current_app
from app.database import db, BaseModel


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
    course_name = db.Column(db.String(20))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_info.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.id'))
    day = db.Column(db.Integer)
    start_time = db.Column(db.String(10))
    stop_time = db.Column(db.String(10))
    time_type = db.Column(db.Integer)
    update_time = db.Column(db.DateTime, default=datetime.now)

    @classmethod
    def get_all(cls, student_id=None, teacher_id=None):
        q = cls.query
        if student_id:
            q = q.filter_by(student_id=student_id)
        else:
            q = q.filter_by(teacher_id=teacher_id)
        return q.order_by(cls.day, cls.time_type).all()

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


class StudyFeedback(BaseModel, db.Model):
    __tablename__ = 'study_feedback'
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.id'))
    chinese_name = db.Column(db.String(20))
    study_date = db.Column(db.Date)
    class_time = db.Column(db.String(30))
    study_time = db.Column(db.String(30))
    course_name = db.Column(db.String(20))
    section = db.Column(db.String(20))
    contents = db.Column(db.String(50))
    homework = db.Column(db.String(75))
    feedback = db.Column(db.String(125))
    update_time = db.Column(db.DateTime, default=datetime.now)
