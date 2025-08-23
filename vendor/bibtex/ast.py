class AstNode:
    def __repr__(self):
        return "<AstNode>"


class PreambleNode(AstNode):
    __slots__ = ["contents"]

    def __repr__(self):
        return "<Preamble>"

    def __str__(self):
        return self.contents


class StringNode(AstNode):
    __slots__ = ["key", "value"]

    def __repr__(self):
        if self.key:
            return f"<String [{self.key!s}]>"
        else:
            return "<String>"

    def __str__(self):
        return self.key


class EntryNode(AstNode):
    __slots__ = ["entry_type", "key", "fields"]

    def __repr__(self):
        if self.key:
            return f"<Entry [{self.key!s}]>"
        else:
            return "<Entry>"

    def __str__(self):
        return self.key


class EntryKeyNode(AstNode):
    __slots__ = ["value"]

    def __repr__(self):
        return "<EntryKeyNode>"

    def __str__(self):
        return self.value


class KeyValueNode(AstNode):
    __slots__ = ["key", "value"]

    def __repr__(self):
        if self.key:
            return f"<KeyValue [{self.key!s}]>"
        else:
            return "<KeyValue>"


class LiteralNode(AstNode):
    __slots__ = ["value"]

    def __repr__(self):
        return f"<LiteralNode '{self.value!s}'>"

    def __str__(self):
        return self.value


class NumberNode(AstNode):
    __slots__ = ["value"]

    def __repr__(self):
        return f"<LiteralNode '{self.value!s}'>"

    def __str__(self):
        return self.value


class QuotedLiteralNode(AstNode):
    __slots__ = ["value"]

    def __repr__(self):
        return f"<LiteralNode '{self.value!s}'>"

    def __str__(self):
        return self.value


class ConcatenationNode(AstNode):
    __slots__ = ["lhs", "rhs"]

    def __repr__(self):
        return f"<ConcatenationNode {self.lhs!r}, {self.rhs!r}>"

    def __str__(self):
        return f"{self.lhs!s}{self.rhs!s}"
