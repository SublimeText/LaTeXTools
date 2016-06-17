import os
import sublime
import sys


__dir__ = os.path.dirname(__file__)
# this should work since it only happens on ST2
if __dir__ == '.':
    dir = sublime.packages_path()

sys.path.insert(0, os.path.join(
    __dir__, 'external')
)
