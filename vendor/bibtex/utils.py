from collections import OrderedDict


class CaseInsensitiveOrderedDict(OrderedDict):
    def __getitem__(self, key):
        return super(CaseInsensitiveOrderedDict, self).__getitem__(key.lower())

    def __setitem__(self, key, value):
        super(CaseInsensitiveOrderedDict, self).__setitem__(key.lower(), value)

    def setdefault(self, key, default=None):
        super(CaseInsensitiveOrderedDict, self).setdefault(key.lower(), default)

    __marker = object()

    def pop(self, key, default=__marker):
        key = key.lower()
        if default is self.__marker:
            return super(CaseInsensitiveOrderedDict, self).pop(key)
        else:
            return super(CaseInsensitiveOrderedDict, self).pop(key, default)
