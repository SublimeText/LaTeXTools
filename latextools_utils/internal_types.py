try:
    from latextools_plugin_internal import LaTeXToolsPlugin
except ImportError:
    from LaTeXTools.latextools_plugin import LaTeXToolsPlugin


class FillAllHelper(LaTeXToolsPlugin):
    '''
    Interface for LatexFillAllCommand plugins
    '''

    def get_auto_completions(self, view, prefix, line):
        '''
        Gets the completions to display with Sublime's autocomplete

        Should return a list of completions or a tuple consisting of a list of
        completions and a single character to be inserted. This second option
        is to allow completing, e.g., \ref -> \ref{}

        :param view:
            The view the completions are requested for

        :param prefix:
            The current word the user has selected

        :param line:
            The contents of the first selected line, used by some plugins to
            determine the correct completions
        '''
        return []

    def get_completions(self, view, prefix, line):
        '''
        Gets the completions to display in the quick panel

        Should return a list of completions formatted to be displayed in the
        quick panel.

        :param view:
            The view the completions are requested for

        :param prefix:
            The current word the user has selected
            Note that if completions are entered using { , etc. this will be
            blank

        :param line:
            The contents of the first selected line, used by some plugins to
            determine the correct completions
        '''
        return None

    def matches_line(self, line):
        '''
        Checks if this plugin matches the current line

        :param line:
            The current line to check
        '''
        return False

    def get_supported_scope_selector(self):
        '''
        Returns the scope selector, in which the completion should be
        enabled. Default value is outside comments (- comment).
        Omit text.tex.latex, because it is always checked.
        '''
        return '- comment'

    # subclass may implement matches_fancy_prefix(self, line) to
    # support a fancy prefix, such as \cite_prefix, etc.

    def is_enabled(self):
        '''
        Checks whether this plugin should be used for triggered completions
        '''
        return False
