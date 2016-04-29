from base_viewer import BaseViewer

import os
import subprocess


class SkimViewer(BaseViewer):

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        keep_focus = kwargs.pop('keep_focus', True)
        path_to_skim = '/Applications/Skim.app'

        if not os.path.exists(path_to_skim):
            path_to_skim = subprocess.check_output([
                'osascript',
                '-e',
                'POSIX path of (path to app id "net.sourceforge.skim-app.skim")'
            ]).decode("utf8")[:-1]

        command = [
            os.path.join(
                path_to_skim,
                'Contents',
                'SharedSupport',
                'displayline'
            ),
            '-r'
        ]

        if keep_focus:
            command.append('-g')

        command += [
            str(line), pdf_file, tex_file
        ]

        subprocess.Popen(command)

    def view_file(self, pdf_file, **kwargs):
        keep_focus = kwargs.pop('keep_focus', True)

        command = [
            '/bin/sh',
            os.path.normpath(
                os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    'skim',
                    'displayfile'
                )
            ),
            '-r'
        ]

        if keep_focus:
            command.append('-g')

        command.append(pdf_file)

        subprocess.Popen(command)

    def supports_keep_focus(self):
        return True

    def supports_platform(self, platform):
        return platform == 'osx'
