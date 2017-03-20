import sys
import re
from datetime import datetime
import validators

ParamError = lambda n, msg: ValueError("Parameter %r %s" % (n, msg))


class ParamValidation(object):
    name = None
    names = []
    type = None
    type_str = None

    @classmethod
    def check(cls, value, name, args):
        param = cls()
        param.name = name
        if type(args) != dict:
            raise TypeError
        return param.validate(value, args)

    def validate_value(self, value, args):
        pass

    def type_err(self):
        return self.error('is not %s' % self.type_str)

    def get_err_msg(self):
        return 'not be %s' % self.value

    def error(self, msg):
        return ParamError(self.name, msg)

    def value_err(self):
        return self.error('should ' + self.get_err_msg())

    def validate(self, value, args):
        try:
            value = self.type(value) if value is not None else None
        except:
            raise self.type_err()

        if not self.validate_value(value, args):
            self.value = value
            raise self.value_err()
        return value


class EmailParam(ParamValidation):
    type = str
    type_str = 'string'

    def validate_value(self, value, args):
        m = re.match(r'^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$', value)
        return m is not None

    def get_err_msg(self):
        return 'not an email format'


class PhoneParam(ParamValidation):
    type = str
    type_str = 'string'

    def validate_value(self, value, args):
        return re.match(r'^[0-9]{11}$', value) is not None

    def get_err_msg(self):
        return 'not an phone number format'


class StringParam(ParamValidation):
    type = unicode
    type_str = 'string'

    def validate_value(self, value, args):
        return validators.length(unicode(value), args.get('min', 0), args.get('max', sys.maxunicode))

    def get_err_msg(self):
        return 'length error'


class PasswordParm(ParamValidation):
    type = str
    type_str = 'string'

    def validate_value(self, value, args):
        ret = validators.length(unicode(value), args.get('min', 0), args.get('max', sys.maxunicode))
        if not ret:
            return ret
        ret = re.search(r'[a-z]', value) is not None
        if not ret:
            return ret
        ret = re.search(r'[A-Z]', value) is not None
        if not ret:
            return ret
        return re.search(r'[0-9]', value) is not None

    def get_err_msg(self):
        return 'invalid password'


class DateParam(ParamValidation):
    type = str
    type_str = 'string'

    def validate_value(self, value, args):
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except:
            return False

    def get_err_msg(self):
        return 'not a date like 2016-01-01 format'


class IntParam(ParamValidation):
    type = int
    type_str = 'integer'

    def validate_value(self, value, args):
        return args.get('min', 0) <= value <= args.get('max', sys.maxint)

    def get_err_msg(self):
        return 'length error'


class ListParam(ParamValidation):
    type = list
    type_str = 'list'

    def validate_value(self, value, args):
        return len(value) == len(list(set(value)))

    def get_err_msg(self):
        return 'length error'
