import sublime

__all__ = ['getRegion']

if sublime.version() < '3000':
    def getRegion(a, b):
        return sublime.Region(long(a), long(b))
else:
    def getRegion(a, b):
        return sublime.Region(a, b)
