from base_viewer import BaseViewer

from latextools_utils.external_command import external_command


class PreviewViewer(BaseViewer):

    def view_file(self, pdf_file, **kwargs):
        external_command(
            ['open', '-a', 'Preview', pdf_file], use_texpath=False
        )

    def supports_platform(self, platform):
        return platform == 'osx'
