def _getattr(obj, name, default=None):
    return getattr(obj, name.upper(), default)


class BaseEnum(object):

    """ Base Enum class.

    fields -- the list of field/attribute
    values -- the list of value
    """
    fields = None
    values = None

    def __getitem__(self, key):
        return _getattr(self, key)

    def get(self, item, default=None):
        return _getattr(self, item, default)
