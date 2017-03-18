# -*- coding: utf-8 -*-
from flask import request, _request_ctx_stack, current_app
from flask.ext.security import current_user
from werkzeug.exceptions import HTTPException
from app import create_app, redis
import thread
import json


def delay(func):
    def wraper(*args, **kwargs):
        kwargs['user_id'] = current_user.get_id()
        kwargs['request_ctx'] = _request_ctx_stack.top
        kwargs['app_config'] = current_app.config
        thread.start_new_thread(func, args, kwargs)
    return wraper


def context_loader(func):
    class Meta(object):
        pass

    def load_config(config):
        meta = Meta()
        for k, v in config.items():
            setattr(meta, k, v)
        return meta

    def wraper(*args, **kwargs):
        conf = load_config(kwargs.pop('app_config').copy())
        app = create_app(conf)
        reqctx = kwargs.pop('request_ctx')
        reqctx.push()
        task_id = 'task:' + getattr(request, 'request_id')
        user_id = kwargs.pop('user_id', None)
        if user_id:
            from app.user_system.models import User
            user = User.get(id=user_id)
        else:
            from flask_login import AnonymousUserMixin
            user = AnonymousUserMixin()
        setattr(_request_ctx_stack.top, 'user', user)
        with app.app_context():
            info = {'status_code': 200,
                    'message': '开始执行任务'}
            redis.db.set(task_id, json.dumps(info))
            try:
                func(*args, **kwargs)
                info['message'] = '任务执行成功'
            except HTTPException, e:
                app.logger.error(e)
                info = e.data
            except Exception:
                info['status_code'] = 500
                info['message'] = '任务执行失败'
            redis.db.set(task_id, json.dumps(info))
            redis.db.expire(task_id, 60*60*12)
    return wraper
