import os
import threading
import urllib.request

import sublime
import sublime_plugin


from Default.open_context_url import rex as url_regex

from .latextools_utils.settings import get_setting
from .latextools_utils.tex_directives import get_tex_root

template = """
\\begin{figure}
\\centering
\\includegraphics[$2]{<<image_name>>}
\\caption{$1}
\\label{fig:${1/([0-9a-zA-Z_])|([^0-9a-zA-Z_]+)/\\L\\1(?2:_:)/g}}
\\end{figure}
"""


class LatextoolsDownloadInsertImageHelperCommand(sublime_plugin.TextCommand):
    @staticmethod
    def _download(image_path, image_url, on_done=None):
        # create the folder
        os.makedirs(os.path.split(image_path)[0], exist_ok=True)
        # open the file
        with open(image_path, "wb") as out_file:
            # download and write the request
            with urllib.request.urlopen(image_url) as response:
                content = response.read()
                out_file.write(content)
                if on_done:
                    on_done()

    def run(self, edit, image_name, image_url, image_ext):
        view = self.view
        tex_root = get_tex_root(view)
        if not tex_root:
            return
        root_dir, _ = os.path.split(tex_root)
        image_path = os.path.normpath(os.path.join(root_dir, image_name))
        image_ext = "." + image_ext
        if not image_path.endswith(image_ext):
            image_path += image_ext

        pos = view.sel()[0].b + 1
        contents = template.replace("<<image_name>>", image_name)
        self.view.run_command("insert_snippet", {"contents": contents})

        pid = view.add_phantom(
            "lt-dl-img", sublime.Region(pos), "Downloading Image...",
            sublime.LAYOUT_BLOCK)

        def on_done():
            view.erase_phantom_by_id(pid)
        threading.Thread(
            target=self._download,
            args=(image_path, image_url, on_done)
        ).start()


def download_insert_image(window, view, image_url):
    if not get_tex_root(view):
        window.run_command("paste")
        sublime.status_message(
            "Need to save the view before downloading image.")
        return
    ext = image_url.split(".")[-1]
    caption = "Image name (.{})".format(ext)

    def on_cancel(text):
        window.run_command("paste")

    def on_done(text):
        kwargs = {
            "image_name": text,
            "image_url": image_url,
            "image_ext": ext
        }
        window.run_command("latextools_download_insert_image_helper", kwargs)

    window.show_input_panel(
        caption, "", on_done, on_change=lambda _: None,
        on_cancel=on_cancel)


class LatextoolsSmartPasteCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        view = window.active_view()
        clipboard = sublime.get_clipboard().strip()

        if (url_regex.match(clipboard) and
            any(clipboard.endswith(image_type)
                for image_type in get_setting("image_types"))):
            download_insert_image(window, view, clipboard)
        else:
            window.run_command("paste")
