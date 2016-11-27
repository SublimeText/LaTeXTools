import sys

if sys.version_info < (3,):
    # reraise implementation from 6
    exec("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")

    strbase = basestring
    unicode = unicode
    long = long

    def get_self(method):
        '''gets reference to the instance for a specific method'''
        try:
            if not method.__class__.__name__ == 'method':
                raise ValueError('method must be a method')
        except AttributeError:
            raise ValueError('method must be a method')

        return method.im_self
else:
    # reraise implementation from 6
    def reraise(tp, value, tb=None):
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    strbase = str
    long = int
    unicode = str

    def get_self(method):
        '''gets reference to the instance for a specific method'''
        try:
            if not method.__class__.__name__ == 'method':
                raise ValueError('method must be a method')
        except AttributeError:
            raise ValueError('method must be a method')

        return method.__self__
