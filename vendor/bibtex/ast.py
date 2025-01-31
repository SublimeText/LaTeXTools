class AstNode:
    def __repr__(self):
        return "<AstNode>"


class PreambleNode(AstNode):
    __slots__ = ["contents"]

    def __repr__(self):
        return "<Preamble>"


class StringNode(AstNode):
    __slots__ = ["key", "value"]

    def __repr__(self):
        if self.key:
            return "<String [{0!s}]>".format(self.key)
        else:
            return "<String>"


class EntryNode(AstNode):
    __slots__ = ["entry_type", "key", "fields"]

    def __repr__(self):
        if self.key:
            return "<Entry [{0!s}]>".format(self.key)
        else:
            return "<Entry>"


class EntryKeyNode(AstNode):
    __slots__ = ["value"]

    def __repr__(self):
        return "<EntryKeyNode>"

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return ""


class KeyValueNode(AstNode):
    __slots__ = ["key", "value"]


class LiteralNode(AstNode):
    __slots__ = ["value"]

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return ""

    __repr__ = __str__


class NumberNode(AstNode):
    __slots__ = ["value"]

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return ""

    __repr__ = __str__


class QuotedLiteralNode(AstNode):
    __slots__ = ["value"]

    def __str__(self):
        try:
            return self.value
        except (AttributeError, NameError):
            return ""

    __repr__ = __str__


class ConcatenationNode(AstNode):
    __slots__ = ["lhs", "rhs"]

    def __str__(self):
        return "".join(str(s) for s in (self.lhs, self.rhs))

    __repr__ = __str__
