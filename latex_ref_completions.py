# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    import getTeXRoot
    from latex_fill_all import FillAllHelper
    from latextools_utils.is_tex_file import is_tex_file, get_tex_extensions
    from latextools_utils import get_setting
else:
    _ST3 = True
    from . import getTeXRoot
    from .latex_fill_all import FillAllHelper
    from .latextools_utils.is_tex_file import is_tex_file, get_tex_extensions
    from .latextools_utils import get_setting

import os
import re
import codecs

_ref_special_commands = "|".join([
    "", "eq", "page", "v", "V", "auto", "autopage", "name",
    "c", "C", "cpage", "Cpage", "namec", "nameC", "lcnamec", "labelc",
    "labelcpage", "sub", "f", "F", "vpage", "t", "p", "A", "B", "P", "S",
    "title", "headname", "tocname"
])[::-1]

OLD_STYLE_REF_REGEX = re.compile(
    r"([^_]*_)?(?:\*?s?fer(" +
    _ref_special_commands +
    r")?)\\"
)

NEW_STYLE_REF_REGEX = re.compile(
    r"([^}]*)\{(?:\*?s?fer(" +
    _ref_special_commands +
    r")?)\\"
)

NEW_STYLE_REF_RANGE_REGEX = re.compile(
    r"([^}]*)\{(?:\}[^\}]*\{)?\*?egnarfer(egapv|v|egapc|C|c)\\"
)

NEW_STYLE_REF_MULTIVALUE_REGEX = re.compile(
    r"([^},]*)(?:,[^},]*)*\{fer(c|C|egapc|egapC)\\"
)

AUTOCOMPLETE_EXCLUDE_RX = re.compile(
    r"fer(?:" + _ref_special_commands + r")?\\?"
)


# recursively search all linked tex files to find all
# included \label{} tags in the document and extract
def find_labels_in_files(rootdir, src, labels):
    if not is_tex_file(src):
        src_tex_file = None
        for ext in get_tex_extensions():
            src_tex_file = ''.join((src, ext))
            if os.path.exists(os.path.join(rootdir, src_tex_file)):
                src = src_tex_file
                break
        if src != src_tex_file:
            print("Could not find file {0}".format(src))
            return

    file_path = os.path.normpath(os.path.join(rootdir, src))
    print ("Searching file: " + repr(file_path))
    # The following was a mistake:
    #dir_name = os.path.dirname(file_path)
    # THe reason is that \input and \include reference files **from the directory
    # of the master file**. So we must keep passing that (in rootdir).

    # read src file and extract all label tags

    # We open with utf-8 by default. If you use a different encoding, too bad.
    # If we really wanted to be safe, we would read until \begin{document},
    # then stop. Hopefully we wouldn't encounter any non-ASCII chars there. 
    # But for now do the dumb thing.
    try:
        src_file = codecs.open(file_path, "r", "UTF-8")
    except IOError:
        sublime.status_message("LaTeXTools WARNING: cannot find included file " + file_path)
        print ("WARNING! I can't find it! Check your \\include's and \\input's." )
        return

    src_content = re.sub("%.*", "", src_file.read())
    src_file.close()

    # If the file uses inputenc with a DIFFERENT encoding, try re-opening
    # This is still not ideal because we may still fail to decode properly, but still... 
    m = re.search(r"\\usepackage\[(.*?)\]\{inputenc\}", src_content)
    if m and (m.group(1) not in ["utf8", "UTF-8", "utf-8"]):
        print("reopening with encoding " + m.group(1))
        f = None
        try:
            f = codecs.open(file_path, "r", m.group(1))
            src_content = re.sub("%.*", "", f.read())
        except:
            print("Uh-oh, could not read file " + file_path + " with encoding " + m.group(1))
        finally:
            if f and not f.closed:
                f.close()

    labels += re.findall(r'\\label\{([^{}]+)\}', src_content)

    # search through input tex files recursively
    for f in re.findall(r'\\(?:input|include|subfile)\{([^\{\}]+)\}', src_content):
        find_labels_in_files(rootdir, f, labels)


# get_ref_completions forms the guts of the parsing shared by both the
# autocomplete plugin and the quick panel command
def get_ref_completions(view):
    completions = []
    # Check the file buffer first:
    #    1) in case there are unsaved changes
    #    2) if this file is unnamed and unsaved, get_tex_root will fail
    view.find_all(r'\\label\{([^\{\}]+)\}', 0, '\\1', completions)

    root = getTeXRoot.get_tex_root(view)
    if root:
        print("TEX root: " + repr(root))
        find_labels_in_files(os.path.dirname(root), root, completions)

    # remove duplicates
    completions = list(set(completions))

    return completions


# Based on html_completions.py
#
# It expands references; activated by
# ref<tab>
# refp<tab> [this adds parentheses around the ref]
# eqref<tab> [obvious]
#
# Furthermore, you can "pre-filter" the completions: e.g. use
#
# ref_sec
#
# to select all labels starting with "sec".
#
# There is only one problem: if you have a label "sec:intro", for instance,
# doing "ref_sec:" will find it correctly, but when you insert it, this will be done
# right after the ":", so the "ref_sec:" won't go away. The problem is that ":" is a
# word boundary. Then again, TextMate has similar limitations :-)

# called by LatexFillAllCommand
class RefFillAllHelper(FillAllHelper):

    def get_auto_completions(self, view, prefix, line):
        # Reverse, to simulate having the regex
        # match backwards (cool trick jps btw!)
        line = line[::-1]

        # Check the first location looks like a ref, but backward
        old_style = OLD_STYLE_REF_REGEX.match(line)

        # Do not match on plain "ref" when autocompleting,
        # in case the user is typing something else
        if old_style and not prefix:
            return []

        completions = get_ref_completions(view)

        if prefix:
            lower_prefix = prefix.lower()
            completions = [c for c in completions if lower_prefix in c.lower()]

        if old_style:
            return completions, '{'
        else:
            return completions

    def get_completions(self, view, prefix, line):
        completions = get_ref_completions(view)

        if prefix:
            lower_prefix = prefix.lower()
            completions = [c for c in completions if lower_prefix in c.lower()]

        return completions

    def matches_line(self, line):
        return bool(
            (
                not line.startswith(',') or
                NEW_STYLE_REF_MULTIVALUE_REGEX.match(line)
            ) and (
                OLD_STYLE_REF_REGEX.match(line) or
                NEW_STYLE_REF_REGEX.match(line) or
                NEW_STYLE_REF_RANGE_REGEX.match(line)
            )
        )

    def matches_fancy_prefix(self, line):
        return bool(OLD_STYLE_REF_REGEX.match(line))

    def is_enabled(self):
        return get_setting('ref_auto_trigger', True)
