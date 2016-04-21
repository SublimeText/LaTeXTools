import re


def split_tex_string(string, maxsplit=-1, sep=None):
    '''
    A variation of string.split() to support tex strings

    In particular, ignores text in brackets, no matter how deeply nested and
    defaults to breaking on any space char or ~.
    '''

    if sep is None:
        # tilde == non-breaking space
        sep = r'(?u)[\s~]+'

    result = []

    # track ignore separators in braces
    brace_level = 0
    # calculate once
    string_len = len(string)
    word_start = 0
    splits = 0

    i = 0
    next_break = re.compile(r'\{|}|(?P<sep>' + sep + ')')

    while i < string_len:
        match = next_break.search(string, i)
        if match:
            matched = match.group(0)
            if matched == '{':
                brace_level += 1
            elif matched == '}':
                brace_level -= 1
            elif brace_level == 0 and match.start('sep') > 0:
                if match.end('sep') <= string_len:
                    result.append(string[word_start:match.start('sep')])
                    word_start = match.end('sep')

                    splits += 1
                    if splits == maxsplit:
                        break
            i = match.end()
        else:
            i = string_len

    if word_start < string_len:
        result.append(string[word_start:])

    return [part.strip() for part in result if part]


def tokenize_list(list_str, _and='and'):
    return split_tex_string(list_str, sep=r'(?iu)(?:|([\s~])+)' + _and + r'(?:[\s~]+|$)')
