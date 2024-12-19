class AstNode(object):

    def __repr__(self):
        return '<AstNode>'


class PreambleNode(AstNode):

    def __repr__(self):
        return '<Preamble>'


class StringNode(AstNode):

    def __repr__(self):
        if self.key:
            return '<String [{0!s}]>'.format(self.key)
        else:
            return '<String>'


class EntryNode(AstNode):

    def __repr__(self):
        if self.key:
            return '<Entry [{0!s}]>'.format(self.key)
        else:
            return '<Entry>'


class EntryKeyNode(AstNode):

    def __repr__(self):
        return '<EntryKeyNode>'

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return ''


class KeyValueNode(AstNode):
    pass


class LiteralNode(AstNode):

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return ''

    __repr__ = __str__


class NumberNode(AstNode):

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return ''

    __repr__ = __str__


class QuotedLiteralNode(AstNode):

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return ''

    __repr__ = __str__


class ConcatenationNode(AstNode):

    def __str__(self):
        return ''.join(str(s) for s in (self.lhs, self.rhs))

    __repr__ = __str__
