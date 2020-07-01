import os
import sublime

try:
	from latextools_utils.external_command import get_texpath
	from latextools_utils.system import which
except ImportError:
	from .external_command import get_texpath
	from .system import which

def _get_perl_command():
	texpath = get_texpath() or os.environ['PATH']
	return which('perl', path=texpath)

def perl_installed():
	"""Return whether perl is available in the PATH."""
	return _get_perl_command() is not None

