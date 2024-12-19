import os
import shutil
import threading
import urllib.request

import sublime
import sublime_plugin


from Default.open_context_url import rex as url_regex

from .latextools_utils import analysis
from .latextools_utils.settings import get_setting
from .latextools_utils.tex_directives import get_tex_root


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

    @staticmethod
    def _copy(new_image_path, old_image_path, on_done=None):
        # create the folder
        os.makedirs(os.path.split(new_image_path)[0], exist_ok=True)
        shutil.copy2(old_image_path, new_image_path)
        if on_done:
            on_done()

    def run(self, edit, image_name, image_url, image_ext, offline):
        view = self.view
        tex_root = get_tex_root(view)
        if not tex_root:
            return
        ana = analysis.get_analysis(tex_root)
        graphics_paths = ana.graphics_paths()
        if graphics_paths:
            base_dir = graphics_paths[0]
        else:
            base_dir = ana.tex_base_path(view.file_name())
        if os.path.isabs(image_name):
            image_path = image_name
        else:
            image_path = os.path.join(base_dir, image_name)
        image_path = os.path.normpath(image_path)
        image_ext = "." + image_ext
        if not image_path.endswith(image_ext):
            image_path += image_ext

        if os.path.exists(image_path):
            ok = sublime.ok_cancel_dialog(
                "Target image does already exist. Overwrite?",
                "Overwrite!")
            if not ok:
                return

        pos = view.sel()[0].b + 1
        contents = _create_image_snippet(image_name)
        self.view.run_command("insert_snippet", {"contents": contents})

        if offline:
            # if it is offline just copy the file non-blocking
            threading.Thread(
                target=self._copy,
                args=(image_path, image_url)
            ).start()
        else:
            # if the image is online also show a phantom to notify the
            # download
            pid = view.add_phantom(
                "lt-dl-img", sublime.Region(pos), "Downloading Image...",
                sublime.LAYOUT_BLOCK)

            def on_done():
                view.erase_phantom_by_id(pid)

            threading.Thread(
                target=self._download,
                args=(image_path, image_url, on_done)
            ).start()


def _create_image_snippet(image_name):
    template = "\n".join(get_setting("smart_paste_image_snippet", []))
    contents = template.replace("<<image_name>>", image_name)
    return contents


def _download_insert_image(window, view, image_url, offline=False):
    tex_root = get_tex_root(view)
    if not tex_root:
        window.run_command("paste")
        sublime.status_message(
            "Need to save the view before downloading image.")
        return
    ext = image_url.split(".")[-1]
    caption = "Include graphics path (.{})".format(ext)

    def on_cancel():
        window.run_command("paste")

    def on_done(text):
        kwargs = {
            "image_name": text,
            "image_url": image_url,
            "image_ext": ext,
            "offline": offline,
        }
        window.run_command("latextools_download_insert_image_helper", kwargs)

    # if the image is offline check whether it is in a subdirectory
    # of the root folder or the graphics path. If so just include it directly
    if offline:
        ana = analysis.get_analysis(tex_root)
        graphics_paths = ana.graphics_paths()
        image_dir = os.path.normpath(os.path.split(image_url)[0])
        if not graphics_paths:
            graphics_paths = [ana.tex_base_path(view.file_name())]
        for graphics_path in graphics_paths:
            if image_dir.startswith(graphics_path):
                image_name = os.path.relpath(image_url, graphics_path)
                image_name = image_name.replace("\\", "/")
                contents = _create_image_snippet(image_name)
                view.run_command("insert_snippet", {"contents": contents})
                return

    example_name = ""
    if not offline:
        example_name = image_url.split("/")[-1]
    else:
        _, example_name = os.path.split(image_url)

    window.show_input_panel(
        caption, example_name, on_done, on_change=lambda _: None,
        on_cancel=on_cancel)
    window.run_command("select_all")


def _is_possible_image_path(text):
    return any(
        text.endswith("." + image_type)
        for image_type in get_setting("image_types")
    )


class LatextoolsSmartPasteCommand(sublime_plugin.WindowCommand):
    def is_visible(self, *args):
        view = self.window.active_view()
        return bool(view.score_selector(0, "text.tex.latex"))

    def run(self):
        window = self.window
        view = window.active_view()
        clipboard = sublime.get_clipboard()

        content = clipboard.strip()
        if sublime.platform() == "windows":
            content = content.strip('"')

        is_empty_line = all(
            not view.substr(view.line(sel.b)).strip()
            for sel in view.sel())
        maybe_image = _is_possible_image_path(content)

        if is_empty_line and maybe_image and url_regex.match(content):
            _download_insert_image(window, view, content)
        elif is_empty_line and maybe_image and os.path.isfile(content):
            _download_insert_image(window, view, content, offline=True)
        else:
            window.run_command("paste")
