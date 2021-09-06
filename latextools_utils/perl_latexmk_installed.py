import os
from shutil import which
from .external_command import get_texpath


def perl_latexmk_installed():
    """Return whether perl and latexmk is available in the PATH."""
    texpath = get_texpath() or os.environ['PATH']
    return which('perl', path=texpath) and which('latexmk', path=texpath)
