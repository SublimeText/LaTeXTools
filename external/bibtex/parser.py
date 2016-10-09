'''
parser for the bibtex lexer

expected tokens:
    PREAMBLE        - @preamble marker
    STRING          - @string marker
    ENTRY_START     - @ marker when starting an entry
    ENTRY_TYPE      - the entry type
    IDENTIFIER      - a non-quoted non-numeric value
    NUMBER          - a numeric-only value
    KEY             - the key in a "key = value" pair
    VALUE           - a value occurring between brackets
    QUOTED_STRING   - a value occurring in quote marks
    ENTRY_END       - the } at the end of an entry
    #               - concatenation operator
    EOF             - EOF marker

grammar (roughly):
    database = entries EOF;
    entries = (preamble | string | entry)*;
    preamble = PREAMBLE field_value ENTRY_END;
    string = STRING KEY (VALUE | QUOTED_STRING) ENTRY_END;
    entry = ENTRY_START ENTRY_TYPE IDENTIFIER key_values ENTRY_END;
    key_values = (KEY field_value)*;
    field_value = concatenated_values* | value;
    concatenated_values = value # field_value;
    value = IDENTIFIER | NUMBER | VALUE | QUOTED_STRING;
'''

from .ast import *
from .lexer import Lexer
from .model import *
from .names import Name
from .tex import tokenize_list

import sys

if sys.version_info > (3, 0):
    unicode = str

__all__ = ['Parser']


class Parser(object):

    def __init__(self, lexer=Lexer()):
        super(Parser, self).__init__()
        self.lexer = lexer
        self.tokens = []
        self.database = None

        self._current_token = -1
        self._tokens_len = -1
        self._mark_locations = []

    def parse(self, s):
        self.tokens = self.lexer.tokenize(s)
        self._current_token = 0
        self._tokens_len = len(self.tokens)
        self._mark_locations = []

        if self._tokens_len < 0:
            raise SyntaxError('could not find any entries')

        self.database = database = Database()

        while True:
            try:
                self._advance()
            except IndexError:
                self.unexpected_token('preamble, string, entry_start, or eof')

            token_type = self.token_type
            if token_type == 'PREAMBLE':
                preamble = self.preamble()
                database.add_preamble(
                    self._handle_value(preamble.contents)
                )
            elif token_type == 'STRING':
                string = self.string()
                database.add_macro(
                    string.key,
                    self._handle_value(string.value)
                )
            elif token_type == 'ENTRY_START':
                entry_node = self.entry()

                entry = Entry(
                    entry_node.entry_type,
                    entry_node.key.value
                )

                for field in entry_node.fields:
                    entry[field.key] = self._handle_value(field.value)
                    if field.key in Name.NAME_FIELDS:
                        entry[field.key] = ' and '.join(
                            (unicode(Name(s)) for s in
                                tokenize_list(entry[field.key])))

                database.add_entry(entry)
            elif token_type == 'EOF':
                return database
            else:
                self.unexpected_token('preamble, string, entry_start, or eof')

    def _advance(self):
        token_len = self._tokens_len

        current_token = self._current_token
        if current_token >= token_len:
            raise IndexError('no more tokens')

        self.token_type, self.token_value, self.line_info = self.tokens[current_token]
        self._current_token += 1

    def _mark(self):
        self._mark_locations.append(self._current_token)

    def _unmark(self):
        self._mark_locations.pop()

    def _rewind(self):
        try:
            last_mark = self._mark_locations.pop()
            self._current_token = last_mark
        except IndexError:
            if self._current_token <= 0:
                raise Exception('attempted to rewind before the beginning')

            self._current_token -= 1

        try:
            self.token_type, self.token_value, self.line_info = self.tokens[self._current_token]
        except IndexError:
            pass

    def preamble(self):
        node = PreambleNode()

        # contents are optional
        try:
            node.contents = self.field_value()
        except SyntaxError:
            self._rewind()

        try:
            self._advance()
        except IndexError:
            self.unexpected_token('entry_end')

        if self.token_type != 'ENTRY_END':
            self.unexpected_token('entry_end')

        return node

    def string(self):
        node = StringNode()

        try:
            self._advance()
        except IndexError:
            self.unexpected_token('key')

        if self.token_type != 'KEY':
            self.unexpected_token('key')

        node.key = self.token_value
        node.value = self.field_value()

        try:
            self._advance()
        except IndexError:
            self.unexpected_token('entry_end')

        if self.token_type != 'ENTRY_END':
            self.unexpected_token('entry_end')

        return node

    def entry(self):
        try:
            self._advance()
        except IndexError:
            self.unexpected_token('entry_type')

        if self.token_type != 'ENTRY_TYPE':
            self.unexpected_token('entry_type')

        node = EntryNode()
        node.entry_type = self.token_value
        node.key = self.entry_key()
        node.fields = self.key_values()

        try:
            self._advance()
        except IndexError:
            self.unexpected_token('entry_end')

        if self.token_type != 'ENTRY_END':
            self.unexpected_token('entry_end')

        return node

    def entry_key(self):
        try:
            self._advance()
        except IndexError:
            self.unexpected_token('identifier')

        if self.token_type in ('IDENTIFIER', 'NUMBER'):
            node = EntryKeyNode()
            node.value = self.token_value
            return node
        else:
            self.unexpected_token('identifier')

    def key_values(self):
        values = []

        while True:
            try:
                self._advance()
            except IndexError:
                break

            if self.token_type == 'KEY':
                node = KeyValueNode()
                node.key = self.token_value
                node.value = self.field_value()

                values.append(node)
            else:
                self._rewind()
                break

        return values

    def field_value(self):
        return self.concatenated_value() or self.value()

    def concatenated_value(self):
        self._mark()
        try:
            lhs = self.value()
        except SyntaxError:
            self._rewind()
            return False

        try:
            self._advance()
        except IndexError:
            self._rewind()
            return False

        if self.token_type != '#':
            self._rewind()
            return False

        try:
            rhs = self.field_value()
        except SyntaxError:
            self._rewind()
            return False

        self._unmark()

        node = ConcatenationNode()
        node.lhs = lhs
        node.rhs = rhs

        return node

    def value(self):
        try:
            self._advance()
        except IndexError:
            self.unexpected_token('quoted_string, value, identifier, or number')

        token_type = self.token_type
        if token_type == 'QUOTED_STRING':
            node = QuotedLiteralNode()
        elif token_type == 'VALUE':
            node = QuotedLiteralNode()
        elif token_type == 'IDENTIFIER':
            node = LiteralNode()
        elif token_type == 'NUMBER':
            node = NumberNode()
        else:
            self.unexpected_token('quoted_string, value, identifier, or number')

        node.value = self.token_value
        return node

    def unexpected_token(self, expecting=None):
        try:
            line    = self.line_info['first_line']
            column  = self.line_info['first_column']
        except (AttributeError, KeyError):
            line, column = -1, -1

        if expecting is not None:
            expecting = '; expecting {0}'.format(expecting)
        else:
            expecting = ''

        try:
            token_type = self.token_type.lower()
        except (AttributeError, NameError):
            token_type = 'eof'

        if line > 0 and column > 0:
            raise SyntaxError('{0}:{1} - unexpected {2}{3}'.format(
                line + 1,
                column + 1,
                token_type,
                expecting
            ))
        else:
            raise SyntaxError('unexpected {0}{1}'.format(
                token_type,
                expecting
            ))

    def _handle_value(self, value):
        if isinstance(value, ConcatenationNode):
            return ''.join((
                self._handle_value(value.lhs),
                self._handle_value(value.rhs)
            ))
        elif isinstance(value, LiteralNode):
            macro_code = value.value
            try:
                return self.database.get_macro(macro_code)
            except KeyError:
                return macro_code
        else:
            return value.value
