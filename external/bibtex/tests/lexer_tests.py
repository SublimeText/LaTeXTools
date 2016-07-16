from ..lexer import Lexer

import unittest


class LexerTest(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()


class TestPreambleToken(LexerTest):

    def test_preamble_token(self):
        self.lexer.code = '@preamble{'
        result = self.lexer.preamble_token()

        self.assertEqual(
            result,
            10,
            'expecting 10 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'PREAMBLE',
            'expected token tag to be "PREAMBLE", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'preamble',
            'expected token value to be "preamble", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_preamble_token_case_insensitive(self):
        self.lexer.code = '@PREAMBLE{'
        self.lexer.preamble_token()

        self.assertEqual(
            self.lexer.tokens[0][1],
            'PREAMBLE',
            'expected token value to be "PREAMBLE", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_preamble_token_fails_match_without_at(self):
        self.lexer.code = 'preamble{'
        result = self.lexer.preamble_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_preamble_token_fails_match_without_bracket(self):
        self.lexer.code = '@preamble'
        result = self.lexer.preamble_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_preamble_token_only_consumes_up_to_bracket(self):
        self.lexer.code = '@preamble{blah, blah, blah, blah'
        result = self.lexer.preamble_token()

        self.assertEqual(
            result,
            10,
            'expecting 10 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_preamble_token_works_with_space_before_bracket(self):
        self.lexer.code = '@preamble {'
        result = self.lexer.preamble_token()

        self.assertEqual(
            result,
            11,
            'expecting 10 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestStringToken(LexerTest):

    def test_string_token(self):
        self.lexer.code = '@string{'
        result = self.lexer.string_token()

        self.assertEqual(
            result,
            8,
            'expecting 8 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'STRING',
            'expected token tag to be "STRING", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'string',
            'expected token value to be "string", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_string_token_case_insensitive(self):
        self.lexer.code = '@STRING{'
        self.lexer.string_token()

        self.assertEqual(
            self.lexer.tokens[0][1],
            'STRING',
            'expected token value to be "STRING", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_string_token_fails_match_without_at(self):
        self.lexer.code = 'string{'
        result = self.lexer.string_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_string_token_fails_match_without_bracket(self):
        self.lexer.code = '@string'
        result = self.lexer.string_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_string_token_only_consumes_up_to_bracket(self):
        self.lexer.code = '@string{blah, blah, blah, blah'
        result = self.lexer.string_token()

        self.assertEqual(
            result,
            8,
            'expecting 8 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_string_token_accepts_whitespace_before_bracket(self):
        self.lexer.code = '@string {'
        result = self.lexer.string_token()

        self.assertEqual(
            result,
            9,
            'expecting 8 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestCommentToken(LexerTest):

    def test_comment_token(self):
        self.lexer.code = '@comment{'
        result = self.lexer.comment_token()

        self.assertEqual(
            result,
            9,
            'expecting 9 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_comment_token_case_insensitive(self):
        self.lexer.code = '@COMMENT{'
        result = self.lexer.comment_token()

        self.assertEqual(
            result,
            9,
            'expecting 9 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_comment_token_fails_match_without_at(self):
        self.lexer.code = 'comment{'
        result = self.lexer.comment_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_comment_token_consumes_whole_line(self):
        self.lexer.code = '@comment{blah blah blah blah blah'
        result = self.lexer.comment_token()

        self.assertEqual(
            result,
            33,
            'expecting 33 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_comment_token_does_not_consume_next_line(self):
        self.lexer.code = '@comment{blah blah blah blah blah\nblah blah blah'
        result = self.lexer.comment_token()

        self.assertEqual(
            result,
            33,
            'expecting 33 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_comment_token_does_not_require_bracket(self):
        self.lexer.code = '@comment blah blah blah blah'
        result = self.lexer.comment_token()

        self.assertEqual(
            result,
            28,
            'expecting 28 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_comment_token_does_not_require_separator(self):
        self.lexer.code = '@commentblah blah blah blah'
        result = self.lexer.comment_token()

        self.assertEqual(
            result,
            27,
            'expecting 27 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestEntryStartToken(LexerTest):

    def test_entry_start_token(self):
        self.lexer.code = '@entry{'
        result = self.lexer.entry_start_token()

        self.assertEqual(
            result,
            1,
            'expecting 1 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'ENTRY_START',
            'expected token tag to be "ENTRY_START", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            '@',
            'expected token value to be "@", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_entry_start_token_fails_match_without_bracket(self):
        self.lexer.code = '@entry'
        result = self.lexer.entry_start_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_entry_start_token_fails_match_without_entry_type(self):
        self.lexer.code = '@{'
        result = self.lexer.entry_start_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_entry_start_token_accepts_whitespace_before_bracket(self):
        self.lexer.code = '@entry {'
        result = self.lexer.entry_start_token()

        self.assertEqual(
            result,
            1,
            'expecting 1 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestEntryTypeToken(LexerTest):

    def test_entry_type_token(self):
        # @ has been consumed by ENTRY_START
        self.lexer.code = 'entry{'
        result = self.lexer.entry_type_token()

        self.assertEqual(
            result,
            6,
            'expecting 6 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'ENTRY_TYPE',
            'expected token tag to be "ENTRY_TYPE", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'entry',
            'expected token value to be "entry", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_entry_type_token_fails_work_without_bracket(self):
        self.lexer.code = 'entry'
        result = self.lexer.entry_type_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_entry_type_token_only_consumes_up_to_bracket(self):
        self.lexer.code = 'entry{blah, blah, blah, blah'
        result = self.lexer.entry_type_token()

        self.assertEqual(
            result,
            6,
            'expecting 6 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_entry_type_token_accepts_whitespace_before_bracket(self):
        self.lexer.code = 'entry {'
        result = self.lexer.entry_type_token()

        self.assertEqual(
            result,
            7,
            'expecting 6 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestIdentifierToken(LexerTest):

    def test_identifier_token(self):
        self.lexer.code = 'beemer'
        result = self.lexer.identifier_token()

        self.assertEqual(
            result,
            6,
            'expecting 6 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'IDENTIFIER',
            'expected token tag to be "IDENTIFIER", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'beemer',
            'expected token value to be "beemer", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_identifier_token_only_matches_up_to_comma(self):
        self.lexer.code = 'beemer,blah'
        result = self.lexer.identifier_token()

        self.assertEqual(
            result,
            6,
            'expecting 6 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_identifier_token_only_matches_up_to_new_line(self):
        self.lexer.code = 'beemer\nblah'
        result = self.lexer.identifier_token()

        self.assertEqual(
            result,
            6,
            'expecting 6 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_identifier_token_only_matches_up_to_concat_operator(self):
        self.lexer.code = 'beemer#blah'
        result = self.lexer.identifier_token()

        self.assertEqual(
            result,
            6,
            'expecting 6 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_identifier_token_matches_with_leading_underscores(self):
        self.lexer.code = '__beemer'
        result = self.lexer.identifier_token()

        self.assertEqual(
            result,
            8,
            'expecting 8 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_identifier_token_matches_with_leading_number(self):
        self.lexer.code = '2beemer'
        result = self.lexer.identifier_token()

        self.assertEqual(
            result,
            7,
            'expecting 7 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestNumberToken(LexerTest):

    def test_number_token(self):
        self.lexer.code = '1234'
        result = self.lexer.number_token()

        self.assertEqual(
            result,
            4,
            'expecting 4 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'NUMBER',
            'expected token tag to be "NUMBER", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            '1234',
            'expected token value to be "1234", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_number_token_only_matches_numbers(self):
        self.lexer.code = '1234a'
        result = self.lexer.number_token()

        self.assertEqual(
            result,
            4,
            'expecting 4 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_number_token_fails_match_non_numbers(self):
        self.lexer.code = 'abc'
        result = self.lexer.number_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestKeyToken(LexerTest):

    def test_key_token(self):
        self.lexer.code = 'key = value'
        result = self.lexer.key_token()

        self.assertEqual(
            result,
            6,
            'expecting 6 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'KEY',
            'expected token tag to be "KEY", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'key',
            'expected token value to be "key", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_key_token_without_spaces(self):
        self.lexer.code = 'key=value'
        self.lexer.key_token()

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'KEY',
            'expected token tag to be "KEY", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'key',
            'expected token value to be "key", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_key_token_with_hyphens(self):
        self.lexer.code = 'key-token = value'
        self.lexer.key_token()

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'KEY',
            'expected token tag to be "KEY", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'key-token',
            'expected token value to be "key-token", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_key_token_accepts_leading_underscores(self):
        self.lexer.code = '__marked = {value}'
        result = self.lexer.key_token()

        self.assertEqual(
            self.lexer.tokens[0][0],
            'KEY',
            'expected token tag to be "KEY", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            '__marked',
            'expected token value to be "__marked", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_key_token_fails_match_without_equals(self):
        self.lexer.code = 'key value'
        result = self.lexer.key_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestValueToken(LexerTest):

    def test_value_token(self):
        self.lexer.code = '{value}'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.value_token()

        self.assertEqual(
            result,
            7,
            'expecting 7 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'VALUE',
            'expected token tag to be "VALUE", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value',
            'expected token value to be "value", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_value_token_fails_consume_without_bracket(self):
        self.lexer.code = 'value'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.value_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_value_token_fails_consume_without_end_bracket(self):
        self.lexer.code = '{value'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.value_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_value_token_with_nested_bracket(self):
        self.lexer.code = '{value {other value}}'
        self.lexer.code_len = len(self.lexer.code)
        self.lexer.value_token()

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value {other value}',
            'expected token value to be "value {{other value}}", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_value_token_with_nested_nested_bracket(self):
        self.lexer.code = '{value {{oth}er value}}'
        self.lexer.code_len = len(self.lexer.code)
        self.lexer.value_token()

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value {{oth}er value}',
            'expected token value to be "value {{{{oth}}er value}}", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_value_token_fails_consume_with_unmatched_nested_bracket(self):
        self.lexer.code = '{value {other value}'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.value_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_value_token_with_newline(self):
        self.lexer.code = '{value\nother value}'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.value_token()

        self.assertEqual(
            result,
            19,
            'expecting 19 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value other value',
            'expected token value to be "value other value", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_value_token_ends_with_newline(self):
        self.lexer.code = '{value\n}'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.value_token()

        self.assertEqual(
            result,
            8,
            'expecting 8 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value',
            'expected token value to be "value", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_value_token_with_newline_and_spaces(self):
        self.lexer.code = '{value\n     other value}'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.value_token()

        self.assertEqual(
            result,
            24,
            'expecting 24 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value other value',
            'expected token value to be "value other value", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_value_token_with_newline_followed_by_another_token(self):
        self.lexer.code = '{value\nother value}1234'
        self.lexer.code_len = len(self.lexer.code)

        self.lexer.current_index += self.lexer.value_token()
        self.lexer.number_token()

        self.assertEqual(
            len(self.lexer.tokens),
            2,
            'expected two tokens but found {0}: {1}'.format(
                len(self.lexer.tokens),
                self.lexer.tokens
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value other value',
            'expected VALUE token value to be "value other value", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

        self.assertEqual(
            self.lexer.tokens[1][1],
            '1234',
            'expected NUMBER token to be "1234", was "{0}"'.format(
                self.lexer.tokens[1][1]
            )
        )


class TestQuotedStringToken(LexerTest):

    def test_quoted_string_token(self):
        self.lexer.code = '"value"'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.quoted_string_token()

        self.assertEqual(
            result,
            7,
            'expecting 7 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'QUOTED_STRING',
            'expected token tag to be "QUOTED_STRING", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value',
            'expected token value to be "value", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_quoted_string_token_fails_consume_without_quotes(self):
        self.lexer.code = 'value'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.quoted_string_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_quoted_string_token_fails_consume_without_end_quote(self):
        self.lexer.code = '"value'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.quoted_string_token()

        self.assertEqual(
            result,
            0,
            'expecting 0 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_quoted_string_token_with_newline(self):
        self.lexer.code = '"value\nother value"'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.quoted_string_token()

        self.assertEqual(
            result,
            19,
            'expecting 19 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value other value',
            'expected token value to be "value other value", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_quoted_string_token_ends_with_newline(self):
        self.lexer.code = '"value\n"'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.quoted_string_token()

        self.assertEqual(
            result,
            8,
            'expecting 8 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value',
            'expected token value to be "value", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_quoted_string_token_with_newline_and_spaces(self):
        self.lexer.code = '"value\n     other value"'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.quoted_string_token()

        self.assertEqual(
            result,
            24,
            'expecting 24 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value other value',
            'expected token value to be "value other value", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_quoted_string_ends_with_slash(self):
        self.lexer.code = '"value other value\\\\"'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.quoted_string_token()

        self.assertEqual(
            result,
            21,
            'expected 21 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'value other value\\\\',
            'expected token value to be "value other value\\\\", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_quoted_string_containing_brackets(self):
        self.lexer.code = '"text {WITH} brackets"'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.quoted_string_token()

        self.assertEqual(
            result,
            22,
            'expected 22 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'text {WITH} brackets',
            'expected token value to be "text {{WITH}} brackets", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_quoted_string_containing_brackets_with_quotes(self):
        self.lexer.code = '"test {"}bracket{ escaping"}"'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.quoted_string_token()

        self.assertEqual(
            result,
            29,
            'expected 29 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'test {"}bracket{ escaping"}',
            'expected token value to be "test {{"}}bracket{{ escaping"}}", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_quoted_string_with_unmatched_brackets(self):
        self.lexer.code = '"test { unmatched"'
        self.lexer.code_len = len(self.lexer.code)
        result = self.lexer.quoted_string_token()

        self.assertEqual(
            result,
            18,
            'expected 18 characters to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            'test { unmatched',
            'expected token value to be "test {{ unmatched", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )


class TestEntryEndToken(LexerTest):

    def test_entry_end_token(self):
        self.lexer.code = '}'
        result = self.lexer.entry_end_token()

        self.assertEqual(
            result,
            1,
            'expecting 1 character to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            'ENTRY_END',
            'expected token tag to be "ENTRY_END", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            '}',
            'expected token value to be "}}", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_entry_end_token_fails_consume_non_match(self):
        self.lexer.code = 'blah}'
        result = self.lexer.entry_end_token()

        self.assertEqual(
            result,
            0,
            'expected 0 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestHashToken(LexerTest):

    def test_hash_token(self):
        self.lexer.code = '#'
        result = self.lexer.hash_token()

        self.assertEqual(
            result,
            1,
            'expecting 1 character to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            1,
            'expecting only 1 token to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][0],
            '#',
            'expected token tag to be "#", was "{0}"'.format(
                self.lexer.tokens[0]
            )
        )

        self.assertEqual(
            self.lexer.tokens[0][1],
            '#',
            'expected token value to be "#", was "{0}"'.format(
                self.lexer.tokens[0][1]
            )
        )

    def test_hash_token_fails_consume_non_match(self):
        self.lexer.code = 'blah#'
        result = self.lexer.hash_token()

        self.assertEqual(
            result,
            0,
            'expected 0 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestCommaToken(LexerTest):

    def test_comma_token(self):
        self.lexer.code = ','
        result = self.lexer.comma_token()

        self.assertEqual(
            result,
            1,
            'expecting 1 character to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            0,
            'expecting only no tokens to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

    def test_comma_token_fails_consume_non_match(self):
        self.lexer.code = 'blah,'
        result = self.lexer.comma_token()

        self.assertEqual(
            result,
            0,
            'expected 0 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestWhitespaceToken(LexerTest):

    def test_whitespace_token(self):
        self.lexer.code = ' '
        result = self.lexer.whitespace_token()

        self.assertEqual(
            result,
            1,
            'expecting 1 character to be consumed, found {0}'.format(
                result
            )
        )

        self.assertEqual(
            len(self.lexer.tokens),
            0,
            'expecting only no tokens to be created, found {0}'.format(
                len(self.lexer.tokens)
            )
        )

    def test_whitespace_token_multiple_spaces(self):
        self.lexer.code = '          '
        result = self.lexer.whitespace_token()

        self.assertEqual(
            result,
            10,
            'expected 10 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_whitespace_token_tabs(self):
        self.lexer.code = '\t\t\t'
        result = self.lexer.whitespace_token()

        self.assertEqual(
            result,
            3,
            'expected 3 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_whitespace_token_newline(self):
        self.lexer.code = '\n\n'
        result = self.lexer.whitespace_token()

        self.assertEqual(
            result,
            2,
            'expected 2 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_whitespace_token_mixed(self):
        self.lexer.code = '  \n\t  \n'
        result = self.lexer.whitespace_token()

        self.assertEqual(
            result,
            7,
            'expected 7 characters to be consumed, found {0}'.format(
                result
            )
        )

    def test_whitespace_token_fails_consume_non_match(self):
        self.lexer.code = 'b '
        result = self.lexer.whitespace_token()

        self.assertEqual(
            result,
            0,
            'expected 0 characters to be consumed, found {0}'.format(
                result
            )
        )


class TestTokenize(LexerTest):

    def test_tokenize_entry(self):
        tokens = self.lexer.tokenize('''
            @book{ citekey,
                Author = { Bloggs, Joe },
            }
        ''')

        self.assertEqual(
            len(tokens),
            7,
            'expected 7 tokens, found {0}'.format(
                len(tokens)
            )
        )

        self.assertEqual(
            tokens[0][0],
            'ENTRY_START',
            'expected first token to be an "ENTRY_START" token, was "{0}"'.format(
                tokens[0][0]
            )
        )

        self.assertEqual(
            tokens[1][0],
            'ENTRY_TYPE',
            'expected second token to be an "ENTRY_TYPE" token, was "{0}"'.format(
                tokens[1][0]
            )
        )

        self.assertEqual(
            tokens[1][1],
            'book',
            'expected second token value to be "book", was "{0}"'.format(
                tokens[1][1]
            )
        )

        self.assertEqual(
            tokens[2][0],
            'IDENTIFIER',
            'expected third token to be an "IDENTIFIER" token, was "{0}"'.format(
                tokens[2][0]
            )
        )

        self.assertEqual(
            tokens[2][1],
            'citekey',
            'expected third token value to be "citekey", was "{0}"'.format(
                tokens[2][1]
            )
        )

        self.assertEqual(
            tokens[3][0],
            'KEY',
            'expected fourth token to be an "KEY" token, was "{0}"'.format(
                tokens[3][0]
            )
        )

        self.assertEqual(
            tokens[3][1],
            'Author',
            'expected fourth token value to be "Author", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[4][0],
            'VALUE',
            'expected fifth token to be an "VALUE" token, was "{0}"'.format(
                tokens[4][0]
            )
        )

        self.assertEqual(
            tokens[4][1],
            'Bloggs, Joe',
            'expected fifth token value to be "Bloggs, Joe", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[5][0],
            'ENTRY_END',
            'expected sixth token to be an "ENTRY_END" token, was "{0}"'.format(
                tokens[5][0]
            )
        )

        self.assertEqual(
            tokens[-1][0],
            'EOF',
            'expected last token to be an "EOF" token, was "{0}"'.format(
                tokens[-1][0]
            )
        )

    def test_tokenize_with_hash(self):
        # preamble is easier to deal with
        tokens = self.lexer.tokenize('@preamble{constant # other_constant}')

        self.assertEqual(
            len(tokens),
            6,
            'expected 6 tokens, found {0}'.format(
                len(tokens)
            )
        )

        self.assertEqual(
            tokens[1][0],
            'IDENTIFIER',
            'expected first token to be an "IDENTIFIER" token, was "{0}"'.format(
                tokens[0][0]
            )
        )

        self.assertEqual(
            tokens[1][1],
            'constant',
            'expected first token value to be "constant", was "{0}"'.format(
                tokens[0][1]
            )
        )

        self.assertEqual(
            tokens[2][0],
            '#',
            'expected second token to be an "#" token, was "{0}"'.format(
                tokens[1][0]
            )
        )

        self.assertEqual(
            tokens[3][0],
            'IDENTIFIER',
            'expected third token to be an "IDENTIFIER" token, was "{0}"'.format(
                tokens[2][0]
            )
        )

        self.assertEqual(
            tokens[3][1],
            'other_constant',
            'expected third token value to be "constant", was "{0}"'.format(
                tokens[2][1]
            )
        )

        self.assertEqual(
            tokens[-1][0],
            'EOF',
            'expected last token to be an "EOF" token, was "{0}"'.format(
                tokens[-1][0]
            )
        )

    def test_entries_with_spaces_before_brackets(self):
        tokens = self.lexer.tokenize('''
            @book  { citekey,
                Author = { Bloggs, Joe },
            }
        ''')

        self.assertEqual(
            len(tokens),
            7,
            'expected 7 tokens, found {0}'.format(
                len(tokens)
            )
        )

        self.assertEqual(
            tokens[0][0],
            'ENTRY_START',
            'expected first token to be an "ENTRY_START" token, was "{0}"'.format(
                tokens[0][0]
            )
        )

        self.assertEqual(
            tokens[1][0],
            'ENTRY_TYPE',
            'expected second token to be an "ENTRY_TYPE" token, was "{0}"'.format(
                tokens[1][0]
            )
        )

        self.assertEqual(
            tokens[1][1],
            'book',
            'expected second token value to be "book", was "{0}"'.format(
                tokens[1][1]
            )
        )

        self.assertEqual(
            tokens[2][0],
            'IDENTIFIER',
            'expected third token to be an "IDENTIFIER" token, was "{0}"'.format(
                tokens[2][0]
            )
        )

        self.assertEqual(
            tokens[2][1],
            'citekey',
            'expected third token value to be "citekey", was "{0}"'.format(
                tokens[2][1]
            )
        )

        self.assertEqual(
            tokens[3][0],
            'KEY',
            'expected fourth token to be an "KEY" token, was "{0}"'.format(
                tokens[3][0]
            )
        )

        self.assertEqual(
            tokens[3][1],
            'Author',
            'expected fourth token value to be "Author", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[4][0],
            'VALUE',
            'expected fifth token to be an "VALUE" token, was "{0}"'.format(
                tokens[4][0]
            )
        )

        self.assertEqual(
            tokens[4][1],
            'Bloggs, Joe',
            'expected fifth token value to be "Bloggs, Joe", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[5][0],
            'ENTRY_END',
            'expected sixth token to be an "ENTRY_END" token, was "{0}"'.format(
                tokens[5][0]
            )
        )

        self.assertEqual(
            tokens[-1][0],
            'EOF',
            'expected last token to be an "EOF" token, was "{0}"'.format(
                tokens[-1][0]
            )
        )

    def test_entries_with_underscores_for_identifier(self):
        tokens = self.lexer.tokenize('''
            @book{__citekey,
                Author = { Bloggs, Joe },
            }
        ''')

        self.assertEqual(
            len(tokens),
            7,
            'expected 7 tokens, found {0}'.format(
                len(tokens)
            )
        )

        self.assertEqual(
            tokens[0][0],
            'ENTRY_START',
            'expected first token to be an "ENTRY_START" token, was "{0}"'.format(
                tokens[0][0]
            )
        )

        self.assertEqual(
            tokens[1][0],
            'ENTRY_TYPE',
            'expected second token to be an "ENTRY_TYPE" token, was "{0}"'.format(
                tokens[1][0]
            )
        )

        self.assertEqual(
            tokens[1][1],
            'book',
            'expected second token value to be "book", was "{0}"'.format(
                tokens[1][1]
            )
        )

        self.assertEqual(
            tokens[2][0],
            'IDENTIFIER',
            'expected third token to be an "IDENTIFIER" token, was "{0}"'.format(
                tokens[2][0]
            )
        )

        self.assertEqual(
            tokens[2][1],
            '__citekey',
            'expected third token value to be "__citekey", was "{0}"'.format(
                tokens[2][1]
            )
        )

        self.assertEqual(
            tokens[3][0],
            'KEY',
            'expected fourth token to be an "KEY" token, was "{0}"'.format(
                tokens[3][0]
            )
        )

        self.assertEqual(
            tokens[3][1],
            'Author',
            'expected fourth token value to be "Author", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[4][0],
            'VALUE',
            'expected fifth token to be an "VALUE" token, was "{0}"'.format(
                tokens[4][0]
            )
        )

        self.assertEqual(
            tokens[4][1],
            'Bloggs, Joe',
            'expected fifth token value to be "Bloggs, Joe", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[5][0],
            'ENTRY_END',
            'expected sixth token to be an "ENTRY_END" token, was "{0}"'.format(
                tokens[5][0]
            )
        )

        self.assertEqual(
            tokens[-1][0],
            'EOF',
            'expected last token to be an "EOF" token, was "{0}"'.format(
                tokens[-1][0]
            )
        )

    def test_entries_with_identifier_starting_with_number(self):
        tokens = self.lexer.tokenize('''
            @book{2citekey,
                Author = { Bloggs, Joe },
            }
        ''')

        self.assertEqual(
            len(tokens),
            7,
            'expected 7 tokens, found {0}'.format(
                len(tokens)
            )
        )

        self.assertEqual(
            tokens[0][0],
            'ENTRY_START',
            'expected first token to be an "ENTRY_START" token, was "{0}"'.format(
                tokens[0][0]
            )
        )

        self.assertEqual(
            tokens[1][0],
            'ENTRY_TYPE',
            'expected second token to be an "ENTRY_TYPE" token, was "{0}"'.format(
                tokens[1][0]
            )
        )

        self.assertEqual(
            tokens[1][1],
            'book',
            'expected second token value to be "book", was "{0}"'.format(
                tokens[1][1]
            )
        )

        self.assertEqual(
            tokens[2][0],
            'IDENTIFIER',
            'expected third token to be an "IDENTIFIER" token, was "{0}"'.format(
                tokens[2][0]
            )
        )

        self.assertEqual(
            tokens[2][1],
            '2citekey',
            'expected third token value to be "2citekey", was "{0}"'.format(
                tokens[2][1]
            )
        )

        self.assertEqual(
            tokens[3][0],
            'KEY',
            'expected fourth token to be an "KEY" token, was "{0}"'.format(
                tokens[3][0]
            )
        )

        self.assertEqual(
            tokens[3][1],
            'Author',
            'expected fourth token value to be "Author", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[4][0],
            'VALUE',
            'expected fifth token to be an "VALUE" token, was "{0}"'.format(
                tokens[4][0]
            )
        )

        self.assertEqual(
            tokens[4][1],
            'Bloggs, Joe',
            'expected fifth token value to be "Bloggs, Joe", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[5][0],
            'ENTRY_END',
            'expected sixth token to be an "ENTRY_END" token, was "{0}"'.format(
                tokens[5][0]
            )
        )

        self.assertEqual(
            tokens[-1][0],
            'EOF',
            'expected last token to be an "EOF" token, was "{0}"'.format(
                tokens[-1][0]
            )
        )

    def test_entries_with_number_for_identifier(self):
        tokens = self.lexer.tokenize('''
            @book{123456,
                Author = { Bloggs, Joe },
            }
        ''')

        self.assertEqual(
            len(tokens),
            7,
            'expected 7 tokens, found {0}'.format(
                len(tokens)
            )
        )

        self.assertEqual(
            tokens[0][0],
            'ENTRY_START',
            'expected first token to be an "ENTRY_START" token, was "{0}"'.format(
                tokens[0][0]
            )
        )

        self.assertEqual(
            tokens[1][0],
            'ENTRY_TYPE',
            'expected second token to be an "ENTRY_TYPE" token, was "{0}"'.format(
                tokens[1][0]
            )
        )

        self.assertEqual(
            tokens[1][1],
            'book',
            'expected second token value to be "book", was "{0}"'.format(
                tokens[1][1]
            )
        )

        self.assertEqual(
            tokens[2][0],
            'IDENTIFIER',
            'expected third token to be an "IDENTIFIER" token, was "{0}"'.format(
                tokens[2][0]
            )
        )

        self.assertEqual(
            tokens[2][1],
            '123456',
            'expected third token value to be "123456", was "{0}"'.format(
                tokens[2][1]
            )
        )

        self.assertEqual(
            tokens[3][0],
            'KEY',
            'expected fourth token to be an "KEY" token, was "{0}"'.format(
                tokens[3][0]
            )
        )

        self.assertEqual(
            tokens[3][1],
            'Author',
            'expected fourth token value to be "Author", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[4][0],
            'VALUE',
            'expected fifth token to be an "VALUE" token, was "{0}"'.format(
                tokens[4][0]
            )
        )

        self.assertEqual(
            tokens[4][1],
            'Bloggs, Joe',
            'expected fifth token value to be "Bloggs, Joe", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[5][0],
            'ENTRY_END',
            'expected sixth token to be an "ENTRY_END" token, was "{0}"'.format(
                tokens[5][0]
            )
        )

        self.assertEqual(
            tokens[-1][0],
            'EOF',
            'expected last token to be an "EOF" token, was "{0}"'.format(
                tokens[-1][0]
            )
        )

    def test_entries_with_underscores_for_key(self):
        tokens = self.lexer.tokenize('''
            @book{citekey,
                __marked = {project:1},
            }
        ''')

        self.assertEqual(
            len(tokens),
            7,
            'expected 7 tokens, found {0}'.format(
                len(tokens)
            )
        )

        self.assertEqual(
            tokens[0][0],
            'ENTRY_START',
            'expected first token to be an "ENTRY_START" token, was "{0}"'.format(
                tokens[0][0]
            )
        )

        self.assertEqual(
            tokens[1][0],
            'ENTRY_TYPE',
            'expected second token to be an "ENTRY_TYPE" token, was "{0}"'.format(
                tokens[1][0]
            )
        )

        self.assertEqual(
            tokens[1][1],
            'book',
            'expected second token value to be "book", was "{0}"'.format(
                tokens[1][1]
            )
        )

        self.assertEqual(
            tokens[2][0],
            'IDENTIFIER',
            'expected third token to be an "IDENTIFIER" token, was "{0}"'.format(
                tokens[2][0]
            )
        )

        self.assertEqual(
            tokens[2][1],
            'citekey',
            'expected third token value to be "citekey", was "{0}"'.format(
                tokens[2][1]
            )
        )

        self.assertEqual(
            tokens[3][0],
            'KEY',
            'expected fourth token to be an "KEY" token, was "{0}"'.format(
                tokens[3][0]
            )
        )

        self.assertEqual(
            tokens[3][1],
            '__marked',
            'expected fourth token value to be "__marked", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[4][0],
            'VALUE',
            'expected fifth token to be an "VALUE" token, was "{0}"'.format(
                tokens[4][0]
            )
        )

        self.assertEqual(
            tokens[4][1],
            'project:1',
            'expected fifth token value to be "project:1", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[5][0],
            'ENTRY_END',
            'expected sixth token to be an "ENTRY_END" token, was "{0}"'.format(
                tokens[5][0]
            )
        )

        self.assertEqual(
            tokens[-1][0],
            'EOF',
            'expected last token to be an "EOF" token, was "{0}"'.format(
                tokens[-1][0]
            )
        )

    def test_entry_with_url(self):
        # to ensure KEY isn't too greedy
        tokens = self.lexer.tokenize('''
            @book{citekey,
                url={https://books.google.ch/books?id=bar}
            }
        ''')

        self.assertEqual(
            len(tokens),
            7,
            'expected 7 tokens, found {0}'.format(
                len(tokens)
            )
        )

        self.assertEqual(
            tokens[0][0],
            'ENTRY_START',
            'expected first token to be an "ENTRY_START" token, was "{0}"'.format(
                tokens[0][0]
            )
        )

        self.assertEqual(
            tokens[1][0],
            'ENTRY_TYPE',
            'expected second token to be an "ENTRY_TYPE" token, was "{0}"'.format(
                tokens[1][0]
            )
        )

        self.assertEqual(
            tokens[1][1],
            'book',
            'expected second token value to be "book", was "{0}"'.format(
                tokens[1][1]
            )
        )

        self.assertEqual(
            tokens[2][0],
            'IDENTIFIER',
            'expected third token to be an "IDENTIFIER" token, was "{0}"'.format(
                tokens[2][0]
            )
        )

        self.assertEqual(
            tokens[2][1],
            'citekey',
            'expected third token value to be "citekey", was "{0}"'.format(
                tokens[2][1]
            )
        )

        self.assertEqual(
            tokens[3][0],
            'KEY',
            'expected fourth token to be an "KEY" token, was "{0}"'.format(
                tokens[3][0]
            )
        )

        self.assertEqual(
            tokens[3][1],
            'url',
            'expected fourth token value to be "url", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[4][0],
            'VALUE',
            'expected fifth token to be an "VALUE" token, was "{0}"'.format(
                tokens[4][0]
            )
        )

        self.assertEqual(
            tokens[4][1],
            'https://books.google.ch/books?id=bar',
            'expected fifth token value to be "https://books.google.ch/books?id=bar", was "{0}"'.format(
                tokens[3][1]
            )
        )

        self.assertEqual(
            tokens[5][0],
            'ENTRY_END',
            'expected sixth token to be an "ENTRY_END" token, was "{0}"'.format(
                tokens[5][0]
            )
        )

        self.assertEqual(
            tokens[-1][0],
            'EOF',
            'expected last token to be an "EOF" token, was "{0}"'.format(
                tokens[-1][0]
            )
        )
