from base_viewer import BaseViewer

import subprocess


class PreviewViewer(BaseViewer):
    def view_file(self, pdf_file, **kwargs):
        subprocess.Popen(['open', '-a', 'Preview', pdf_file])

    def supports_platform(self, platform):
        return platform == 'osx'
