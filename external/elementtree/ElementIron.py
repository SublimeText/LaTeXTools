#
# ElementTree
# $Id: ElementIron.py 443 2006-11-18 18:47:34Z effbot $
#
# an experimental ElementTree driver for IronPython.
#
# Copyright (c) 2006 by Fredrik Lundh.  All rights reserved.
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# The ElementTree toolkit is
#
# Copyright (c) 1999-2007 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# and will comply with the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# Secret Labs AB or the author not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------

import clr
clr.AddReference("System.Xml")

from System.IO import StringReader, TextReader
from System.Xml import XmlReader, XmlNodeType

# node types/categories
START = XmlNodeType.Element
DATA_TEXT = XmlNodeType.Text
DATA_CDATA = XmlNodeType.CDATA
DATA_SPACE = XmlNodeType.Whitespace
END = XmlNodeType.EndElement

def _ironparse(source):

    # internal event generator.  takes a TextReader subclass, a file-
    # like object, or a filename, and generates an event stream.  use
    # the parse() and iterparse() adapters to access this from user-
    # code.

    if isinstance(source, TextReader):
        pass # use as is
    elif hasattr(source, "read"):
        # FIXME: implement TextReader wrapper for Python I/O objects
        source = StringReader(source.read())

    # FIXME: handle settings here? (disable comments, etc)

    reader = XmlReader.Create(source)

    # tag cache
    tags = {}
    namespaces = []

    def gettag():
        key = reader.NamespaceURI, reader.LocalName
        try:
            tag = tags[key]
        except KeyError:
            if key[0]:
                tag = "{%s}%s" % key
            else:
                tag = key[1]
            tags[key] = tag
        return tag

    while reader.Read():
        node = reader.NodeType
        if node == START:
            tag = gettag()
            attrib = {}
            ns = 0 # count namespace declarations
            while reader.MoveToNextAttribute():
                if reader.LocalName == "xmlns":
                    ns += 1 # default namespace
                    yield "start-ns", ("", reader.Value)
                elif reader.Prefix == "xmlns":
                    ns += 1 # prefixed namespace
                    yield "start-ns", (reader.LocalName, reader.Value)
                else:
                    attrib[gettag()] = reader.Value
            namespaces.append(ns)
            reader.MoveToElement()
            yield "start", tag, attrib
            if reader.IsEmptyElement:
                yield "end", tag
                for i in xrange(namespaces.pop()):
                    yield "end-ns", None
        elif node == END:
            yield "end", tags[reader.NamespaceURI, reader.LocalName]
            for i in xrange(namespaces.pop()):
                yield "end-ns", None
        elif node == DATA_TEXT or node == DATA_SPACE or node == DATA_CDATA:
            yield "data", reader.Value
        else:
            pass # yield "unknown", node
    reader.Close()

class _iterparse:

    # iterparse generator.  we could use a generator method for this,
    # but we need to expose a custom attribute as well, and generators
    # cannot have arbitrary attributes

    def __init__(self, source, target, events):
        self.root = None
        self.source = source
        self.target = target
        self.events = events
    def __iter__(self):
        source = self.source
        target = self.target
        events = self.events
        if not events:
            events = ["end"]
        start = end = start_ns = end_ns = None
        for event in events:
            # use the passed-in objects as event codes
            if event == "start":
                start = event
            elif event == "end":
                end = event
            elif event == "start-ns":
                start_ns = event
            elif event == "end-ns":
                end_ns = event
        for event in _ironparse(source):
            code = event[0]
            if code == "start":
                elem = target.start(event[1], event[2])
                if start:
                    yield start, elem
            elif code == "end":
                elem = target.end(event[1])
                if end:
                    yield end, elem
            elif code == "data":
                target.data(event[1])
            elif code == "start-ns":
                if start_ns:
                    yield start_ns, event[1]
            elif code == "end-ns":
                if end_ns:
                    yield end_ns, event[1]
        self.root = target.close()

class ParserAPI(object):

    def __init__(self, target_factory):
        self.target_factory = target_factory

    def parse(self, source):
        target = self.target_factory()
        for event in _ironparse(source):
            code = event[0]
            if code == "start":
                target.start(event[1], event[2])
            elif code == "end":
                target.end(event[1])
            elif code == "data":
                target.data(event[1])
        return target.close()

    def iterparse(self, source, events=None):
        target = self.target_factory()
        return _iterparse(source, target, events)

    def fromstring(self, source):
        return self.parse(StringReader(source))
