import sublime

__all__ = ['get_Region']

if sublime.version() < '3000':
    def get_Region(a, b):
        return sublime.Region(long(a), long(b))
else:
    def get_Region(a, b):
        return sublime.Region(a, b)
