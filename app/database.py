# -*- coding:utf-8 -*-
from flask import current_app
from flask.ext.sqlalchemy import Pagination, orm, SQLAlchemy
import flask.ext.sqlalchemy as sqlalchemy
from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool
from . import errorcode
from app.utils.api import BaseResource


def custom_paginate(cls, page, per_page=20, error_out=False):
    """Returns `per_page` items from page `page`.  By default it will
    abort with 404 if no items were found and the page was larger than
    1.  This behavor can be disabled by setting `error_out` to `False`.

    Returns an :class:`Pagination` object.
    """
    # per_page = 0 表示返回全部
    per_page = per_page and int(per_page) or 0
    if per_page == 0:
        items = cls.all()
    else:
        items = cls.limit(per_page).offset((page - 1) * per_page).all()

    # No need to count if we're on the first page and there are fewer
    # items than we expected.
    if page == 1 and len(items) < per_page:
        total = len(items)
    else:
        total = cls.order_by(None).count()
        if per_page == 0:
            per_page = total

    return Pagination(cls, page, per_page, total, items)

# --- SQLALCHEMY SUPPORT

db = SQLAlchemy()

sqlalchemy.BaseQuery.paginate = custom_paginate
# add support for custom query
orm.query.Query.paginate = custom_paginate


def drop_all():
    db.drop_all()


def create_all():
    db.create_all()


def remove_session():
    db.session.remove()

# --- SQLALCHEMY SUPPORT END


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()


class BaseModel(object):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    @classmethod
    def _commit(cls, **kwargs):
        try:
            db.session.commit()
        except Exception, e:
            current_app.logger.error(e)
            db.session.rollback()
            if 'Duplicate' in e.message:
                ecode = errorcode.DUPLICATE
                BaseResource.server_error(ecode)
            else:
                ecode = errorcode.DATABASE_ERROR
            BaseResource.server_error(ecode, **kwargs)

    @classmethod
    def get(cls, **kwargs):
        try:
            return cls.query.filter_by(**kwargs).first()
        except Exception, e:
            current_app.logger.error(e)
        return None

    @classmethod
    def delete_by_id(cls, id, **kwargs):
        cls.query.filter_by(id=id).delete()
        cls._commit(**kwargs)

    def save(self, **kwargs):
        db.session.add(self)
        self._commit(**kwargs)

    def delete(self, **kwargs):
        db.session.delete(self)
        self._commit(**kwargs)
