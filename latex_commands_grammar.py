# mini-grammar to remove LaTeX commands from the string, replacing them with the text inside the brackets.
import pyparsing
from pyparsing import ZeroOrMore, Literal, Suppress, Forward, Optional, CharsNotIn, ParserElement, White

__all__ = ['remove_latex_commands']

latex_command   = Forward()
brackets        = Forward()
content         = CharsNotIn(u'{}' + ParserElement.DEFAULT_WHITE_CHARS) + Optional(White(), '')
content.leaveWhitespace()
brackets        <<= Suppress(u'{') + ZeroOrMore(latex_command | brackets | content) + Suppress(u'}')
latex_command   <<= (Suppress(Literal(u'\\')) + Suppress(CharsNotIn(u'{')) + brackets) | brackets

def remove_latex_commands(s):
    result = latex_command.scanString(s)
    if result:
        for r in result:
            tokens, preloc, nextloc = r
            s = s[:preloc] \
                + u''.join(tokens) \
                + s[nextloc:]
    return s
