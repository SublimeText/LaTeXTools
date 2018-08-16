import re

# used to convert arguments and optional arguments into fields
BRACES_MATCH_RX = re.compile(r'\{([^\}]*)\}|\[([^\]]*)\]')

ALPHAS_RX = re.compile(r'^[a-zA-Z]+$')

BEGIN_ENV_RX = re.compile(
    r'\\begin{(?P<name>[^\}]*)\}'
    r'(?:(?P<remainder1>.*)(?P<item>\\item)|(?P<remainder2>.*))'
)


def command_to_snippet(keyword):
    '''
    converts a LaTeX command, like \dosomething{arg1}{arg2} into a ST snippet
    like \dosomething{$1:arg1}{$2:arg2}
    '''

    # replace strings in [] and {} with snippet syntax
    def replace_braces(matchobj):
        replace_braces.index += 1
        if matchobj.group(1) is not None:
            word = matchobj.group(1)
            return u'{${%d:%s}}' % (replace_braces.index, word)
        else:
            word = matchobj.group(2)
            return u'[${%d:%s}]' % (replace_braces.index, word)

    replace_braces.index = 0

    # \begin{}...\end{} pairs should be inserted together
    m = BEGIN_ENV_RX.match(keyword)
    if m:
        item = bool(m.group('item'))
        name = m.group('name')

        # \begin{}, no environment
        if not name:
            replace, n = BRACES_MATCH_RX.subn(replace_braces, keyword)
            final = replace + u'\n${0}\n\\end{{$1}}$0'.format(
                replace_braces.index + 1
            )

            return keyword, final
        # \begin{} with environment
        # only create fields for any other items
        else:
            remainder = m.group('remainder1') or m.group('remainder2') or ''
            replace, n = BRACES_MATCH_RX.subn(replace_braces, remainder)

            final = u'\\begin{{{0}}}{1}\n'.format(name, replace or '')
            if item:
                final += u'\\item ${0}\n'.format(replace_braces.index + 1)
            else:
                final += u'${0}\n'.format(replace_braces.index + 1)
            final += u'\\end{{{0}}}$0'.format(name)

            # having \item at the end of the display value messes with
            # completions thus, we cut the \item off the end
            if item:
                return keyword[:-5], final
            else:
                return keyword, final
    else:
        replace, n = BRACES_MATCH_RX.subn(replace_braces, keyword)

        # I do not understand why sometimes the input will eat the '\'
        # character before it! This code is to avoid these things.
        if n == 0 and ALPHAS_RX.search(keyword[1:].strip()) is not None:
            return keyword, keyword
        else:
            return keyword, replace
