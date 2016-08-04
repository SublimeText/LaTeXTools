import re

# used to convert arguments and optional arguments into fields
BRACES_MATCH_REGEX = re.compile(r'\{([^\{\}\[\]]*)\}|\[([^\{\}\[\]]*)\]')

ALPHAS_REGEX = re.compile(r'^[a-zA-Z]+$')


def command_to_snippet(keyword):
    '''
    converts a LaTeX command, like \dosomething{arg1}{arg2} into a ST snippet
    like \dosomething{$1:arg1}{$2:arg2}
    '''
    # Replace strings in [] and {} with snippet syntax
    def replace_braces(matchobj):
        replace_braces.index += 1
        if matchobj.group(1) is not None:
            word = matchobj.group(1)
            return u'{${%d:%s}}' % (replace_braces.index, word)
        else:
            word = matchobj.group(2)
            return u'[${%d:%s}]' % (replace_braces.index, word)

    replace_braces.index = 0

    replace, n = BRACES_MATCH_REGEX.subn(
        replace_braces, keyword
    )

    # I do not understand why sometimes the input will eat the '\' charactor
    # before it! This code is to avoid these things.
    if n == 0 and ALPHAS_REGEX.search(keyword[1:].strip()) is not None:
        return keyword
    else:
        return replace
