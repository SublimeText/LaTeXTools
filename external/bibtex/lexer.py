'''
lexer for bibtex files

produces tokens in the form:
    (TOKEN_TAG, TOKEN_VALUE, {LOCATION_INFORMATION})

produced tokens:
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

location information:
    four co-ordinates for each token consisting of the first_line, first_column, last_line, and last_column
    all 0-based

note that the EOF token does not have associated location_information
'''

import re

__all__ = ['Lexer']


class Lexer(object):

    def __init__(self):
        super(Lexer, self).__init__()
        self.tokens = []
        self.code = ''
        self.code_len = 0
        self.current_line = 0
        self.current_column = 0
        self.current_index = 0
        self.in_entry = False

    def tokenize(self, code):
        self.code = code
        code_len = self.code_len = len(code)

        # reset values
        self.tokens = []
        self.current_line = 0
        self.current_column = 0
        self.current_index = 0
        self.in_entry = False

        while self.current_index < code_len:
            if not self.in_entry:
                consumed = self.until_entry()
                self.in_entry = True
                start_entry = True
            else:
                if start_entry:
                    consumed = (
                        self.preamble_token()       or
                        self.string_token()         or
                        self.comment_token()        or
                        self.entry_start_token()    or
                        self.token_error()
                    )

                    start_entry = False
                elif self.tokens[-1][0] == 'ENTRY_START':
                    consumed = (
                        self.entry_type_token()     or
                        self.token_error()
                    )
                else:
                    consumed = (
                        self.whitespace_token()     or
                        self.comma_token()          or
                        self.key_token()            or
                        self.identifier_token()     or
                        self.number_token()         or
                        self.value_token()          or
                        self.quoted_string_token()  or
                        self.hash_token()           or
                        self.entry_end_token()      or
                        self.token_error()
                    )

            self.current_line, self.current_column = \
                self.get_line_and_column(consumed)

            self.current_index += consumed

        self.tokens.append(('EOF', '', {}))

        return self.tokens

    def until_entry(self):
        match = ENTRY_START.search(self.code, self.current_index)
        if match:
            # don't consume the @
            return match.start() - self.current_index

        return self.code_len - self.current_index

    def preamble_token(self):
        match = PREAMBLE.match(self.code, self.current_index)
        if not match:
            return 0
        self.add_token('PREAMBLE', match.group(1))

        return len(match.group(0))

    def string_token(self):
        match = STRING.match(self.code, self.current_index)
        if not match:
            return 0
        self.add_token('STRING', match.group(1))

        return len(match.group(0))

    def comment_token(self):
        match = COMMENT.match(self.code, self.current_index)
        if not match:
            return 0

        # we consume the whole line
        self.in_entry = False

        return len(match.group(0))

    def entry_start_token(self):
        match = ENTRY_START.match(self.code, self.current_index)
        if not match:
            return 0
        self.add_token('ENTRY_START', match.group(0))

        return len(match.group(0))

    def entry_type_token(self):
        match = ENTRY_TYPE.match(self.code, self.current_index)
        if not match:
            return 0
        self.add_token('ENTRY_TYPE', match.group(1))

        return len(match.group(0))

    def identifier_token(self):
        match = IDENTIFIER.match(self.code, self.current_index)
        if not match:
            return 0
        self.add_token('IDENTIFIER', match.group(0))

        return len(match.group(0))

    def number_token(self):
        match = NUMBER.match(self.code, self.current_index)
        if not match:
            return 0
        self.add_token('NUMBER', match.group(0))

        return len(match.group(0))

    def key_token(self):
        match = KEY.match(self.code, self.current_index)
        if not match:
            return 0
        self.add_token('KEY', match.group(1))

        return len(match.group(0))

    def match_brackets(self, i):
        value = []

        code_len = self.code_len
        bracket_depth = 1

        while i < code_len:
            match = NEXT_BRACKET_BREAK.search(self.code, i)
            if match:
                value.append(self.code[i:match.start()])
                i = match.end()

                matched = match.group(0)

                if matched == '}':
                    bracket_depth -= 1
                    if bracket_depth == 0:
                        break
                    value.append(matched)
                elif matched == '{':
                    bracket_depth += 1
                    value.append(matched)
                else:
                    self.current_line += 1
                    # consume space after new line replacing with 1 space
                    match = SPACE.match(self.code, i - 1)
                    if match:
                        i = match.end()
                        if self.code[i] != '}':
                            value.append(' ')
            else:
                i = code_len

        if bracket_depth != 0:
            return (i, None)

        return (i, ''.join(value))

    def value_token(self):
        i = self.current_index
        if self.code[i] != '{':
            return 0

        i, value = self.match_brackets(i + 1)
        if value is None:
            return 0

        self.add_token('VALUE', ''.join(value).strip())
        return i - self.current_index

    def quoted_string_token(self):
        i = initial_index =  self.current_index
        if self.code[i] != '"':
            return 0

        value = []

        i += 1
        code_len = self.code_len

        while i < code_len:
            match = NEXT_QUOTE_BREAK.search(self.code, i)
            if match:
                value.append(self.code[i:match.start()])
                i = match.end()

                matched = match.group(0)

                if matched == '"':
                    break
                elif matched == '{':
                    new_i, bracket_value = self.match_brackets(i)
                    if bracket_value is None:
                        value.append('{')
                    else:
                        value.extend(['{', bracket_value, '}'])
                        i = new_i
                else:
                    self.current_line += 1
                    # consume space after new line replacing with 1 space
                    match = SPACE.match(self.code, i - 1)
                    if match:
                        i = match.end()
                        if self.code[i] != '"':
                            value.append(' ')
            else:
                i = code_len

        # if we don't end with a quote
        if i > code_len or self.code[i - 1] != '"':
            return 0

        self.add_token('QUOTED_STRING', ''.join(value))
        return i - initial_index

    def entry_end_token(self):
        if self.code[self.current_index] != '}':
            return 0
        self.add_token('ENTRY_END', '}')

        self.in_entry = False

        return 1

    def comma_token(self):
        if self.code[self.current_index] != ',':
            return 0

        return 1

    def hash_token(self):
        if self.code[self.current_index] != '#':
            return 0
        self.add_token('#', '#')

        return 1

    def whitespace_token(self):
        match = WHITESPACE.match(self.code, self.current_index)
        if not match:
            return 0
        return len(match.group(0))

    def token_error(self):
        line, column = self.get_line_and_column()
        raise SyntaxError('{0}:{1} - unrecognised token "{2}"'.format(
            line + 1,
            column + 1,
            self.code[self.current_index:].split('\n', 1)[0]
        ))

    def get_line_and_column(self, offset=0):
        if offset == 0:
            return self.current_line, self.current_column

        if offset >= self.code_len - self.current_index:
            lines = self.code[self.current_index:].splitlines()
        else:
            lines = self.code[self.current_index:offset + self.current_index].splitlines()

        line_count = len(lines) - 1

        if line_count > 0:
            column = len(lines[-1])
        else:
            column = self.current_column + offset

        return (
            self.current_line + line_count,
            column
        )

    def add_token(self, tag, value, offset=0, length=None):
        if length is None:
            length = len(value)

        location_data = {}
        location_data['first_line'], location_data['first_column'] = \
            self.get_line_and_column(offset)
        location_data['last_line'], location_data['last_column'] = \
            self.get_line_and_column(offset + length)

        self.tokens.append((tag, value, location_data))

# Roughly speaking, these are the tokens
WHITESPACE          = re.compile(r'([\s\n]+)', re.UNICODE)
PREAMBLE            = re.compile(r'@(preamble)\s*\{', re.UNICODE | re.IGNORECASE)
STRING              = re.compile(r'@(string)\s*\{', re.UNICODE | re.IGNORECASE)
COMMENT             = re.compile(r'@(comment)[^\n]+', re.UNICODE | re.IGNORECASE)
ENTRY_START         = re.compile(r'@(?=[^\W][^,\s]*\s*\{)', re.UNICODE)
ENTRY_TYPE          = re.compile(r'([^\W\d_][^,\s]*)\s*\{', re.UNICODE)
IDENTIFIER          = re.compile(r'[^\W][^,\s}#]*(?=\s*[,]|\s*#\s*|\s*\}?(?:\n|$))', re.UNICODE)
NUMBER              = re.compile(r'\d+', re.UNICODE)
KEY                 = re.compile(r'([^\W\d][^,\s=]*)\s*=\s*', re.UNICODE)

# These are used internally by the more complex "tokens"
NEXT_QUOTE_BREAK    = re.compile(r'\n|"|\{')
NEXT_BRACKET_BREAK  = re.compile(r'\{|}|\n')
SPACE               = re.compile(r'\s+', re.UNICODE)
