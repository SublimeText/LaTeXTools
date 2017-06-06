import os
import sys

from .six import reraise


def make_dirs(path):
    '''
    wraps os.makedirs to surpress any error as long as the directory exists
    '''
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            reraise(*sys.exc_info())

from shutil import which
