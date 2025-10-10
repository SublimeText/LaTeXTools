from __future__ import annotations
from unittest import TestCase

from LaTeXTools.latextools.latex_cwl_completions import command_to_snippet
from ._data_decorator import data_decorator, data


@data_decorator
class CommandToSnippetTest(TestCase):
    @data(
        (
            (
                "\\item",
                ("\\item", "\\item")
            ),
            (
                "\\item []",
                ("\\item []", "\\item [${1:}]")
            ),
            (
                "\\item [label]",
                ("\\item [label]", "\\item [${1:label}]")
            ),
            (
                "\\item [%<label%>] %<description%>",
                ("\\item [label] description", "\\item [${1:label}] ${2:description}")
            ),
            (
                "\\bordermatrix{%<line%> \\cr %<... line%> \\cr}",
                (
                    "\\bordermatrix{line \\cr ... line \\cr}",
                    "\\bordermatrix{${1:line} \\cr ${2:... line} \\cr}"
                )
            ),
            (
                "\\Biggl\\{%<..%>\\Biggr\\}",
                ("\\Biggl\\{..\\Biggr\\}", "\\Biggl\\{${1:..}\\Biggr\\}")
            ),
            (
                "\\MakeActive\\%<<char>%>",
                ("\\MakeActive\\<char>", "\\MakeActive\\${1:<char>}")
            ),
            (
                "\\MakeActiveDef\\%<<char><parameters>%>{%<replace%>}",
                (
                    "\\MakeActiveDef\\<char><parameters>{replace}",
                    "\\MakeActiveDef\\${1:<char><parameters>}{${2:replace}}",
                )
            ),
            (
                "\\ifcase%<..%>\\or%<..%>\\fi",
                ("\\ifcase..\\or..\\fi", "\\ifcase${1:..}\\or${2:..}\\fi")
            ),
            (
                "\\Arrow{label%plain}",
                ("\\Arrow{label}", "\\Arrow{${1:label}}")
            ),
            (
                "\\ytableaushort[formatting%plain]{line1,line2,...%plain}",
                (
                    "\\ytableaushort[formatting]{line1,line2,...}",
                    "\\ytableaushort[${1:formatting}]{${2:line1,line2,...}}"
                )
            ),
        ),
    )
    def convert_cwl_item(self, cwl_item, result):
        self.assertEqual(command_to_snippet(cwl_item), result)
