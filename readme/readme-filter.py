#!/usr/bin/env python
from __future__ import print_function

from pandocfilters import *


def minted_code_blocks(key, value, format_, meta):
    if (
        format_ == 'latex' and
        key == 'CodeBlock' and
        value[0][1]
    ):
        language = value[0][1][0]
        pos = value[0][1][1:] if len(value[0][1]) > 1 else []
        content = value[1]

        return [RawBlock(
            'latex',
            u'\\begin{{minted}}[{options}]{{{language}}}\n{content}\n\end{{minted}}'.format(
                language=language,
                options=u',\n'.join(pos + value[0][2]),
                content=content
            )
        )]


def remove_first_section_from_toc(key, value, format_, meta):
    if (
        format_ == 'latex' and
        key == 'Header' and
        value[0] == 1
    ):
        label = value[1][0]
        heading = stringify(value[2])
        return [Para([RawInline(
            "tex", u"\\section*{" + heading + u"}\label{" + label + u"}"
        )])]


def prepend_toc_to_body(key, value, format_, meta):
    if (
        not prepend_toc_to_body.added_toc and
        format_ == 'latex' and
        key == 'Header' and
        value[0] == 2
    ):
        prepend_toc_to_body.added_toc = True
        return [Para([RawInline("tex", '\\clearpage\\tableofcontents\\clearpage')]), Header(*value)]

prepend_toc_to_body.added_toc = False

if __name__ == '__main__':
    toJSONFilters([
        minted_code_blocks,
        remove_first_section_from_toc,
        prepend_toc_to_body
    ])
