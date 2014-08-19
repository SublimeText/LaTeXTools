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

from pybtex.utils import CaseInsensitiveDict
from pybtex.bibtex.exceptions import BibTeXError
from pybtex.bibtex.builtins import builtins, print_warning
from pybtex.bibtex.utils import wrap
#from pybtex.database.input import bibtex


class Variable(object):

    def _undefined(self):
        raise NotImplementedError

    default = property(_undefined)
    value_type = property(_undefined)

    def __init__(self, value=None):
        self.set(value)
    def __repr__(self):
        return '{0}({1})'.format(type(self).__name__, repr(self._value))
    def set(self, value):
        if value is None:
            value = self.default
        self.validate(value)
        self._value = value
    def validate(self, value):
        if not (isinstance(value, self.value_type) or value is None):
            raise ValueError('Invalid value for BibTeX %s: %s' % (self.__class__.__name__, value))
    def execute(self, interpreter):
        interpreter.push(self.value())
    def value(self):
        return self._value

    def __repr__(self):
        return '{0}({1})'.format(type(self).__name__, repr(self.value()))

    def __eq__(self, other):
        return type(self) == type(other) and self._value == other._value


class EntryVariable(Variable):
    def __init__(self, interpreter, name):
        Variable.__init__(self)
        self.interpreter = interpreter
        self.name = name
    def set(self, value):
        if value is not None:
            self.validate(value)
            self.interpreter.current_entry.vars[self.name] = value
    def value(self):
        try:
            return self.interpreter.current_entry.vars[self.name]
        except KeyError:
            return None


class Integer(Variable):
    value_type = int
    default = 0


class EntryInteger(Integer, EntryVariable):
    pass


class String(Variable):
    value_type = str
    default = ''


class EntryString(String, EntryVariable):
    pass


class MissingField(str):
    def __new__(cls, name):
        self = str.__new__(cls)
        self.name = name
        return self
    def __bool__(self):
        return False


class Field(object):
    def __init__(self, interpreter, name):
        self.interpreter = interpreter
        self.name = name

    def execute(self, interpreter):
        self.interpreter.push(self.value())

    def value(self):
        try:
            return self.interpreter.current_entry.fields[self.name]
        except KeyError:
            return MissingField(self.name)


class Crossref(Field):
    def __init__(self, interpreter):
        super(Crossref, self).__init__(interpreter, 'crossref')

    def value(self):
        try:
            value = self.interpreter.current_entry.fields[self.name]
            crossref_entry = self.interpreter.bib_data.entries[value]
        except KeyError:
            return MissingField(self.name)
        return crossref_entry.key


class Identifier(Variable):
    value_type = str
    def execute(self, interpreter):
        try:
            f = interpreter.vars[self.value()]
        except KeyError:
            raise BibTeXError('can not execute undefined function %s' % self)
        f.execute(interpreter)


class QuotedVar(Variable):
    value_type = str
    def execute(self, interpreter):
        try:
            var = interpreter.vars[self.value()]
        except KeyError:
            raise BibTeXError('can not push undefined variable %s' % self.value())
        interpreter.push(var)


class Function(object):
    def __init__(self, body=None):
        if body is None:
            body = []
        self.body = body

    def __repr__(self):
        return '{0}({1})'.format(type(self).__name__, repr(self.body))

    def __eq__(self, other):
        return type(self) == type(other) and self.body == other.body

    def execute(self, interpreter):
#        print 'executing function', self.body
        for element in self.body:
            element.execute(interpreter)


class FunctionLiteral(Function):
    def execute(self, interpreter):
        interpreter.push(Function(self.body))


class Interpreter(object):
    def __init__(self, bib_format, bib_encoding):
        self.bib_format = bib_format
        self.bib_encoding = bib_encoding
        self.stack = []
        self.vars = CaseInsensitiveDict(builtins)
        self.add_variable('global.max$', Integer(20000))  # constants taken from
        self.add_variable('entry.max$', Integer(250))     # BibTeX 0.99d (TeX Live 2012)
        self.add_variable('sort.key$', EntryString(self, 'sort.key$'))
        self.macros = {}
        self.output_buffer = []
        self.output_lines = []

    def push(self, value):
#        print 'push <%s>' % value
        self.stack.append(value)
#        print 'stack:', self.stack

    def pop(self):
        try:
            value = self.stack.pop()
        except IndexError:
            raise BibTeXError('pop from empty stack')
#        print 'pop <%s>' % value
        return value

    def get_token(self):
        return next(self.bst_script)

    def add_variable(self, name, value):
        if name in self.vars:
            raise BibTeXError('variable "{0}" already declared as {1}'.format(name, type(value).__name__))
        self.vars[name] = value

    def output(self, string):
        self.output_buffer.append(string)

    def newline(self):
        output = wrap(''.join(self.output_buffer))
        self.output_lines.append(output)
        self.output_lines.append('\n')
        self.output_buffer = []

    def run(self, bst_script, citations, bib_files, min_crossrefs):
        """Run bst script and return formatted bibliography."""

        self.bst_script = iter(bst_script)
        self.citations = citations
        self.bib_files = bib_files
        self.min_crossrefs = min_crossrefs

        for command in self.bst_script:
            name = command[0]
            args = command[1:]
            method = 'command_' + name.lower()
            if hasattr(self, method):
                getattr(self, method)(*args)
            else:
                print('Unknown command', name)

        return ''.join(self.output_lines)

    def command_entry(self, fields, ints, strings):
        for id in fields:
            name = id.value()
            self.add_variable(name, Field(self, name))
        self.add_variable('crossref', Crossref(self))
        for id in ints:
            name = id.value()
            self.add_variable(name, EntryInteger(self, name))
        for id in strings:
            name = id.value()
            self.add_variable(name, EntryString(self, name))

    def command_execute(self, command_):
#        print 'EXECUTE'
        command_[0].execute(self)

    def command_function(self, name_, body):
        name = name_[0].value()
        self.add_variable(name, Function(body))

    def command_integers(self, identifiers):
#        print 'INTEGERS'
        for identifier in identifiers:
            self.vars[identifier.value()] = Integer()

    def command_iterate(self, function_group):
        function = function_group[0].value()
        self._iterate(function, self.citations)

    def _iterate(self, function, citations):
        f = self.vars[function]
        for key in citations:
            self.current_entry_key = key
            self.current_entry = self.bib_data.entries[key]
            f.execute(self)
        self.currentEntry = None

    def command_macro(self, name_, value_):
        name = name_[0].value()
        value = value_[0].value()
        self.macros[name] = value

    def command_read(self):
#        print 'READ'
        p = self.bib_format(
            encoding=self.bib_encoding,
            macros=self.macros,
            person_fields=[],
            wanted_entries=self.citations,
        )
        self.bib_data = p.parse_files(self.bib_files)
        self.citations = self.bib_data.add_extra_citations(self.citations, self.min_crossrefs)
        self.citations = list(self.remove_missing_citations(self.citations))
#        for k, v in self.bib_data.iteritems():
#            print k
#            for field, value in v.fields.iteritems():
#                print '\t', field, value
#        pass

    def remove_missing_citations(self, citations):
        for citation in citations:
            if citation in self.bib_data.entries:
                yield citation
            else:
                print_warning('missing database entry for "{0}"'.format(citation))

    def command_reverse(self, function_group):
        function = function_group[0].value()
        self._iterate(function, reversed(self.citations))

    def command_sort(self):
        def key(citation):
            return self.bib_data.entries[citation].vars['sort.key$']
        self.citations.sort(key=key)

    def command_strings(self, identifiers):
        #print 'STRINGS'
        for identifier in identifiers:
            self.vars[identifier.value()] = String()

    @staticmethod
    def is_missing_field(field):
        return isinstance(field, MissingField)
