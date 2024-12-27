from base_viewer import BaseViewer

from latextools_utils.external_command import external_command


class PreviewViewer(BaseViewer):

    def view_file(self, pdf_file, **kwargs):
        keep_focus = kwargs.pop('keep_focus', True)

        command = ['open']
        if keep_focus:
            command.append('-g')

        command += ['-a', 'Preview', pdf_file]

        external_command(command, use_texpath=False)

    def supports_platform(self, platform):
        return platform == 'osx'

    def supports_keep_focus(self):
        return True
