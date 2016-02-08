from __future__ import print_function

try:
	from latextools_utils.settings import get_setting
	from latextools_utils import sublime
except ImportError:
	from .settings import get_setting
	from . import sublime
