from ..ast import *
from ..model import *
from ..parser import Parser

import unittest


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = Parser(None)

class TestValue(ParserTest):

    def test_value_with_identifier(self):
        self.parser.tokens = [('IDENTIFIER', 'id', {})]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        node = self.parser.value()

        self.assertIsInstance(
            node,
            LiteralNode
        )

        self.assertEqual(
            node.value,
            'id'
        )

    def test_value_with_number(self):
        self.parser.tokens = [('NUMBER', '1234', {})]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        node = self.parser.value()

        self.assertIsInstance(
            node,
            NumberNode
        )

        self.assertEqual(
            node.value,
            '1234'
        )

    def test_value_with_value(self):
        self.parser.tokens = [('VALUE', 'value', {})]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        node = self.parser.value()

        self.assertIsInstance(
            node,
            QuotedLiteralNode
        )

        self.assertEqual(
            node.value,
            'value'
        )

    def test_value_with_quoted_string(self):
        self.parser.tokens = [('QUOTED_STRING', 'value', {})]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        node = self.parser.value()

        self.assertIsInstance(
            node,
            QuotedLiteralNode
        )

        self.assertEqual(
            node.value,
            'value'
        )

    def test_value_with_invalid_token(self):
        self.parser.tokens = [('EOF', 'EOF', {})]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        self.assertRaises(
            SyntaxError,
            self.parser.value
        )

    def test_value_with_no_tokens(self):
        self.parser.tokens = []
        self.parser._current_token = 0
        self.parser._tokens_len = 0

        self.assertRaises(
            SyntaxError,
            self.parser.value
        )


class TestConcatenatedValue(ParserTest):

    def test_concatenated_value(self):
        self.parser.tokens = [
            ('IDENTIFIER', 'id', {}),
            ('#', '', {}),
            ('IDENTIFIER', 'id2', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 3

        node = self.parser.concatenated_value()

        self.assertIsInstance(
            node,
            ConcatenationNode
        )

        self.assertIsNotNone(
            node.lhs
        )

        self.assertEqual(
            node.lhs.value,
            'id'
        )

        self.assertIsNotNone(
            node.rhs
        )

        self.assertEqual(
            node.rhs.value,
            'id2'
        )

    def test_concatenated_value_fails_if_first_token_not_value(self):
        self.parser.tokens = [
            ('EOF', 'eof', {}),
            ('#', '', {}),
            ('IDENTIFIER', 'id2', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 3

        result = self.parser.concatenated_value()

        self.assertFalse(
            result
        )

    def test_concatenated_value_fails_if_second_token_not_hash(self):
        self.parser.tokens = [
            ('IDENTIFIER', 'id', {}),
            ('IDENTIFIER', 'id2', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 2

        result = self.parser.concatenated_value()

        self.assertFalse(
            result
        )

    def test_concatenated_value_fails_if_third_token_not_value(self):
        self.parser.tokens = [
            ('IDENTIFIER', 'id', {}),
            ('#', '', {}),
            ('EOF', 'eof', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 3

        result = self.parser.concatenated_value()

        self.assertFalse(
            result
        )

    def test_concatenated_value_with_additional_concatenation(self):
        self.parser.tokens = [
            ('IDENTIFIER', 'id', {}),
            ('#', '', {}),
            ('IDENTIFIER', 'id2', {}),
            ('#', '', {}),
            ('IDENTIFIER', 'id3', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 5

        node = self.parser.concatenated_value()

        self.assertIsInstance(
            node,
            ConcatenationNode
        )

        self.assertIsInstance(
            node.lhs,
            LiteralNode
        )

        self.assertIsInstance(
            node.rhs,
            ConcatenationNode
        )

    def test_concatenated_value_with_multiple_concatenations(self):
        self.parser.tokens = [
            ('IDENTIFIER', 'id', {}),
            ('#', '', {}),
            ('IDENTIFIER', 'id2', {}),
            ('#', '', {}),
            ('IDENTIFIER', 'id3', {}),
            ('#', '', {}),
            ('IDENTIFIER', 'id4', {}),
            ('#', '', {}),
            ('IDENTIFIER', 'id5', {}),
            ('#', '', {}),
            ('IDENTIFIER', 'id6', {}),
            ('#', '', {}),
            ('IDENTIFIER', 'id7', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 13

        node = self.parser.concatenated_value()

        self.assertIsInstance(
            node,
            ConcatenationNode
        )

        self.assertIsInstance(
            node.rhs,
            ConcatenationNode
        )

        self.assertIsInstance(
            node.rhs.rhs,
            ConcatenationNode
        )

        self.assertIsInstance(
            node.rhs.rhs.rhs,
            ConcatenationNode
        )

        self.assertIsInstance(
            node.rhs.rhs.rhs.rhs,
            ConcatenationNode
        )

        self.assertIsInstance(
            node.rhs.rhs.rhs.rhs.rhs,
            ConcatenationNode
        )

        self.assertIsInstance(
            node.rhs.rhs.rhs.rhs.rhs.rhs,
            LiteralNode
        )


class TestFieldValue(ParserTest):

    def test_field_value_value_only(self):
        self.parser.tokens = [('IDENTIFIER', 'id', {})]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        node = self.parser.field_value()

        self.assertIsNotNone(
            node
        )

        self.assertNotEqual(
            node,
            False
        )

    def test_field_value_concatenated_value(self):
        self.parser.tokens = [
            ('IDENTIFIER', 'id', {}),
            ('#', '#', {}),
            ('IDENTIFIER', 'id2', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 3

        node = self.parser.field_value()

        self.assertIsNotNone(
            node
        )

        self.assertIsInstance(
            node,
            ConcatenationNode
        )

    def test_field_value_with_invalid_token(self):
        self.parser.tokens = [('EOF', 'EOF', {})]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        self.assertRaises(
            SyntaxError,
            self.parser.field_value
        )

    def test_field_value_with_no_tokens(self):
        self.parser.tokens = []
        self.parser._current_token = 0
        self.parser._tokens_len = 0

        self.assertRaises(
            SyntaxError,
            self.parser.field_value
        )


class TestKeyValue(ParserTest):

    def test_key_value_simple(self):
        self.parser.tokens = [
            ('KEY', 'key', {}),
            ('VALUE', 'value', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 2

        node = self.parser.key_values()[0]

        self.assertIsInstance(
            node,
            KeyValueNode
        )

        self.assertEqual(
            node.key,
            'key'
        )

        self.assertIsInstance(
            node.value,
            QuotedLiteralNode
        )

    def test_key_value_only_one(self):
        self.parser.tokens = [
            ('KEY', 'key', {}),
            ('VALUE', 'value', {}),
            ('EOF', 'eof', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 3

        node = self.parser.key_values()[0]

        self.assertIsInstance(
            node,
            KeyValueNode
        )

    def test_multiple_keyvalues(self):
        self.parser.tokens = [
            ('KEY', 'key1', {}),
            ('VALUE', 'value1', {}),
            ('KEY', 'key2', {}),
            ('VALUE', 'value2', {}),
            ('KEY', 'key3', {}),
            ('VALUE', 'value4', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 6

        nodes = self.parser.key_values()

        self.assertEqual(
            len(nodes),
            3
        )

        self.assertIsInstance(
            nodes[0],
            KeyValueNode
        )

        self.assertIsInstance(
            nodes[1],
            KeyValueNode
        )

        self.assertIsInstance(
            nodes[2],
            KeyValueNode
        )

    def test_key_value_without_key(self):
        self.parser.tokens = [
            ('VALUE', 'value1', {}),
            ('VALUE', 'value2', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 2

        result = self.parser.key_values()

        self.assertEqual(
            result,
            []
        )

    def test_key_value_without_value(self):
        self.parser.tokens = [
            ('KEY', 'key', {}),
            ('EOF', 'EOF', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 2

        self.assertRaises(
            SyntaxError,
            self.parser.key_values
        )

    def test_key_value_with_invalid_token(self):
        self.parser.tokens = [('EOF', 'EOF', {})]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        result = self.parser.key_values()

        self.assertEqual(
            result,
            []
        )

    def test_key_value_with_no_tokens(self):
        self.parser.tokens = []
        self.parser._current_token = 0
        self.parser._tokens_len = 0

        result = self.parser.key_values()

        self.assertEqual(
            result,
            []
        )

class TestEntryKey(ParserTest):

    def test_entry_key(self):
        self.parser.tokens = [('IDENTIFIER', 'id', {})]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        node = self.parser.entry_key()

        self.assertIsInstance(
            node,
            EntryKeyNode
        )

        self.assertEqual(
            node.value,
            'id'
        )

    def test_entry_key_with_number(self):
        self.parser.tokens = [('NUMBER', '123456', {})]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        node = self.parser.entry_key()

        self.assertIsInstance(
            node,
            EntryKeyNode
        )

        self.assertEqual(
            node.value,
            '123456'
        )

    def test_entry_key_with_invalid_token(self):
        self.parser.tokens = [('EOF', 'EOF', {})]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        self.assertRaises(
            SyntaxError,
            self.parser.entry_key
        )

    def test_entry_key_with_no_tokens(self):
        self.parser.tokens = []
        self.parser._current_token = 0
        self.parser._tokens_len = 0

        self.assertRaises(
            SyntaxError,
            self.parser.entry_key
        )


class TestEntry(ParserTest):

    def test_entry(self):
        self.parser.tokens = [
            ('ENTRY_TYPE', 'book', {}),
            ('IDENTIFIER', 'id', {}),
            ('KEY', 'title', {}),
            ('VALUE', '1984', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 5

        node = self.parser.entry()

        self.assertIsInstance(
            node,
            EntryNode
        )

        self.assertIsInstance(
            node.key,
            EntryKeyNode
        )

        self.assertIsInstance(
            node.fields[0],
            KeyValueNode
        )

    def test_entry_works_without_key_value(self):
        self.parser.tokens = [
            ('ENTRY_TYPE', 'book', {}),
            ('IDENTIFIER', 'id', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 3

        node = self.parser.entry()

        self.assertIsInstance(
            node,
            EntryNode
        )

    def test_entry_fails_without_entry_type(self):
        self.parser.tokens = [
            ('IDENTIFIER', 'id', {}),
            ('KEY', 'title', {}),
            ('VALUE', '1984', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 4

        self.assertRaises(
            SyntaxError,
            self.parser.entry
        )

    def test_entry_fails_with_invalid_entry_type(self):
        self.parser.tokens = [
            ('EOF', 'eof', {}),
            ('IDENTIFIER', 'id', {}),
            ('KEY', 'title', {}),
            ('VALUE', '1984', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 5

        self.assertRaises(
            SyntaxError,
            self.parser.entry
        )

    def test_entry_fails_without_identifier(self):
        self.parser.tokens = [
            ('ENTRY_TYPE', 'book', {}),
            ('KEY', 'title', {}),
            ('VALUE', '1984', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 4

        self.assertRaises(
            SyntaxError,
            self.parser.entry
        )

    def test_entry_fails_without_entry_end(self):
        self.parser.tokens = [
            ('ENTRY_TYPE', 'book', {}),
            ('IDENTIFIER', 'id', {}),
            ('KEY', 'title', {}),
            ('VALUE', '1984', {}),
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 4

        self.assertRaises(
            SyntaxError,
            self.parser.entry
        )

    def test_entry_fails_if_key_invalid_type(self):
        self.parser.tokens = [
            ('ENTRY_TYPE', 'book', {}),
            ('IDENTIFIER', 'id', {}),
            ('EOF', 'eof', {}),
            ('VALUE', '1984', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 5

        self.assertRaises(
            SyntaxError,
            self.parser.entry
        )

    def test_entry_fails_if_value_invalid_type(self):
        self.parser.tokens = [
            ('ENTRY_TYPE', 'book', {}),
            ('IDENTIFIER', 'id', {}),
            ('KEY', 'key', {}),
            ('EOF', 'eof', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 5

        self.assertRaises(
            SyntaxError,
            self.parser.entry
        )

    def test_entry_fails_with_no_entry_type(self):
        self.parser.tokens = [
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 0

        self.assertRaises(
            SyntaxError,
            self.parser.entry
        )


class TestString(ParserTest):

    def test_string(self):
        self.parser.tokens = [
            ('KEY', 'cup', {}),
            ('VALUE', 'Cambridge University Press', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 3

        node = self.parser.string()

        self.assertIsInstance(
            node,
            StringNode
        )

        self.assertEqual(
            node.key,
            'cup'
        )

        self.assertIsInstance(
            node.value,
            QuotedLiteralNode
        )

    def test_string_fails_without_key(self):
        self.parser.tokens = [
            ('VALUE', 'Cambridge University Press', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 2

        self.assertRaises(
            SyntaxError,
            self.parser.string
        )

    def test_string_fails_without_value(self):
        self.parser.tokens = [
            ('KEY', 'cup', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 2

        self.assertRaises(
            SyntaxError,
            self.parser.string
        )

    def test_string_fails_without_entry_end(self):
        self.parser.tokens = [
            ('KEY', 'cup', {}),
            ('VALUE', 'Cambridge University Press', {}),
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 2

        self.assertRaises(
            SyntaxError,
            self.parser.string
        )

    def test_string_fails_with_invalid_key_type(self):
        self.parser.tokens = [
            ('EOF', 'eof', {}),
            ('VALUE', 'Cambridge University Press', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 3

        self.assertRaises(
            SyntaxError,
            self.parser.string
        )

    def test_string_fails_with_invalid_value_type(self):
        self.parser.tokens = [
            ('KEY', 'cup', {}),
            ('EOF', 'eof', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 3

        self.assertRaises(
            SyntaxError,
            self.parser.string
        )

    def test_string_fails_with_invalid_entry_end(self):
        self.parser.tokens = [
            ('KEY', 'cup', {}),
            ('VALUE', 'Cambridge University Press', {}),
            ('EOF', 'eof', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 3

        self.assertRaises(
            SyntaxError,
            self.parser.string
        )

    def test_string_fails_without_tokens(self):
        self.parser.tokens = []
        self.parser._current_token = 0
        self.parser._tokens_len = 0

        self.assertRaises(
            SyntaxError,
            self.parser.string
        )


class TestPreamble(ParserTest):

    def test_preamble(self):
        self.parser.tokens = [
            ('VALUE', r'\newcommand{\nop}[1]{}', {}),
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 2

        node = self.parser.preamble()

        self.assertIsInstance(
            node,
            PreambleNode
        )

        self.assertIsInstance(
            node.contents,
            QuotedLiteralNode
        )

    def test_preamble_with_only_entry_end(self):
        self.parser.tokens = [
            ('ENTRY_END', '}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        node = self.parser.preamble()

        self.assertIsInstance(
            node,
            PreambleNode
        )

    def test_preamble_fails_without_entry_end(self):
        self.parser.tokens = [
            ('VALUE', r'\newcommand{\nop}[1]{}', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        self.assertRaises(
            SyntaxError,
            self.parser.preamble
        )

    def test_preamble_fails_with_invalid_entry_end(self):
        self.parser.tokens = [
            ('VALUE', r'\newcommand{\nop}[1]{}', {}),
            ('EOF', '', {})
        ]
        self.parser._current_token = 0
        self.parser._tokens_len = 1

        self.assertRaises(
            SyntaxError,
            self.parser.preamble
        )


class TestParse(unittest.TestCase):

    class DummyLexer(object):
        def __init__(self, tokens):
            self.tokens = tokens

        def tokenize(self, _):
            return self.tokens

    def test_parse_preamble(self):
        parser = Parser(self.DummyLexer([
            ('PREAMBLE', '@preambles', {}),
            ('VALUE', r'\newcommand{\nop}[1]{}', {}),
            ('ENTRY_END', '}', {}),
            ('EOF', '', {})
        ]))

        result = parser.parse(None)

        self.assertIsInstance(
            result,
            Database
        )

        self.assertIsNotNone(
            result.get_preamble()
        )

    def test_parse_string(self):
        parser = Parser(self.DummyLexer([
            ('STRING', '@string', {}),
            ('KEY', 'cup', {}),
            ('VALUE', 'Cambridge University Press', {}),
            ('ENTRY_END', '}', {}),
            ('EOF', '', {})
        ]))

        result = parser.parse(None)

        self.assertIsInstance(
            result,
            Database
        )

        self.assertIsNotNone(
            result.get_macro('cup')
        )

    def test_parse_entry(self):
        parser = Parser(self.DummyLexer([
            ('ENTRY_START', '@', {}),
            ('ENTRY_TYPE', 'book', {}),
            ('IDENTIFIER', 'id', {}),
            ('ENTRY_END', '}', {}),
            ('EOF', '', {})
        ]))

        result = parser.parse(None)

        self.assertIsInstance(
            result,
            Database
        )

        self.assertIsNotNone(
            result.get_entries('id')
        )

    def test_parse_entry_with_number_for_key(self):
        parser = Parser(self.DummyLexer([
            ('ENTRY_START', '@', {}),
            ('ENTRY_TYPE', 'book', {}),
            ('NUMBER', '123456', {}),
            ('ENTRY_END', '}', {}),
            ('EOF', '', {})
        ]))

        result = parser.parse(None)

        self.assertIsInstance(
            result,
            Database
        )

        self.assertIsNotNone(
            result.get_entries('123456')
        )

    def test_parse_entry_with_field(self):
        parser = Parser(self.DummyLexer([
            ('ENTRY_START', '@', {}),
            ('ENTRY_TYPE', 'book', {}),
            ('IDENTIFIER', 'id', {}),
            ('KEY', 'title', {}),
            ('VALUE', '1984', {}),
            ('ENTRY_END', '}', {}),
            ('EOF', '', {})
        ]))

        result = parser.parse(None)

        self.assertIsInstance(
            result,
            Database
        )

        self.assertIsNotNone(
            result.get_entries('id')
        )

        self.assertEquals(
            result.get_entries('id')[0]['title'],
            '1984'
        )

    def test_parse_entry_with_name(self):
        parser = Parser(self.DummyLexer([
            ('ENTRY_START', '@', {}),
            ('ENTRY_TYPE', 'book', {}),
            ('IDENTIFIER', 'id', {}),
            ('KEY', 'author', {}),
            ('VALUE', 'Coddington, Simon', {}),
            ('ENTRY_END', '}', {}),
            ('EOF', '', {})
        ]))

        result = parser.parse(None)

        self.assertEquals(
            result.get_entries('id')[0]['author'],
            'Coddington, Simon'
        )

    def test_parse_entry_with_multi_name_field(self):
        parser = Parser(self.DummyLexer([
            ('ENTRY_START', '@', {}),
            ('ENTRY_TYPE', 'book', {}),
            ('IDENTIFIER', 'id', {}),
            ('KEY', 'author', {}),
            ('VALUE', 'Coddington, Simon and Harding, Warren', {}),
            ('ENTRY_END', '}', {}),
            ('EOF', '', {})
        ]))

        result = parser.parse(None)

        self.assertEquals(
            result.get_entries('id')[0]['author'],
            'Coddington, Simon and Harding, Warren'
        )

    def test_parse_eof(self):
        parser = Parser(self.DummyLexer([
            ('EOF', '', {})
        ]))

        result = parser.parse(None)

        self.assertIsInstance(
            result,
            Database
        )

    def test_parse_fails_with_unexpected_token(self):
        parser = Parser(self.DummyLexer([
            ('VALUE', 'value', {})
        ]))

        self.assertRaises(
            SyntaxError,
            parser.parse,
            None
        )

    def test_parse_fails_with_no_tokens(self):
        parser = Parser(self.DummyLexer([]))

        self.assertRaises(
            SyntaxError,
            parser.parse,
            None
        )
