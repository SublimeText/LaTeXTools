from __future__ import print_function

try:
	from latextools_utils.settings import get_setting
	from latextools_utils.tex_directives import parse_tex_directives
	from latextools_utils import sublime_utils
except ImportError:
	from .settings import get_setting
	from .tex_directives import parse_tex_directives
	from . import sublime_utils
