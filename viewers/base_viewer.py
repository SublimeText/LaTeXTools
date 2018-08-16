import latextools_plugin
import sys

import latextools_utils.sublime_utils as st_utils

# most methods take a kwargs variable, which currently only consists of the
# `keep_focus` setting


class BaseViewer(latextools_plugin.LaTeXToolsPlugin):

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        '''
        command to jump to the file at a specified line and column

        if this raises a NotImplementedError, we will fallback to
        invoking view_file

        :params:
            pdf_file - full path to the generated pdf
            tex_file - full path to the tex file of the active view
            line - indicates the line number in the tex file (1-based)
            col - incidates the column number in the tex file (1-based)
            **kwargs:
                keep_focus - if true, focus should return to ST
        '''
        raise NotImplementedError()

    def view_file(self, pdf_file, **kwargs):
        '''
        command to open a file

        :params:
            pdf_file - full path to the generated pdf
        '''
        raise NotImplementedError()

    def supports_keep_focus(self):
        '''
        return True to indicate that this plugin supports the keep_focus
        setting or False (the default) to use the default refocus
        implementation
        '''
        return False

    def supports_platform(self, platform):
        '''
        return True to indicate that this plugin supports the reported
        platform or False to indicate that it is not supported in the
        current platform / environment
        '''
        return True

    def focus_st(self):
        st_utils.focus_st()


latextools_plugin.add_whitelist_module(
    'base_viewer', sys.modules[BaseViewer.__module__]
)
