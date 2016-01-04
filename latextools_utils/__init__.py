from __future__ import print_function

try:
	from latextools_utils.settings import get_setting
except ImportError:
	from .settings import get_setting

try:
	from latextools_utils.tex_directives import parse_tex_directives
except ImportError:
	from .tex_directives import parse_tex_directives
