from ...latextools.utils.external_command import external_command

from .base_viewer import BaseViewer

__all__ = ["PreviewViewer"]


class PreviewViewer(BaseViewer):

    @classmethod
    def view_file(cls, pdf_file, **kwargs):
        keep_focus = kwargs.pop("keep_focus", True)

        command = ["open"]
        if keep_focus:
            command.append("-g")

        command += ["-a", "Preview", pdf_file]

        external_command(command, use_texpath=False)

    @classmethod
    def supports_platform(cls, platform):
        return platform == "osx"

    @classmethod
    def supports_keep_focus(cls):
        return True
