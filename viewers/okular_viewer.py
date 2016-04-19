from base_viewer import BaseViewer

import subprocess


class OkularViewer(BaseViewer):

    def _run_with_locator(self, locator, **kwargs):
        keep_focus = kwargs.pop('keep_focus', True)
        command = ['okular', '--unique']
        if keep_focus:
            command.append('--noraise')
        command.append(locator)

        subprocess.Popen(command)

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        self._run_with_locator(
            '{pdf_file}#src:{line}{tex_file}'.format(**locals()),
            **kwargs
        )

    def view_file(self, pdf_file, **kwargs):
        self._run_with_locator(
            pdf_file,
            **kwargs
        )

    def supports_keep_focus(self):
        return True

    def supports_platform(self, platform):
        return platform == 'linux'
