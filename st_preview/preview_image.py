import imghdr
import inspect
import os
import struct
import threading
import types

import sublime
import sublime_plugin


from ..getTeXRoot import get_tex_root
from ..jumpto_tex_file import open_image, find_image
from ..latextools_utils import cache, get_setting
from . import preview_utils
from .preview_utils import (
    convert_installed, run_convert_command, ghostscript_installed,
    run_ghostscript_command
)
from . import preview_threading as pv_threading

# export the listeners
exports = ["PreviewImageHoverListener", "PreviewImagePhantomListener"]

# the path to the temp files (set on loading)
temp_path = None

# we use png files for the html popup
_IMAGE_EXTENSION = ".png"
# we add this extension to log error information
_ERROR_EXTENSION = ".err"

_lt_settings = {}

# the name is used as identifier and to extract folder and file names
_name = "preview_image"


def _on_setting_change():
    max_threads = get_setting(
        "preview_max_convert_threads", default=None, view={})
    if max_threads is not None:
        pv_threading.set_max_threads(max_threads)


def plugin_loaded():
    global _lt_settings, temp_path
    _lt_settings = sublime.load_settings("LaTeXTools.sublime-settings")

    temp_path = os.path.join(cache._global_cache_path(), _name)
    # validate the temporary file directory is available
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    # init all variables
    _on_setting_change()
    # add a callback to setting changes
    _lt_settings.add_on_change("lt_preview_image_main", _on_setting_change)

    # register the temp folder for auto deletion
    pv_threading.register_temp_folder(_name, temp_path)


def plugin_unloaded():
    _lt_settings.clear_on_change("lt_preview_image_main")


_GS_EXTS = set(['ps', 'eps', 'pdf'])


def _uses_gs(file):
    file, ext = os.path.splitext(file)
    return ext.lower() in _GS_EXTS


def _can_create_preview(file=None):
    if file is None:
        return ghostscript_installed() or convert_installed()
    else:
        if _uses_gs(file):
            return ghostscript_installed()
        else:
            return convert_installed()


def create_thumbnail(image_path, thumbnail_path, width, height):
    # convert the image
    if os.path.exists(thumbnail_path):
        return

    if _uses_gs(image_path):
        run_ghostscript_command([
            '-sDEVICE=pngalpha', '-dLastPage=1',
            '-sOutputFile={thumbnail_path}'.format(**locals()),
            '-g{width}x{height}'.format(**locals())
        ])
    else:
        run_convert_command([
            '-thumbnail', '{width}x{height}'.format(**locals()),
            image_path, thumbnail_path
        ])

    if not os.path.exists(thumbnail_path):
        with open(thumbnail_path + _ERROR_EXTENSION, "w") as f:
            f.write("Failed to create preview thumbnail.")


# CONVERT THREADING
def _append_image_job(image_path, thumbnail_path, width, height, cont):
    global _job_list
    if not _can_create_preview(image_path):
        return

    def job():
        create_thumbnail(image_path, thumbnail_path, width, height)
        cont()

    _, job_id = os.path.split(thumbnail_path)
    pv_threading.append_job(_name, jid=job_id, job=job)


def _run_image_jobs():
    if not pv_threading.has_function(_name):
        pv_threading.register_function(_name, lambda job: job())
    pv_threading.run_jobs(_name)


# see https://bugs.python.org/issue16512#msg198034
# not added to imghdr.tests because of potential issues with reloads
def _is_jpg(h):
    return h.startswith(b'\xff\xd8')


# from http://stackoverflow.com/a/20380514/5963435
# somewhat enhanced from http://stackoverflow.com/a/39778771
def get_image_size(image_path):
    '''Determine the image type of image_path and return its size.
    from draco'''
    with open(image_path, 'rb') as fhandle:
        # read 32 as we pass this to imghdr
        head = fhandle.read(32)
        if len(head) != 32:
            return
        what = imghdr.what(image_path, head)
        if what == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif what == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif what == 'jpeg' or _is_jpg(head):
            try:
                fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf or ftype in (0xc4, 0xc8, 0xcc):
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception:  # IGNORE:W0703
                return
        else:
            return
        return width, height


def _adapt_image_size(thumbnail_path, width, height):
    try:
        w, h = get_image_size(thumbnail_path)
        width_ration = float(width) / w
        height_ratio = float(height) / h
        if height_ratio > width_ration:
            height = int(height * width_ration / height_ratio)
        elif width_ration > height_ratio:
            width = int(width * height_ratio / width_ration)
    except TypeError:
        pass
    return width, height


def open_image_folder(image_path):
    folder_path, image_name = os.path.split(image_path)
    sublime.active_window().run_command(
        "open_dir", {"dir": folder_path, "file": image_name})


def _validate_thumbnail_currentness(image_path, thumbnail_path):
    """Remove the thumbnail if it is outdated"""
    if not os.path.exists(thumbnail_path) or image_path == thumbnail_path:
        return
    try:
        if os.path.getmtime(image_path) > os.path.getmtime(thumbnail_path):
            os.remove(thumbnail_path)
    except:
        pass


def _get_thumbnail_path(image_path, width, height):
    """Get the path to the the thumbnail"""
    if image_path is None:
        return None
    _, ext = os.path.splitext(image_path)
    if ext in [".png", ".jpg", ".jpeg", ".gif"]:
        thumbnail_path = image_path
    else:
        fingerprint = cache.hash_digest(
            "{width}x{height}\n{image_path}"
            .format(**locals()),
        )
        thumbnail_path = os.path.join(
            temp_path, fingerprint + _IMAGE_EXTENSION)

        # remove the thumbnail if it is outdated
        _validate_thumbnail_currentness(image_path, thumbnail_path)
    return thumbnail_path


def _get_popup_html(image_path, thumbnail_path, width, height):
    if os.path.exists(thumbnail_path):
        # adapt the size to keep the width/height ratio, but stay inside
        # the image dimensions
        width, height = _adapt_image_size(thumbnail_path, width, height)
        img_tag = (
            '<img src="file://{thumbnail_path}"'
            ' width="{width}" '
            'height="{height}">'
            .format(**locals())
        )
    elif _uses_gs(image_path) and not ghostscript_installed():
        img_tag = "Install Ghostscript to enable preview."
    elif not _uses_gs(image_path) and not convert_installed():
        img_tag = "Install ImageMagick to enable preview."
    elif os.path.exists(thumbnail_path + _ERROR_EXTENSION):
        img_tag = "ERROR: Failed to create preview thumbnail."
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
        if view.is_popup_visible():
            # don't let the popup blink
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

        file_name = view.substr(image_scope)[1:-1].strip()
        location = containing_scope.begin() + 1

        tex_root = get_tex_root(view)
        if not tex_root:
            view.show_popup(
                "Save your file to show an image preview.",
                location=location, flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY)
            return
        image_path = find_image(
            tex_root, file_name, tex_file_name=view.file_name())
        if not image_path:
            # image does not exists
            view.show_popup(
                "Image not found.", location=location,
                flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY)
            return

        size = get_setting("preview_popup_image_size", view=view)
        if isinstance(size, list):
            width, height = size
        else:
            width = height = size

        scale = get_setting("preview_image_scale_quotient", view=view)

        tn_width, tn_height = scale * width, scale * height
        thumbnail_path = _get_thumbnail_path(
            image_path, tn_width, tn_height)

        html_content = _get_popup_html(
            image_path, thumbnail_path, width, height)

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
        if (_can_create_preview(image_path) and
                not os.path.exists(thumbnail_path)):
            def update_popup():
                html_content = _get_popup_html(
                    image_path, thumbnail_path, width, height)
                if on_hide.hidden:
                    return
                view.show_popup(
                    html_content, location=location,
                    flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY,
                    on_navigate=on_navigate)

            _append_image_job(
                image_path, thumbnail_path, width=tn_width, height=tn_height,
                cont=update_popup)
            _run_image_jobs()


class PreviewImagePhantomListener(sublime_plugin.ViewEventListener,
                                  preview_utils.SettingsListener):
    key = "preview_image"

    def __init__(self, view):
        self.view = view
        self.phantoms = []
        self._selection_modifications = 0

        self._phantom_lock = threading.Lock()

        self._init_watch_settings()

        view.erase_phantoms(self.key)
        # self.update_phantoms()
        sublime.set_timeout_async(self.update_phantoms)

    def _init_watch_settings(self):
        def update_image_size(init=False):
            size = self.image_size
            if isinstance(size, list):
                self.image_width, self.image_height = size
            else:
                self.image_width = self.image_height = size
            if not init:
                self.reset_phantoms()

        view_attr = {
            "visible_mode": {
                "setting": "preview_image_mode",
                "call_after": self.update_phantoms
            },
            "image_size": {
                "setting": "preview_phantom_image_size",
                "call_after": update_image_size
            },
            "image_scale": {
                "setting": "preview_image_scale_quotient",
                "call_after": self.reset_phantoms
            },
        }

        lt_attr_updates = view_attr.copy()

        self._init_list_add_on_change(_name, view_attr, lt_attr_updates)

        update_image_size(init=True)

    @classmethod
    def is_applicable(cls, settings):
        try:
            view = inspect.currentframe().f_back.f_locals['view']
            return view.score_selector(0, 'text.tex.latex') > 0
        except KeyError:
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
            if os.path.exists(p.thumbnail_path):
                width, height = _adapt_image_size(
                    p.thumbnail_path, self.image_width, self.image_height)
                html_content += """
                <div>
                <img src="file://{p.thumbnail_path}"
                 width="{width}"
                 height="{height}">
                </div>
                """.format(**locals())
            elif convert_installed():
                html_content += """Preparing image for preview..."""
            elif os.path.exists(p.thumbnail_path + _ERROR_EXTENSION):
                img_tag = "ERROR: Failed to create preview thumbnail."
            else:
                html_content += (
                    "Install ImageMagick to enable a preview for "
                    "this image type."
                )
        html_content = """
        <body id="latextools-preview-image-phantom">
            {html_content}
        </body>
        """.format(html_content=html_content)
        return html_content

    def on_navigate(self, href):
        command, index = href.split(" ")
        index = int(index)
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

    def reset_phantoms(self):
        self.delete_phantoms()
        self.update_phantoms()

    def delete_phantoms(self):
        view = self.view
        with self._phantom_lock:
            for p in self.phantoms:
                view.erase_phantom_by_id(p.id)
            self.phantoms = []

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

        tn_width = self.image_scale * self.image_width
        tn_height = self.image_scale * self.image_height
        for scope in scopes:
            file_name = view.substr(scope)[1:-1]
            image_path = find_image(
                tex_root, file_name, tex_file_name=view.file_name())

            thumbnail_path = _get_thumbnail_path(
                image_path, tn_width, tn_height)

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

        if _can_create_preview():
            for p in need_thumbnails:
                _append_image_job(
                    p.image_path, p.thumbnail_path,
                    width=tn_width, height=tn_height,
                    cont=lambda: self.update_phantom(p))
            if need_thumbnails:
                _run_image_jobs()
