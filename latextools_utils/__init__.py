from __future__ import print_function


def is_bib_buffer(view, point=0):
    return view.match_selector(point, 'text.bibtex') or is_biblatex_buffer(view, point)


def is_biblatex_buffer(view, point=0):
    return view.match_selector(point, 'text.biblatex')

try:
    from latextools_utils.settings import get_setting
    from latextools_utils.tex_directives import parse_tex_directives
    from latextools_utils import analysis
    from latextools_utils import cache
    from latextools_utils import sublime_utils
    from latextools_utils import utils
except ImportError:
    from .settings import get_setting
    from .tex_directives import parse_tex_directives
    from . import analysis
    from . import cache
    from . import sublime_utils
    from . import utils
