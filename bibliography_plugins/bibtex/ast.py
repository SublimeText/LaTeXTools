class AstNode(object):

    def __repr__(self):
        return u'<AstNode>'


class PreambleNode(AstNode):

    def __repr__(self):
        return u'<Preamble>'


class StringNode(AstNode):

    def __repr__(self):
        if self.key:
            return u'<String [{0!s}]>'.format(self.key)
        else:
            return u'<String>'


class EntryNode(AstNode):

    def __repr__(self):
        if self.key:
            return u'<Entry [{0!s}]>'.format(self.key)
        else:
            return u'<Entry>'


class EntryKeyNode(AstNode):

    def __repr__(self):
        return u'<EntryKeyNode>'

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return u''


class KeyValueNode(AstNode):
    pass


class LiteralNode(AstNode):

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return u''

    __repr__ = __str__


class NumberNode(AstNode):

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return u''

    __repr__ = __str__


class QuotedLiteralNode(AstNode):

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return u''

    __repr__ = __str__


class ConcatenationNode(AstNode):

    def __str__(self):
        return ''.join(str(s) for s in (self.lhs, self.rhs))

    __repr__ = __str__
