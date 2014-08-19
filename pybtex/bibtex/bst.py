# Copyright (c) 2007, 2008, 2009, 2010, 2011, 2012  Andrey Golovizin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import re
from pybtex.bibtex.interpreter import (Integer, String, QuotedVar,
        Identifier, FunctionLiteral, BibTeXError)
import pybtex.io

#ParserElement.enablePackrat()

def process_int_literal(value):
    return Integer(int(value.strip('#')))

def process_string_literal(value):
    assert value.startswith('"')
    assert value.endswith('"')
    return String(value[1:-1])

def process_identifier(name):
    if name[0] == "'":
        return QuotedVar(name[1:])
    else:
        return Identifier(name)

def process_function(toks):
    return FunctionLiteral(toks[0])


quote_or_comment = re.compile(r'[%"]')
def strip_comment(line):
    """Strip the commented part of the line."

    >>> print(strip_comment('a normal line'))
    a normal line
    >>> print(strip_comment('%'))
    <BLANKLINE>
    >>> print(strip_comment('%comment'))
    <BLANKLINE>
    >>> print(strip_comment('trailing%'))
    trailing
    >>> print(strip_comment('a normal line% and a comment'))
    a normal line
    >>> print(strip_comment('"100% compatibility" is a myth'))
    "100% compatibility" is a myth
    >>> print(strip_comment('"100% compatibility" is a myth% or not?'))
    "100% compatibility" is a myth

    """
    pos = 0
    end = len(line) - 1
    in_string = False
    while pos <= end:
        match = quote_or_comment.search(line, pos)
        if not match:
            break
        if match.group() == '%' and not in_string:
            return line[:match.start()]
        elif match.group() == '"':
            in_string = not in_string
        pos = match.end()
    return line


from pybtex.scanner import (
    Scanner, Pattern, Literal,
    TokenRequired, PybtexSyntaxError,
)


class BstParser(Scanner):
    LBRACE = Literal('{')
    RBRACE = Literal('}')
    STRING = Pattern(r'"[^\"]*"', 'string')
    INTEGER = Pattern(r'#-?\d+', 'integer')
    NAME = Pattern(r'[^#\"\{\}\s]+', 'name')

    COMMANDS = {
        'ENTRY': 3,
        'EXECUTE': 1,
        'FUNCTION': 2,
        'INTEGERS': 1,
        'ITERATE': 1,
        'MACRO': 2,
        'READ': 0,
        'REVERSE': 1,
        'SORT': 0,
        'STRINGS': 1,
    }

    LITERAL_TYPES = {
        STRING: process_string_literal,
        INTEGER: process_int_literal,
        NAME: process_identifier,
    }

    def parse(self):
        while True:
            try:
                yield list(self.parse_command())
            except EOFError:
                break
            except PybtexSyntaxError as e:
                raise
                break

    def parse_group(self):
        while True:
            token = self.required([self.LBRACE, self.RBRACE, self.STRING, self.INTEGER, self.NAME])
            if token.pattern is self.LBRACE:
                yield FunctionLiteral(list(self.parse_group()))
            elif token.pattern is self.RBRACE:
                break
            else:
                yield self.LITERAL_TYPES[token.pattern](token.value)

    def parse_command(self):
        command_name = self.required([self.NAME], 'BST command', allow_eof=True).value
        try:
            arity = self.COMMANDS[command_name.upper()]
        except KeyError:
            raise TokenRequired('BST command', self)
        yield command_name
        for i in range(arity):
            brace = self.optional([self.LBRACE])
            if not brace:
                break
            yield list(self.parse_group())


def parse_file(filename, encoding=None):
    bst_file = pybtex.io.open_unicode(filename, encoding=encoding)
    return parse_stream(bst_file, filename)


def parse_stream(stream, filename='<INPUT>'):
    bst = '\n'.join(strip_comment(line.rstrip()) for line in stream)
    return list(BstParser(bst, filename=filename).parse())


if __name__ == '__main__':
    import sys
    from pprint import pprint
    pprint(parse_file(sys.argv[1]))

