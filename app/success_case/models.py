from datetime import datetime
from flask import current_app
from app.database import db, BaseModel


class SuccessCase(BaseModel, db.Model):
    __tablename__ = 'success_case'
    tag = db.Column(db.String(10))
    chinese_name = db.Column(db.String(20))
    school = db.Column(db.String(100), default='')
    test1 = db.Column(db.String(20))
    score1 = db.Column(db.String(20))
    test2 = db.Column(db.String(20), default='')
    score2 = db.Column(db.String(20), default='')
    test3 = db.Column(db.String(20), default='')
    score3 = db.Column(db.String(20), default='')
    feeling = db.Column(db.String(200))
    comment = db.Column(db.String(400))
    update_time = db.Column(db.DateTime, default=datetime.now)

    @classmethod
    def get_all(cls, page, page_size, tag=None, order_by=None):
        try:
            q = cls.query
            if tag:
                q = q.filter(cls.tag.like('%'+tag+'%'))
            total = q.count()
            if order_by is None:
                order_by = cls.update_time.desc()
            pagination = q.order_by(order_by).paginate(page, page_size)
            return total, pagination.items
        except Exception, e:
            current_app.logger.error(e)
        return 0, []
