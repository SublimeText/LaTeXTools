# mini-grammar to remove LaTeX commands from the string, replacing them with the text inside the brackets.
import pyparsing
from pyparsing import ZeroOrMore, Literal, Suppress, Forward, Optional, CharsNotIn, ParserElement, White
import sublime

__all__ = ['remove_latex_commands']

latex_command   = Forward()
brackets        = Forward()
content         = CharsNotIn(u'{}' + ParserElement.DEFAULT_WHITE_CHARS) + Optional(White(), '')
content.leaveWhitespace()
brackets        <<= Suppress(u'{') + ZeroOrMore(latex_command | brackets | content) + Suppress(u'}')
latex_command   <<= (Suppress(Literal(u'\\')) + Suppress(CharsNotIn(u'{')) + brackets) | brackets

if sublime.version() < '3000':
        exec("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")
else:
    def reraise(tp, value, tb=None):
        if value is None:
            value = tp()
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value


def remove_latex_commands(s):
    result = latex_command.scanString(s)
    if result:
        try:
            for r in result:
                tokens, preloc, nextloc = r
                s = s[:preloc] \
                    + u''.join(tokens) \
                    + s[nextloc:]
        except TypeError:
            # Note: for some reason this grammar will occassionally produce a TypeError on the first
            # run-through only and only on ST2; this error is not reproducible in a simulated environment
            # running Python 2.6.8, so I've resorted to this ugly hack which, in the case of the type error on
            # ST2 will re-process the string; for whatever reason, the error doesn't appear in the second 
            # and subsequent invocations of this grammar.
            import sys

            # save the current exception state
            exc_info = sys.exc_info()

            if sublime.version() < '3000':
                # check that the caller is not this function to avoid an infinite recursion
                import inspect
                frame = inspect.currentframe()
                try:
                    if frame.f_back.f_code.co_name != 'remove_latex_commands':
                        remove_latex_commands(s)
                    else:
                        reraise(*exec_info)
                finally:
                    del frame
            else:
                reraise(*exec_info)
    return s
