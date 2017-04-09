# -*- coding:utf-8 -*-
from cStringIO import StringIO
from datetime import timedelta, datetime
from re import compile
from app.utils.ipip import IPX

IPV4_PATTERN = compile(r'^((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))$')


def str_to_bool(s):
    '''Convert string to bool'''
    if 'true' == s.lower():
        return True
    elif 'false' == s.lower():
        return False
    else:
        raise ValueError('%s: not bool string' % s)


def str_to_bool_if_possible(s):
    ''''''
    if 'true' == s.lower():
        return True
    elif 'false' == s.lower():
        return False
    else:
        s


def str_to_int_if_possible(s):
    try:
        return int(s)
    except Exception:
        return s


def is_num(s):
    '''Check whether is number'''
    try:
        int(s)
        return True
    except ValueError:
        pass

    return False


def read_all(f):
    out = StringIO()
    while True:
        buffer_ = f.read(1024)
        if buffer_ and len(buffer_) > 0:
            out.write(buffer_)
        else:
            break

    return out.getvalue()


def zero_if_none(v):
    if v is None:
        return 0
    else:
        v


def system_config_int(v):
    try:
        if v is None:
            return 0
        else:
            return int(v)
    except ValueError:
        return 0


def redis_int(v):
    try:
        if v is None:
            return 0
        else:
            return int(v)
    except ValueError:
        return 0


def datetime_range(start, end=None, step='1h'):
    ret = []
    if end is None:
        end = datetime.now()
    if step.endswith('h'):
        values = step.split('h', 2)
        while True:
            ret.append(start)
            start += timedelta(seconds=int(values[0])*60*60)
            if start >= end:
                break
    elif step.endswith('d'):
        values = step.split('d', 2)
        while True:
            ret.append(start)
            start += timedelta(days=int(values[0]))
            if start > end:
                break
    else:
        raise ValueError('bad value for step[%s]' % step)

    return ret


def last_24h(now=None):
    if now is None:
        now = datetime.now()
    tmp = now - timedelta(seconds=23*60*60)
    start = datetime(tmp.year, tmp.month, tmp.day, tmp.hour)
    return datetime_range(start, step='1h')


def last_7d(now=None):
    if now is None:
        now = datetime.now()
    tmp = now - timedelta(days=6)
    start = datetime(tmp.year, tmp.month, tmp.day)
    return datetime_range(start, step='1d')


def last_30d(now=None):
    if now is None:
        now = datetime.now()
    tmp = now - timedelta(days=29)
    start = datetime(tmp.year, tmp.month, tmp.day)
    return datetime_range(start, step='1d')


def is_ip_v4(s):
    if IPV4_PATTERN.match(s):
        return True
    else:
        return False


def ip_location(ip):
    try:
        ret = IPX.find(ip)
    except:
        return 'unknown'
    if ret == 'N/A':
        return 'unknown'
    ret = ret.split('\t')
    length = len(ret)
    if length != 13:
        return 'unknown'
    elif ret[0] != ret[1] and ret[0] == u'中国':
        if len(ret[2]):
            return ret[2]
        else:
            return ret[1]
    else:
        return ret[0]



def ip_latitude_longitude(ip):
    try:
        ret = IPX.find(ip)
    except:
        return ['unknown', 'unknown']
    ret = ret.split('\t')
    length = len(ret)
    if length != 13:
        return ['unknown', 'unknown']
    try:
        return [float(ret[6]), float(ret[5])]
    except:
        return [104.0755463, 31.6585285]


def ip_country(ip):
    try:
        ret = IPX.find(ip)
    except:
        return 'unknown'
    ret = ret.split('\t')
    if ret[0] == '局域网':
        return 'CN'
    length = len(ret)
    if length != 13:
        return 'unknown'
    if ret[-2] == '*':
        return 'unknown'
    return ret[-2]


def page_total(total, page_size):
    pg_total = total / page_size
    if total % page_size != 0:
        pg_total += 1
    return pg_total

