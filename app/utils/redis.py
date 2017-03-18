import json
from datetime import datetime
from flask_redis import FlaskRedis


class RedisDB(object):
    """Simple Queue with Redis Backend"""

    default_namespace = None

    def __init__(self, app=None, name=None, namespace=None, sub_namespace=None):
        'key format -> namespace:sub_namescape:name'
        self.name = name
        self.namespace = namespace or self.default_namespace
        self.sub_namespace = sub_namespace
        if app is not None:
            self.init(app)

    def init(self, app):
        self.app = app
        self.app.config.setdefault('REDIS_QUEUE_NAMESPACE', self.namespace)
        self.app.config.setdefault('REDIS_QUEUE_NAME', self.name)
        self.db = FlaskRedis(app)
        self.namespace = self.namespace or self.app.config.get(
            'REDIS_QUEUE_NAMESPACE')
        self.name = self.name or self.app.config.get('REDIS_QUEUE_NAME')

    def qsize(self, name=None, sub_namespace=None):
        """Return the approximate size of the queue."""
        return self.db.llen(self.abs_key(name, sub_namespace))

    def empty(self, name):
        """Return True if the queue is empty, False otherwise."""
        return self.qsize(name) == 0

    def put(self, item, name, sub_namespace=None):
        """Put item into the queue."""
        item = self.jsonfiy_value(item)
        self.db.lpush(self.abs_key(name, sub_namespace), item)

    def get(self, name=None, block=True, timeout=None):
        """Remove and return an item from the queue.

        If optional args block is true and timeout is None (the default), block
        if necessary until an item is available."""
        key = '%s:%s' % (self.namespace, name or self.name)
        if block:
            item = self.db.blpop(key, timeout=timeout)
        else:
            item = self.db.lpop(key)

        if item:
            item = item[1]
        return item

    def get_nowait(self, name):
        """Equivalent to get(False)."""
        return self.get(name, False)

    def get_list(self, name, start=0, end=-1):
        key = '%s:%s' % (self.namespace, name or self.name)
        return self.db.lrange(key, start, end)

    def db(self):
        return self.db

    def delete_queue(self, *names):
        if names:
            keys = ["%s:%s" % (self.namespace, name) for name in names]
            self.db.delete(*keys)
        else:
            key = self.abs_key(self.name)
            self.db.delete(key)

    def log(self, value):
        self.db.lpush('log', '%s: %s' % (str(datetime.now())[:19], value))

    def setex(self, name, value, sub_namespace=None, time=300):
        value = self.jsonfiy_value(value)
        self.db.setex(self.abs_key(name, sub_namespace), value, time)

    def hset(self, field, value, name, sub_namespace=None):
        value = self.jsonfiy_value(value)
        self.db.hset(self.abs_key(name, sub_namespace), field, value)

    def hlen(self, name, sub_namespace=None):
        return self.db.hlen(self.abs_key(name, sub_namespace))

    def hkeys(self, name, sub_namespace=None):
        return self.db.hkeys(self.abs_key(name, sub_namespace))

    def hget(self, name, field, sub_namespace=None):
        value = self.db.hget(self.abs_key(name, sub_namespace), field)
        return json.loads(value) if value else None

    def abs_key(self, name, sub_namespace=None):
        name = name or self.name
        sub_namespace = sub_namespace or self.sub_namespace
        return "%s:%s" % (self.namespace, "%s:%s" % (sub_namespace, name) if sub_namespace else name)

    def jsonfiy_value(self, value):
        if isinstance(value, dict):
            value = json.dumps(value)
        return value

    def expire(self, name, seconds=300, sub_namespace=None):
        self.db.expire(self.abs_key(name, sub_namespace), seconds)

    def set(self, name, value, sub_namespace=None):
        value = self.jsonfiy_value(value)
        self.db.set(self.abs_key(name, sub_namespace), value)

    def rpush(self, item, name=None, sub_namespace=None):
        item = self.jsonfiy_value(item)
        self.db.rpush(self.abs_key(name, sub_namespace), item)

    def exists(self, name=None, sub_namespace=None):
        return self.db.exists(self.abs_key(name, sub_namespace))

    def lrange(self, start, stop, name=None, sub_namespace=None):
        return self.db.lrange(self.abs_key(name, sub_namespace), start, stop)

    def sadd(self, name=None, sub_namespace=None, *value):
        return self.db.sadd(self.abs_key(name, sub_namespace), value)

    def zincrby(self, member, increment=1, name=None, sub_namespace=None):
        return self.db.zincrby(self.abs_key(name, sub_namespace), member, increment)

    def zrange(self, name, start=0, stop=-1):
        return self.db.zrange(self.abs_key(name), start, stop)

    def zscore(self, name, member):
        return self.db.zscore(self.abs_key(name), member)

    def incr(self, name=None, sub_namespace=None):
        return self.db.incr(self.abs_key(name, sub_namespace))

    def delete(self, name=None, sub_namespace=None):
        return self.db.delete(self.abs_key(name, sub_namespace))
