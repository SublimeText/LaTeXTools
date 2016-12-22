from base_viewer import BaseViewer

from latextools_utils import get_setting
from latextools_utils.external_command import external_command
from latextools_utils.sublime_utils import get_sublime_exe

import os
import re
import shlex
import sublime
import string
import sys

try:
    from shlex import quote
except ImportError:
    from pipes import quote

if sys.version_info >= (3, 0):
    PY2 = False
    strbase = str
else:
    PY2 = True
    strbase = basestring


WINDOWS_SHELL = re.compile(r'\b(?:cmd|powershell)(?:.exe)?\b', re.UNICODE)


# a viewer that runs a user-specified command
class CommandViewer(BaseViewer):

    CONTAINS_VARIABLE = re.compile(
        r'\$(?:(?:pdf|src)_file(?:_(?:name|ext|base_name|path))?'
        r'|sublime_binary|src_file_rel_path|line|col)\b',
        re.IGNORECASE | re.UNICODE
    )

    def _replace_vars(self, s, pdf_file, tex_file=None, line='', col=''):
        '''
        Function to substitute various values into a user-provided string

        Returns a tuple consisting of the string with any substitutions made
        and a boolean indicating if any substitutions were made

        Provided Values:
        --------------------|-----------------------------------------------|
        $pdf_file           | full path of PDF file
        $pdf_file_name      | name of the PDF file
        $pdf_file_ext       | extension of the PDF file
        $pdf_file_base_name | name of the PDF file without the extension
        $pdf_file_path      | full path to directory containing PDF file
        $sublime_binary     | full path to the Sublime binary

        Forward Sync Only:
        --------------------|-----------------------------------------------|
        $src_file           | full path of the tex file
        $src_file_name      | name of the tex file
        $src_file_ext       | extension of the tex file
        $src_file_base_name | name of the tex file without the extension
        $src_file_path      | full path to directory containing tex file
        $line               | line to sync to
        $col                | column to sync to
        '''
        # only do the rest if we must
        if not self.CONTAINS_VARIABLE.search(s):
            return(s, False)

        sublime_binary = get_sublime_exe() or ''

        pdf_file_path = os.path.split(pdf_file)[0]
        pdf_file_name = os.path.basename(pdf_file)
        pdf_file_base_name, pdf_file_ext = os.path.splitext(pdf_file_name)

        if tex_file is None:
            src_file = ''
            src_file_path = ''
            src_file_name = ''
            src_file_ext = ''
            src_file_base_name = ''
        else:
            if os.path.isabs(tex_file):
                src_file = tex_file
            else:
                src_file = os.path.normpath(
                    os.path.join(
                        pdf_file_path,
                        tex_file
                    )
                )

            src_file_path = os.path.split(src_file)[0]
            src_file_name = os.path.basename(src_file)
            src_file_base_name, src_file_ext = os.path.splitext(src_file_name)

        template = string.Template(s)
        return (template.safe_substitute(
            pdf_file=pdf_file,
            pdf_file_path=pdf_file_path,
            pdf_file_name=pdf_file_name,
            pdf_file_ext=pdf_file_ext,
            pdf_file_base_name=pdf_file_base_name,
            sublime_binary=sublime_binary,
            src_file=src_file,
            src_file_path=src_file_path,
            src_file_name=src_file_name,
            src_file_ext=src_file_ext,
            src_file_base_name=src_file_base_name,
            line=line,
            col=col
        ), True)

    def _run_command(self, command, pdf_file, tex_file=None, line='', col=''):
        if isinstance(command, strbase):
            if PY2:
                command = str(command)

            command = shlex.split(command)

            if PY2:
                command = [unicode(c) for c in command]

        substitution_made = False
        for i, component in enumerate(command):
            command[i], replaced = self._replace_vars(
                component, pdf_file, tex_file, line, col)
            substitution_made = substitution_made or replaced

        if not replaced:
            command.append(pdf_file)

        external_command(
            command,
            cwd=os.path.split(pdf_file)[0],
            # show the Window if not using a Windows shell, i.e., powershell or
            # cmd
            show_window=not bool(WINDOWS_SHELL.match(command[0]))
            if sublime.platform() == 'windows' else False
        )

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        command = get_setting('viewer_settings', {}).\
            get(sublime.platform(), {}).get('forward_sync_command')

        if command is None:
            self.view_file(pdf_file)
            return

        self._run_command(command, pdf_file, tex_file, line, col)

    def view_file(self, pdf_file, **kwargs):
        command = get_setting('viewer_settings', {}).\
            get(sublime.platform(), {}).get('view_command')

        if command is None:
            sublime.error_message(
                'You must set the command setting in viewer_settings before '
                'using the viewer.'
            )
            return

        self._run_command(command, pdf_file)
