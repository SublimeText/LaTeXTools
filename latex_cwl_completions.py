import sublime
import sublime_plugin
import os
import re

index = 0

if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
    from latex_cite_completions import OLD_STYLE_CITE_REGEX, NEW_STYLE_CITE_REGEX, match
    from latex_ref_completions import OLD_STYLE_REF_REGEX, NEW_STYLE_REF_REGEX
    from latex_input_completions import TEX_INPUT_FILE_REGEX
    from latexFoldSection import get_Region
else:
    _ST3 = True
    from .latex_cite_completions import OLD_STYLE_CITE_REGEX, NEW_STYLE_CITE_REGEX, match
    from .latex_ref_completions import OLD_STYLE_REF_REGEX, NEW_STYLE_REF_REGEX
    from .latex_input_completions import TEX_INPUT_FILE_REGEX
    from .latexFoldSection import get_Region

# Do not do completions in this envrioments
env_donot_compl = [TEX_INPUT_FILE_REGEX, OLD_STYLE_CITE_REGEX, NEW_STYLE_CITE_REGEX, OLD_STYLE_REF_REGEX, NEW_STYLE_REF_REGEX]

class LatexCwlCompletion(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        
        settings = sublime.load_settings("LaTeXTools.sublime-settings")
        cwl_completion = settings.get('cwl_completion')
        if cwl_completion == None or cwl_completion == False:
            return []

        point = locations[0]
        if not view.score_selector(point, "text.tex.latex"):
            return []

        point = locations[0]
        line = view.substr(get_Region(view.line(point).a, point))
        line = line[::-1]

        # Do not do completions in actions
        for rex in env_donot_compl:
            if match(rex, line) != None:
                print(match(rex,line))
                return []

        completions = parse_cwl_file()
        return (completions, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)


def parse_cwl_file():

    CLW_COMMENT = re.compile(r'#[^#]*')
    # Get cwl file list
    cwl_path = sublime.packages_path() + "/LaTeX-cwl"
    settings = sublime.load_settings("LaTeXTools.sublime-settings")
    cwl_file_list = settings.get('cwl_list')

    
    # Configurations of cwl_list do not exists!
    if cwl_file_list == None:
        return []
    
    # Generating cwl_file_list with absolute path
    cwl_files = [os.path.normpath(
        '{}/{}'.format(cwl_path, x)) for x in cwl_file_list]

    completions = []
    for cwl in cwl_files:
        # Process cwl files
        with open(cwl, 'r') as f:
            for line in f:
                if CLW_COMMENT.match(line.strip()):
                    pass
                else:
                    keyword = line.strip()
                    method = os.path.splitext(os.path.basename(cwl))[0]
                    item = ('{}\t{}'.format(keyword, method), parse_keyword(keyword))
                    completions.append(item)
    return completions


def parse_keyword(keyword):
    
    # Replace strings in [] and {} with snippet syntax

    def replace_braces(matchobj):
        global index
        index += 1
        if matchobj.group(1) != None:
            word = matchobj.group(1)
            return '{{${{{}:{}}}}}'.format(index, word)
        else:
            word = matchobj.group(2)
            return '[${{{}:{}}}]'.format(index, word)
        

    replace, n = re.subn(r'\{([^\{\}\[\]]*)\}|\[([^\{\}\[\]]*)\]', replace_braces, keyword[1:])
    
    # I do not understand why some of the input will eat the '\' charactor before it!
    # This code is to avoid these things.
    if n == 0 and re.search(r'^[a-zA-Z]+$', keyword[1:].strip()) != None:
            return keyword
    else:
        return replace
