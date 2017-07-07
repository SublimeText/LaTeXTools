from unittest import TestCase

from LaTeXTools.latextools_utils.selectors import (
    AstNode as Node, AstLeaf as Leaf, build_ast
)


class BuildAstTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_simple(self):
        selector = "equation"
        ast = Leaf("equation")
        self.assertEqual(ast, build_ast(selector))

    def test_nested(self):
        selector = "list equation"
        ast = Node(
            " ",
            Leaf("list"),
            Leaf("equation")
        )
        self.assertEqual(ast, build_ast(selector))

    def test_nested_or(self):
        selector = "align | list equation"
        ast = Node(
            "|",
            Leaf("align"),
            Node(
                " ",
                Leaf("list"),
                Leaf("equation")
            )
        )
        self.assertEqual(ast, build_ast(selector))

    def test_complex1(self):
        selector = "align & enumerate itemize | list equation"
        ast = Node(
            "|",
            Node(
                "&",
                Leaf("align"),
                Node(
                    " ",
                    Leaf("enumerate"),
                    Leaf("itemize")
                )
            ),
            Node(
                " ",
                Leaf("list"),
                Leaf("equation")
            )
        )
        self.assertEqual(ast, build_ast(selector))

    def test_complex2(self):
        selector = "a, b - c, d - e f"
        ast = Node(
            ",",
            Node(
                ",",
                Leaf("a"),
                Node(
                    "-",
                    Leaf("b"),
                    Leaf("c")
                )
            ),
            Node(
                "-",
                Leaf("d"),
                Node(
                    " ",
                    Leaf("e"),
                    Leaf("f")
                )
            )
        )
        self.assertEqual(ast, build_ast(selector))

    def test_complex3(self):
        selector = "a, b & (c | d e) - f g, h i & j k - (l | m n)"
        ast = Node(
            ",",
            Node(
                ",",
                Leaf("a"),
                Node(
                    "&",
                    Leaf("b"),
                    Node(
                        "-",
                        Node(
                            "|",
                            Leaf("c"),
                            Node(
                                " ",
                                Leaf("d"),
                                Leaf("e")
                            )
                        ),
                        Node(
                            " ",
                            Leaf("f"),
                            Leaf("g")
                        )
                    )
                )
            ),
            Node(
                "&",
                Node(
                    " ",
                    Leaf("h"),
                    Leaf("i")
                ),
                Node(
                    "-",
                    Node(
                        " ",
                        Leaf("j"),
                        Leaf("k")
                    ),
                    Node(
                        "|",
                        Leaf("l"),
                        Node(
                            " ",
                            Leaf("m"),
                            Leaf("n")
                        )
                    )
                )
            )
        )
        self.assertEqual(ast, build_ast(selector))
