from __future__ import print_function

import sublime
import sublime_plugin
import re

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

trigger_trim_cite = False
current_word = ''
after_current_word = ''


def get_current_word(view, point, type):

    line_prefix = view.substr(get_Region(view.line(point).a, point))[::-1]
    line_suffix = view.substr(get_Region(point, view.line(point).b))

    if type == 'cite':
            
        # prefix is the characters before caret
        prefix = re.match(r'([^{},]*)[\{,]', line_prefix).group(1)
        suffix, after_current_word = re.match(r'([^{},]*)([\},])', line_suffix).groups()

        return prefix[::-1], suffix, after_current_word

    if type != 'ref':
            
        # prefix is the characters before caret
        prefix = re.match(r'([^{}]*)\{', line_prefix).group(1)
        suffix = re.match(r'([^{}]*)\}', line_suffix).group(1)

        return prefix[::-1], suffix, ''
    

class LatexFillAllCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        global trigger_trim_cite
        global current_word
        
        view = self.view
        point = view.sel()[0].b

        # Current lines, used to detemine which situation
        line = view.substr(get_Region(view.line(point).a, point))[::-1]
        # if in cite envoriments
        if match(OLD_STYLE_CITE_REGEX, line) != None or match(NEW_STYLE_CITE_REGEX, line) != None:

            prefix, suffix, after_current_word = get_current_word(view, point, 'cite')

            # Current_word
            current_word = prefix + suffix 

            if current_word != '':
                if after_current_word == ',':
                    trigger_trim_cite = True
                # If the current word is not null, delte it!
                startpoint = point - len(prefix)
                endpoint = point + len(suffix)
                view.run_command('latex_tools_replace', {'a': startpoint, 'b': endpoint, 'replacement': ''})
                view.run_command('latex_cite')
            else:
                view.run_command('latex_cite')
            

        if match(OLD_STYLE_REF_REGEX, line) != None or match(NEW_STYLE_REF_REGEX, line) != None:
            
            prefix, suffix, after_current_word = get_current_word(view, point, 'ref')
            current_word = prefix + suffix
            if current_word != '':
                # If the current word is not null, delte it!
                startpoint = point - len(prefix)
                endpoint = point + len(suffix)
                view.run_command('latex_tools_replace', {'a': startpoint, 'b': endpoint, 'replacement': ''})
                view.run_command('latex_ref')
            else:
                view.run_command('latex_ref')

        if TEX_INPUT_FILE_REGEX.match(line) != None:

            prefix, suffix, after_current_word = get_current_word(view, point, 'input')
            current_word = prefix + suffix
            if current_word != '':
                startpoint = point - len(prefix)
                endpoint = point + len(suffix)
                view.run_command('latex_tools_replace', {'a': startpoint, 'b': endpoint, 'replacement': ''})
                view.run_command('latex_input_file')
            else:
                view.run_command("latex_input_file")

class OnLateFillAllReplacement(sublime_plugin.EventListener):


    # Process the extra and the end of the input by cite command,
    # when fill the citations between two commas.
    def on_selection_modified(self, view):
        
        global trigger_trim_cite

        # If selection is modifed by fill all commands
        if trigger_trim_cite:

            caret = view.sel()[0].b
            last_char = view.substr(get_Region(caret-1, caret))
            if last_char == '}':
                trigger_trim_cite = False
                view.run_command('latex_tools_replace', {'a': caret-1, 'b': caret, 'replacement': ''})
