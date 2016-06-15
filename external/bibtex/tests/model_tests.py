from ..model import *

from operator import itemgetter

import unittest


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.database = Database()

    def test_built_in_macros(self):
        self.assertEqual(
            self.database.get_macro('jan'),
            'January'
        )

        self.assertEqual(
            self.database.get_macro('feb'),
            'February'
        )

        self.assertEqual(
            self.database.get_macro('mar'),
            'March'
        )

        self.assertEqual(
            self.database.get_macro('apr'),
            'April'
        )

        self.assertEqual(
            self.database.get_macro('may'),
            'May'
        )

        self.assertEqual(
            self.database.get_macro('jun'),
            'June'
        )

        self.assertEqual(
            self.database.get_macro('jul'),
            'July'
        )

        self.assertEqual(
            self.database.get_macro('aug'),
            'August'
        )

        self.assertEqual(
            self.database.get_macro('sep'),
            'September'
        )

        self.assertEqual(
            self.database.get_macro('oct'),
            'October'
        )

        self.assertEqual(
            self.database.get_macro('nov'),
            'November'
        )

        self.assertEqual(
            self.database.get_macro('dec'),
            'December'
        )

    def test_macros_are_case_insensitive(self):
        self.assertEqual(
            self.database.get_macro('JAN'),
            'January'
        )

        self.assertEqual(
            self.database.get_macro('JaN'),
            'January'
        )

        self.assertEqual(
            self.database.get_macro('Jan'),
            'January'
        )

        self.assertEqual(
            self.database.get_macro('jAN'),
            'January'
        )

        self.assertEqual(
            self.database.get_macro('jaN'),
            'January'
        )

        self.assertEqual(
            self.database.get_macro('jan'),
            'January'
        )

    def test_adding_new_macro(self):
        self.database.add_macro('test', 'value')

        self.assertEqual(
            self.database.get_macro('test'),
            'value'
        )

    def test_get_preamble_without_preamble(self):
        self.assertEqual(
            self.database.get_preamble(),
            ''
        )

    def test_get_preamble(self):
        self.database.add_preamble('test')

        self.assertEqual(
            self.database.get_preamble(),
            'test'
        )

    def test_get_preamble_multiple_preambles(self):
        self.database.add_preamble('test')
        self.database.add_preamble('test2')
        self.database.add_preamble('test3')

        self.assertEqual(
            self.database.get_preamble(),
            'testtest2test3'
        )

    def test_get_entries_with_no_entry(self):
        self.assertEqual(
            self.database.get_entries(),
            []
        )

    def test_get_entries_with_invalid_entry(self):
        self.assertEqual(
            self.database.get_entries('missing'),
            []
        )

    def test_get_entries_retrieves_single_entry(self):
        entry = Entry('book', 'key')
        self.database._entries['key'] = entry

        self.assertEqual(
            self.database.get_entries('key'),
            [entry]
        )

    def test_get_entries_retieves_multiple_entries(self):
        entry1 = Entry('book', 'key1')
        entry2 = Entry('book', 'key2')

        self.database._entries['key1'] = entry1
        self.database._entries['key2'] = entry2

        result = self.database.get_entries('key1', 'key2')

        self.assertEqual(
            result,
            [entry1, entry2]
        )

    def test_get_entries_retieves_entries_in_order_requested(self):
        entry1 = Entry('book', 'key1')
        entry2 = Entry('book', 'key2')

        self.database._entries['key1'] = entry1
        self.database._entries['key2'] = entry2

        result = self.database.get_entries('key2', 'key1')

        self.assertEqual(
            result,
            [entry2, entry1]
        )

        result = self.database.get_entries('key1', 'key2')

        self.assertEqual(
            result,
            [entry1, entry2]
        )

    def test_getitem_missing_entity(self):
        self.assertRaises(
            KeyError,
            self.database.__getitem__,
            'missing'
        )

    def test_getitem_(self):
        entry = Entry('book', 'key')
        self.database._entries['key'] = entry

        self.assertEqual(
            self.database['key'],
            entry
        )

    def test_add_entry(self):
        entry = Entry('book', 'key')

        self.database.add_entry(entry)

        self.assertEqual(
            self.database._entries['key'],
            entry
        )

    def test_add_entry_ignores_entry_with_duplicate_key(self):
        entry1 = Entry('book', 'key')
        entry2 = Entry('article', 'key')

        self.database._entries['key'] = entry1

        self.assertEqual(
            self.database._entries['key'],
            entry1
        )

    def test_add_entry_succeeds_if_duplicate_deleted(self):
        entry1 = Entry('book', 'key')
        entry2 = Entry('article', 'key')

        self.database._entries['key'] = entry1

        del self.database['key']

        self.database.add_entry(entry2)

        self.assertEqual(
            self.database._entries['key'],
            entry2
        )

    def test_setitem_adds_entry(self):
        entry = Entry('book', 'key')

        self.database['key'] = entry

        self.assertEqual(
            self.database._entries['key'],
            entry
        )

    def test_setitem_uses_item_key(self):
        entry = Entry('book', 'key')

        self.database['dummy'] = entry

        self.assertEqual(
            self.database._entries['key'],
            entry
        )

        self.assertRaises(
            KeyError,
            self.database._entries.__getitem__,
            'dummy'
        )

class TestEntry(unittest.TestCase):

    def setUp(self):
        self.database = Database()
        self.entry = Entry('book', 'key')

    def test_entry_getitem_(self):
        self.entry._attributes['title'] = 'Moby Dick'

        self.assertEqual(
            self.entry['title'],
            'Moby Dick'
        )

    def test_entry_getitem_is_case_insensitive(self):
        self.entry._attributes['title'] = 'Moby Dick'

        self.assertEqual(
            self.entry['title'],
            'Moby Dick'
        )

        self.assertEqual(
            self.entry['TITLE'],
            'Moby Dick'
        )

        self.assertEqual(
            self.entry['TiTlE'],
            'Moby Dick'
        )

        self.assertEqual(
            self.entry['TitlE'],
            'Moby Dick'
        )

    def test_entry_getitem_uses_crossref(self):
        entry1 = Entry('book', 'key1')
        entry1._attributes['title'] = 'Moby Dick'

        self.database.add_entry(entry1)

        self.entry._attributes['crossref'] = 'key1'

        self.database.add_entry(self.entry)

        self.assertEqual(
            self.entry['title'],
            'Moby Dick'
        )

    def test_entry_getitem_crosses_multiple_crossrefs(self):
        entry1 = Entry('book', 'key1')
        entry1._attributes['crossref'] = 'key2'

        entry2 = Entry('book', 'key2')
        entry2._attributes['title'] = 'Moby Dick'

        self.database.add_entry(entry1)
        self.database.add_entry(entry2)

        self.entry._attributes['crossref'] = 'key1'

        self.database.add_entry(self.entry)

        self.assertEqual(
            self.entry['title'],
            'Moby Dick'
        )

    def test_entry_getitem_raises_keyerror_with_missing_crossref(self):
        self.entry._attributes['crossref'] = 'key1'

        self.database.add_entry(self.entry)

        self.assertRaises(
            KeyError,
            self.entry.__getitem__,
            'title'
        )

    def test_entry_getitem_raises_keyerror_with_missing_crossref_field(self):
        entry1 = Entry('book', 'key1')

        self.database.add_entry(entry1)

        self.entry._attributes['crossref'] = 'key1'

        self.database.add_entry(self.entry)

        self.assertRaises(
            KeyError,
            self.entry.__getitem__,
            'title'
        )
