from datetime import datetime
from flask import current_app
from app.database import db, BaseModel


class SuccessCase(BaseModel, db.Model):
    __tablename__ = 'success_case'
    title = db.Column(db.String(255))
    tag = db.Column(db.String(10))
    background = db.Column(db.String(1000))
    strategy = db.Column(db.String(1000))
    experience = db.Column(db.String(1000))
    create_time = db.Column(db.DateTime, default=datetime.now)

    @classmethod
    def get_all(cls, page, page_size, tag=None):
        try:
            q = cls.query
            if tag:
                q.filter_by(tag=tag)
            total = q.count()
            pagination = q.order_by(cls.create_time.desc()).paginate(page, page_size)
            return total, pagination.items
        except Exception, e:
            current_app.logger.error(e)
        return 0, []
