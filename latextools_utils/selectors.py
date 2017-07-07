"""
The MIT License (MIT)

Copyright (c) 2017 Richard Stein

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files
(the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from functools import partial
import re
import shlex
import string


class Ast():
    def __ne__(self, other):
        return not self == other


class AstNode(Ast):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and self.op == other.op and
            self.left == other.left and self.right == other.right)

    def __repr__(self):
        return "({op} {left} {right})".format(**self.__dict__)


class AstLeaf(Ast):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == other.value

    def __repr__(self):
        return self.value


class _Operator():
    def __init__(self, symbol, precedence, right_assoc=False):
        self._symbol = symbol
        self._precedence = precedence
        self._right_assoc = right_assoc

    def right_assoc(self):
        return self._right_assoc

    def precedence(self):
        return self._precedence

    def symbol(self):
        return self._symbol

    def __repr__(self):
        return "[{}]".format(self._symbol)


# format - symbol: (precedence, is_right_assoc, evaluation_function)
_operators = {
    ",": (200, False, lambda left, right: left() or right()),
    "|": (200, False, lambda left, right: left() or right()),
    "&": (250, False, lambda left, right: left() and right()),
    "-": (300, False, lambda left, right: left() and not right()),
    " ": (500, False, None),
}
_op_map = {k: _Operator(k, *v[:2]) for k, v in _operators.items()}
_eval_map = {k: v[2] for k, v in _operators.items() if v[2] is not None}

_WORDCHARS = string.ascii_lowercase + ".*!"
_RE_IS_NORMAL = re.compile(r"^[" + re.escape(_WORDCHARS) + r"]+$")


def _parse_selector(selector):
    def is_operator(token):
        return token in _op_map

    def is_normal_token(token):
        return _RE_IS_NORMAL.match(token)

    lex = shlex.shlex(selector)
    lex.wordchars = _WORDCHARS

    tokens = []
    last_was_normal = False

    token = lex.get_token()
    last_token = None
    while token:
        is_normal = is_normal_token(token)
        if last_was_normal and is_normal:
            tokens.append(" ")
        elif last_token in (None, "(") and is_operator(token):
            tokens.append("")
        tokens.append(token)
        last_was_normal = is_normal
        last_token = token
        token = lex.get_token()
    return tokens


def _convert_infix_to_postfix(tokens):
    # Implementation of the Shunting-yard algorithm
    op_stack = []
    postfix_list = []
    for token in tokens:
        if token == "(":
            op_stack.append(token)
        elif token == ")":
            while op_stack:
                head = op_stack.pop()
                if head == "(":
                    break
                postfix_list.append(head)
        elif token in _op_map:
            _operator = _op_map[token]
            while (
                    op_stack and
                    isinstance(op_stack[-1], _Operator) and
                    not _operator.right_assoc() and
                    _operator.precedence() <= op_stack[-1].precedence()):
                postfix_list.append(op_stack.pop())
            op_stack.append(_operator)
        else:
            postfix_list.append(token)

    while op_stack:
        postfix_list.append(op_stack.pop())
    return postfix_list


def _build_ast(postfix_list):
    ast_stack = []
    for token in postfix_list:
        if not isinstance(token, _Operator):
            assert isinstance(token, str)
            ast_stack.append(AstLeaf(token))
        else:
            assert len(ast_stack) >= 2
            left = ast_stack.pop()
            right = ast_stack.pop()

            ast_stack.append(AstNode(token.symbol(), right, left))

    assert len(ast_stack) == 1

    return ast_stack[0]


def build_ast(selector):
    tokens = _parse_selector(selector)
    print("tokens:", tokens)
    postfix_list = _convert_infix_to_postfix(tokens)
    print("postfix_list:", postfix_list)
    ast = _build_ast(postfix_list)
    return ast


def _build_selector_list(ast, selector_list=None):
    if selector_list is None:
        selector_list = []
    if isinstance(ast, AstLeaf):
        # if ast.value:
        selector_list.append(ast.value)
    else:
        assert ast.op == " "
        _build_selector_list(ast.left, selector_list)
        _build_selector_list(ast.right, selector_list)
    return selector_list


def _match_selector(ast, eval_func):
    if isinstance(ast, AstLeaf) or ast.op == " ":
        selector_list = _build_selector_list(ast)
        if not selector_list or selector_list == [""]:
            return True
        return eval_func(selector_list)
    else:
        assert ast.op in _eval_map
        return _eval_map[ast.op](
            partial(_match_selector, ast.left, eval_func),
            partial(_match_selector, ast.right, eval_func)
        )


def match_selector(selector, eval_func):
    if isinstance(selector, Ast):
        ast = selector
    else:
        ast = build_ast(selector)
    return _match_selector(ast, eval_func)
