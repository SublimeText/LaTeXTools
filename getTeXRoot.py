import glob
import os
import re

MAIN_PATTERN = re.compile(r'\\begin{document}')


def is_main(tex_file):
    with open(tex_file) as fobj:
        for line in fobj:
            if MAIN_PATTERN.search(line):
                return True


def get_tex_root(tex_file):
    if is_main(tex_file):
        return tex_file

    path, _ = os.path.split(tex_file)
    path = os.path.abspath(path)
    while True:
        for fname in glob.iglob(os.path.join(path, '*.tex')):
            if fname == tex_file:
                continue
            if is_main(fname):
                return fname

        parent_path = os.path.abspath(os.path.join(path, '..'))
        if path == parent_path:
            raise ValueError('Main tex file not found.')
        path = parent_path
