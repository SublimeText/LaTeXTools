# ST2/ST3 compat
from __future__ import print_function

try:
	from latextools_utils.tex_directives import get_tex_root
except ImportError:
	from .latextools_utils.tex_directives import get_tex_root
