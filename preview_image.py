import os
import shutil
import subprocess
import threading
import time
import types

import sublime
import sublime_plugin

_ST3 = sublime.version() >= "3000"
if _ST3:
    from .getTeXRoot import get_tex_root
    from .jumpto_tex_file import open_image, find_image
    from .latextools_utils import cache, get_setting

_HAS_IMG_POPUP = sublime.version() >= "3114"
_HAS_HOVER = sublime.version() >= "3116"

_HAS_CONVERT = shutil.which("convert") is not None

# the path to the temp files (set on loading)
temp_path = None

# we use png files for the html popup
_IMAGE_EXTENSION = ".png"

_lt_settings = {}


startupinfo = None
if sublime.platform() == "windows":
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


def plugin_loaded():
    global _lt_settings, temp_path
    _lt_settings = sublime.load_settings("LaTeXTools.sublime-settings")

    temp_path = os.path.join(cache._global_cache_path(), "preview_image")
    # validate the temporary file directory is available
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)


def _call_shell_command(command):
    """Call the command with shell=True and wait for it to finish."""
    subprocess.Popen(command,
                     shell=True,
                     startupinfo=startupinfo).wait()


def create_thumbnail(image_path, thumbnail_path, max_size=300):
    # convert the image
    # max_size = 300
    if os.path.exists(thumbnail_path):
        return
    _call_shell_command(
        'convert -thumbnail {max_size}x{max_size} '
        '"{image_path}" "{thumbnail_path}"'
        .format(**locals())
    )


_max_threads = 2
_job_list_lock = threading.Lock()
_job_list = []
_working_set = set()
_thread_num_lock = threading.Lock()
_thread_num = 0


def _convert_image_thread(thread_id):
    print("start convert thread", thread_id, threading.get_ident())
    while True:
        try:
            with _job_list_lock:
                next_job = _job_list.pop()
                if next_job[1] in _working_set:
                    _job_list.append(next_job)
                    for i in range(len(_job_list)):
                        next_job = _job_list[i]
                        if next_job[1] not in _working_set:
                            del _job_list[i]
                            break
                    else:
                        print("Already working on", next_job[1])
                        raise StopIteration()
                job = next_job[0]
                _working_set.add(next_job[1])
            job()
            with _job_list_lock:
                _working_set.remove(next_job[1])
        except IndexError:
            break
        except StopIteration:
            break
        except Exception as e:
            print("Exception:", e)
            break
        if thread_id >= _max_threads:
            break
    print("close convert thread", thread_id, threading.get_ident())

    # decrease the number of threads -> delete this thread
    global _thread_num
    with _thread_num_lock:
        _thread_num -= 1


def _append_image_job(image_path, thumbnail_path, cont, max_size=300):
    global _job_list
    if not _HAS_CONVERT:
        return

    def job():
        print("job:", image_path)
        before = time.time()
        create_thumbnail(image_path, thumbnail_path)
        cont()
        print("duration:", time.time() - before)

    with _job_list_lock:
        _job_list.append((job, thumbnail_path, image_path))


def _run_image_jobs():
    global _thread_num
    thread_id = -1

    # we may not need locks for this
    with _job_list_lock:
        rem_len = len(_job_list)
    with _thread_num_lock:
        before_num = _thread_num
        after_num = min(_max_threads, rem_len)
        start_threads = after_num - before_num
        if start_threads > 0:
            _thread_num += start_threads
    print("before_num, after_num:", before_num, after_num)
    print("_job_list:", _job_list)
    for thread_id in range(before_num, after_num):
        threading.Thread(target=_convert_image_thread,
                         args=(thread_id,)).start()


def open_image_folder(image_path):

    # TODO open folder for other platforms
    # if sublime.platform() == "windows":
    #     os.startfile(folder_path)

    # if sublime.platform() == 'windows':
    #     subprocess.Popen(["explorer", '/select,', image_path])
    # else:
    folder_path, image_name = os.path.split(image_path)
    sublime.active_window().run_command(
        "open_dir", {"dir": folder_path, "file": image_name})


def _get_thumbnail_path(image_path):
    if image_path is None:
        return None
    _, ext = os.path.splitext(image_path)
    if ext in [".png", ".jpg", ".jpeg", ".gif"]:
        thumbnail_path = image_path
    else:
        thumbnail_path = os.path.join(
            temp_path, cache.hash_digest(image_path) + _IMAGE_EXTENSION)
    return thumbnail_path


def _get_popup_html(thumbnail_path):
    if os.path.exists(thumbnail_path):
        img_tag = (
            '<img src="file://{thumbnail_path}"'
            ' width="150%" '
            'height="150%">'
            # '>'
            .format(**locals())
        )
    elif not _HAS_CONVERT:
        img_tag = "Install ImageMagick to enable preview."
    else:
        img_tag = "Preparing image for preview..."
    html_content = """
    <body id="latextools-preview-image-popup">
    <div>{img_tag}</div>
    <div>
        <a href="open_image">(Open image)</a>
        <a href="open_folder">(Open folder)</a>
    </div>
    </body>
    """.format(**locals())
    return html_content


class PreviewImageHoverListener(sublime_plugin.EventListener):
    def on_hover(self, view, point, hover_zone):
        if hover_zone != sublime.HOVER_TEXT:
            return
        if not view.score_selector(
                point, "meta.function.includegraphics.latex"):
            return
        mode = get_setting("preview_image_mode", view=view)
        if mode != "hover":
            return
        containing_scopes = view.find_by_selector(
            "meta.function.includegraphics.latex")
        try:
            containing_scope = next(
                c for c in containing_scopes if c.contains(point))
        except StopIteration:
            print("Not inside an image scope.")
            return
        image_scopes = view.find_by_selector(
            "meta.function.includegraphics.latex meta.group.brace.latex")
        try:
            image_scope = next(
                i for i in image_scopes if containing_scope.contains(i))
        except StopIteration:
            print("No file name scope found.")
            return

        file_name = view.substr(image_scope)[1:-1]
        location = containing_scope.begin() + 1

        tex_root = get_tex_root(view)
        if not tex_root:
            view.show_popup(
                "Save your file to show an image preview.",
                location=location, flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY)
            return
        image_path = find_image(tex_root, file_name)
        if not image_path:
            # image does not exists
            view.show_popup(
                "Image not found.", location=location,
                flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY)
            return

        thumbnail_path = _get_thumbnail_path(image_path)

        html_content = _get_popup_html(thumbnail_path)

        def on_navigate(href):
            if href == "open_image":
                open_image(view.window(), image_path)
            elif href == "open_folder":
                open_image_folder(image_path)

        def on_hide():
            on_hide.hidden = True
        on_hide.hidden = False

        view.show_popup(
            html_content, location=location,
            flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY, on_navigate=on_navigate,
            on_hide=on_hide)

        # if the thumbnail does not exists, create it and update the popup
        if _HAS_CONVERT and not os.path.exists(thumbnail_path):
            def update_popup():
                html_content = _get_popup_html(thumbnail_path)
                if on_hide.hidden:
                    return
                view.show_popup(
                    html_content, location=location,
                    flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                    on_navigate=on_navigate)

            _append_image_job(image_path, thumbnail_path, cont=update_popup)
            _run_image_jobs()


class PreviewImagePhantomListener(sublime_plugin.ViewEventListener):
    key = "preview_image"

    def __init__(self, view):
        self.view = view
        self.phantoms = []
        self._selection_modifications = 0

        self._phantom_lock = threading.Lock()

        self.visible_mode = get_setting("preview_image_mode", view=view)

        view.erase_phantoms(self.key)
        # self.update_phantoms()
        sublime.set_timeout_async(self.update_phantoms)

    @classmethod
    def is_applicable(cls, settings):
        syntax = settings.get('syntax')
        return syntax == 'Packages/LaTeX/LaTeX.sublime-syntax'

    @classmethod
    def applies_to_primary_view_only(cls):
        return True

    #######################
    # MODIFICATION LISTENER
    #######################

    def on_after_selection_modified_async(self):
        self.update_phantoms()

    def _validate_after_selection_modified(self):
        self._selection_modifications -= 1
        if self._selection_modifications == 0:
            sublime.set_timeout_async(self.on_after_selection_modified_async)

    def on_selection_modified(self):
        self._selection_modifications += 1
        sublime.set_timeout(self._validate_after_selection_modified, 600)

    #########
    # METHODS
    #########

    def _update_phantom_regions(self):
        regions = self.view.query_phantoms([p.id for p in self.phantoms])
        for i in range(len(regions)):
            self.phantoms[i].region = regions[i]

    def _create_html_content(self, p):
        iden = str(p.id)
        if p.thumbnail_path is None:
            html_content = """Image not found!"""
        elif p.hidden:
            html_content = """
            <div>
                <a href="show {p.index}">(Show)</a>
            </div>
            """.format(**locals())
        else:
            html_content = """
            <div>
                <a href="show {p.index}">(Show)</a>
                <a href="hide {p.index}">(Hide)</a>
                <a href="open_image {p.index}">(Open image)</a>
                <a href="open_folder {p.index}">(Open folder)</a>
            </div>
            """.format(**locals())
            if not os.path.exists(p.thumbnail_path):
                html_content += """No preview for this extension available!"""
            else:
                html_content += """
                <div>
                <img src="file://{p.thumbnail_path}" width="100%"
                 height="100%">
                </div>
                """.format(**locals())
        html_content = """
        <body id="latextools-preview-image-phantom">
            {html_content}
        </body>
        """.format(html_content=html_content)
        return html_content

    def on_navigate(self, href):
        print("href:", href)
        command, index = href.split(" ")
        index = int(index)
        print("command, index:", command, index)
        p = self.phantoms[index]
        if command == "hide":
            p.hidden = True
            p.region = self.view.query_phantom(p.id)[0]
            self._update_phantom(p)
        elif command == "show":
            p.hidden = False
            p.region = self.view.query_phantom(p.id)[0]
            self._update_phantom(p)
        elif command == "open_image":
            open_image(self.view.window(), p.image_path)
        elif command == "open_folder":
            open_image_folder(p.image_path)

    def update_phantom(self, p):
        with self._phantom_lock:
            self._update_phantom(p)

    def _update_phantom(self, p):
        view = self.view
        if p.id is not None:
            p.region = self.view.query_phantom(p.id)[0]
            view.erase_phantom_by_id(p.id)
        if p.region == sublime.Region(-1):
            return
        html_content = self._create_html_content(p)
        layout = sublime.LAYOUT_BLOCK
        p.id = view.add_phantom(
            self.key, p.region, html_content, layout,
            on_navigate=self.on_navigate)

    def update_phantoms(self):
        with self._phantom_lock:
            self._update_phantoms()

    def _update_phantoms(self):
        view = self.view
        tex_root = get_tex_root(view)
        if not tex_root:
            return

        if self.visible_mode == "all":
            scopes = view.find_by_selector(
                "meta.function.includegraphics.latex meta.group.brace.latex")
        elif self.visible_mode == "selected":
            graphic_scopes = view.find_by_selector(
                "meta.function.includegraphics.latex")
            selected_scopes = [
                scope for scope in graphic_scopes
                if any(scope.contains(sel) for sel in view.sel())
            ]
            if selected_scopes:
                content_scopes = view.find_by_selector(
                    "meta.function.includegraphics.latex "
                    "meta.group.brace.latex")
                scopes = [
                    s for s in content_scopes
                    if any(scope.contains(s) for scope in selected_scopes)
                ]
            else:
                scopes = []
        else:
            if not self.phantoms:
                return
            scopes = []

        new_phantoms = []
        need_thumbnails = []

        self._update_phantom_regions()

        for scope in scopes:
            file_name = view.substr(scope)[1:-1]
            image_path = find_image(tex_root, file_name)

            thumbnail_path = _get_thumbnail_path(image_path)

            region = sublime.Region(scope.end())

            try:
                p = next(
                    x for x in self.phantoms
                    if x.region == region and x.file_name == file_name)
                new_phantoms.append(p)
                # self._update_phantom(p)
                continue
            except StopIteration:
                pass
            p = types.SimpleNamespace(
                id=None,
                index=len(new_phantoms),
                region=region,
                file_name=file_name,
                hidden=False,
                image_path=image_path,
                thumbnail_path=thumbnail_path
            )

            self._update_phantom(p)

            if p.thumbnail_path and not os.path.exists(p.thumbnail_path):
                need_thumbnails.append(p)

            new_phantoms.append(p)

        delete_phantoms = [x for x in self.phantoms
                           if x not in new_phantoms]
        for p in delete_phantoms:
            if p.region != sublime.Region(-1):
                view.erase_phantom_by_id(p.id)

        self.phantoms = new_phantoms

        if _HAS_CONVERT:
            for p in need_thumbnails:
                _append_image_job(p.image_path, p.thumbnail_path,
                                  cont=lambda: self.update_phantom(p))
            if need_thumbnails:
                _run_image_jobs()
