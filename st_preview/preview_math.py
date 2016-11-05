import base64
import html
import os
import re
import struct
import threading
import time
import types

import sublime
import sublime_plugin

from ..parseTeXlog import parse_tex_log

from ..latextools_utils import cache, get_setting
from ..latextools_utils.external_command import execute_command
from . import preview_utils
from .preview_utils import convert_installed, run_convert_command
from . import preview_threading as pv_threading

# export the listener
exports = ["MathPreviewPhantomListener"]

# increase this number if you change the convert command to mark the
# generated images as expired
_version = 1


try:
    import mdpopups

    def get_color(view):
        try:
            color = mdpopups.scope2style(view, "").get("color", "#CCCCCC")
        except:
            color = "#CCCCCC"
        return color
except:
    def get_color(view):
        return "#CCCCCC"


# the default and usual template for the latex file
default_latex_template = """
\\documentclass[preview]{standalone}
% import xcolor if available and not already present
\\IfFileExists{xcolor.sty}{\\usepackage{xcolor}}{}%
<<packages>>
<<preamble>>
\\begin{document}
% set the foreground color
\\IfFileExists{xcolor.sty}{<<set_color>>}{}%
<<content>>
\\end{document}
"""


# the path to the temp files (set on loading)
temp_path = None

# we use png files for the html popup
_IMAGE_EXTENSION = ".png"
# we add this extension to log error information
_ERROR_EXTENSION = ".err"

_scale_quotient = 1
_density = 150
_lt_settings = {}

_name = "preview_math"


def _on_setting_change():
    global _density, _scale_quotient
    _scale_quotient = _lt_settings.get(
        "preview_math_scale_quotient", _scale_quotient)
    _density = _lt_settings.get("preview_math_density", _density)
    max_threads = get_setting(
        "preview_max_convert_threads", default=None, view={})
    if max_threads is not None:
        pv_threading.set_max_threads(max_threads)


def plugin_loaded():
    print('plugin_loaded in preview_math called')
    global _lt_settings, temp_path
    _lt_settings = sublime.load_settings("LaTeXTools.sublime-settings")

    temp_path = os.path.join(cache._global_cache_path(), _name)
    # validate the temporary file directory is available
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    # init all variables
    _on_setting_change()
    # add a callback to setting changes
    _lt_settings.add_on_change("lt_preview_math_main", _on_setting_change)

    # register the temp folder for auto deletion
    pv_threading.register_temp_folder(_name, temp_path)


def plugin_unloaded():
    _lt_settings.clear_on_change("lt_preview_math_main")


def _create_image(latex_program, latex_document, base_name, color,
                  **kwargs):
    """Create an image for a latex document."""
    rel_source_path = base_name + ".tex"
    pdf_path = os.path.join(temp_path, base_name + ".pdf")
    image_path = os.path.join(temp_path, base_name + _IMAGE_EXTENSION)

    # do nothing if the pdf already exists
    if os.path.exists(pdf_path):
        return

    # write the latex document
    source_path = os.path.join(temp_path, rel_source_path)
    with open(source_path, "w", encoding="utf-8") as f:
        f.write(latex_document)

    # compile the latex document to a pdf
    execute_command([
        latex_program, '-interaction=nonstopmode', rel_source_path
    ], cwd=temp_path)

    pdf_exists = os.path.exists(pdf_path)
    if not pdf_exists:
        dvi_path = os.path.join(temp_path, base_name + ".dvi")
        if os.path.exists(dvi_path):
            pdf_path = dvi_path
            pdf_exists = True

    if pdf_exists:
        # convert the pdf to a png image
        density = _density
        run_convert_command([
            # set the image size/density
            '-density', '{density}x{density}'.format(density=density),
            # trim the content to the real size
            '-trim',
            pdf_path, image_path
        ])

    err_file_path = image_path + _ERROR_EXTENSION
    err_log = []
    if not pdf_exists:
        err_log.append(
            "Failed to run '{latex_program}' to create pdf to preview."
            .format(**locals())
        )
        err_log.append("")
        err_log.append("")

        log_file = os.path.join(temp_path, base_name + ".log")
        log_exists = os.path.exists(log_file)

        if not log_exists:
            err_log.append("No log file found.")
        else:
            with open(log_file, "rb") as f:
                log_data = f.read()
            try:
                errors, warnings, _ = parse_tex_log(log_data, temp_path)
            except:
                err_log.append("Error while parsing log file.")
                errors = warnings = []
            if errors:
                err_log.append("Errors:")
                err_log.extend(errors)
            if warnings:
                err_log.append("Warnings:")
                err_log.extend(warnings)
            err_log.append("")

        err_log.append("LaTeX document:")
        err_log.append("-----BEGIN DOCUMENT-----")
        err_log.append(latex_document)
        err_log.append("-----END DOCUMENT-----")

        if log_exists:
            err_log.append("")
            log_content = log_data.decode("utf8", "ignore")
            err_log.append("Log file:")
            err_log.append("-----BEGIN LOG-----")
            err_log.append(log_content)
            err_log.append("-----END LOG-----")
    elif not os.path.exists(image_path):
        err_log.append("Failed to convert pdf to png to preview.")

    if err_log:
        with open(err_file_path, "w") as f:
            f.write("\n".join(err_log))

    # cleanup created files
    for ext in ["tex", "aux", "log", "pdf", "dvi"]:
        delete_path = os.path.join(temp_path, base_name + "." + ext)
        if os.path.exists(delete_path):
            os.remove(delete_path)


# CONVERT THREADING
def _execute_job(job):
    _create_image(**job)
    job["cont"]()


def _cancel_image_jobs(vid, p=None):
    global _job_list

    if p is None:
        def is_target_job(job):
            return job["vid"] == vid
    elif isinstance(p, list):
        pset = set(p)

        def is_target_job(job):
            return job["vid"] == vid and job["p"] in pset
    else:
        def is_target_job(job):
            return job["vid"] == vid and job["p"] == p

    pv_threading.cancel_jobs(_name, is_target_job)


def _extend_image_jobs(vid, latex_program, jobs):
    prepared_jobs = []
    for job in jobs:
        job["latex_program"] = latex_program
        job["vid"] = vid

        prepared_jobs.append((job["base_name"], job))

    pv_threading.extend_jobs(_name, prepared_jobs[::-1])


def _run_image_jobs():
    if not pv_threading.has_function(_name):
        pv_threading.register_function(_name, _execute_job)
    pv_threading.run_jobs(_name)


def _wrap_html(html_content, color=None, background_color=None):
    if color or background_color:
        style = "<style>"
        style += "body {"
        if color:
            style += "color: {0};".format(color)
        if background_color:
            style += "background-color: {0};".format(background_color)
        style += "}"
        style += "</style>"
    else:
        style = ""
    html_content = (
        '<body id="latextools-preview-math-phantom">'
        '{style}'
        '{html_content}'
        '</body>'
        .format(**locals())
    )
    return html_content


def _generate_error_html(view, image_path, style_kwargs):
    content = "ERROR: "
    err_file = image_path + _ERROR_EXTENSION
    with open(err_file, "r") as f:
        content += f.readline()

    html_content = html.escape(content, quote=False)
    html_content += (
        '<br>'
        '<a href="check_system">(Check System)</a> '
        '<a href="report-{err_file}">(Show Report)</a>'
        .format(**locals())
    )

    html_content = _wrap_html(html_content, **style_kwargs)
    return html_content


def _generate_html(view, image_path, style_kwargs):
    with open(image_path, "rb") as f:
        image_raw_data = f.read()

    if len(image_raw_data) < 24:
        width = height = 0
    else:
        width, height = struct.unpack(">ii", image_raw_data[16:24])

    if width <= 1 and height <= 1:
        html_content = "&nbsp;"
    else:
        if _scale_quotient != 1:
            width /= _scale_quotient
            height /= _scale_quotient
            style = (
                'style="width: {width}; height: {height};"'
                .format(**locals())
            )
        else:
            style = ""
        img_data_b64 = base64.b64encode(image_raw_data).decode('ascii')
        html_content = (
            "<img {style} src=\"data:image/png;base64,{img_data_b64}\">"
            .format(**locals())
        )
    # wrap the html content in a body and style
    html_content = _wrap_html(html_content, **style_kwargs)
    return html_content


class MathPreviewPhantomListener(sublime_plugin.ViewEventListener,
                                 preview_utils.SettingsListener):
    key = "preview_math"
    # a dict from the file name to the content to avoid storing it for
    # every view
    template_contents = {}
    # cache to check refresh the template
    template_mtime = {}
    template_lock = threading.Lock()

    def __init__(self, view):
        self.view = view
        self.phantoms = []

        self._phantom_lock = threading.Lock()

        self._modifications = 0
        self._selection_modifications = 0

        self._init_watch_settings()

        if self.latex_template_file:
            sublime.set_timeout_async(self._read_latex_template_file)

        view.erase_phantoms(self.key)
        # start with updating the phantoms
        sublime.set_timeout_async(self.update_phantoms)

    def _init_watch_settings(self):
        # listen to setting changes to update the phantoms
        def update_packages_str(init=False):
            self.packages_str = "\n".join(self.packages)
            if not init:
                self.reset_phantoms()

        def update_preamble_str(init=False):
            if isinstance(self.preamble, str):
                self.preamble_str = self.preamble
            else:
                self.preamble_str = "\n".join(self.preamble)

            if not init:
                self.reset_phantoms()

        def update_template_file(init=False):
            self._read_latex_template_file(refresh=True)
            if not init:
                self.reset_phantoms()

        view_attr = {
            "visible_mode": {
                "setting": "preview_math_mode",
                "call_after": self.update_phantoms
            },
            "latex_program": {
                "setting": "preview_math_latex_compile_program",
                "call_after": self.reset_phantoms
            },
            "no_star_env": {
                "setting": "preview_math_no_star_envs",
                "call_after": self.reset_phantoms
            },
            "color": {
                "setting": "preview_math_color",
                "call_after": self.reset_phantoms
            },
            "background_color": {
                "setting": "preview_math_background_color",
                "call_after": self.reset_phantoms
            },
            "packages": {
                "setting": "preview_math_template_packages",
                "call_after": update_packages_str
            },
            "preamble": {
                "setting": "preview_math_template_preamble",
                "call_after": update_preamble_str
            },
            "latex_template_file": {
                "setting": "preview_math_template_file",
                "call_after": update_template_file
            }
        }

        lt_attr = view_attr.copy()

        # watch these attributes for setting changes to reset the phantoms
        watch_attr = {
            "_watch_scale_quotient": {
                "setting": "preview_math_scale_quotient",
                "call_after": self.reset_phantoms
            },
            "_watch_density": {
                "setting": "preview_math_density",
                "call_after": self.reset_phantoms
            }
        }
        for attr_name, d in watch_attr.items():
            settings_name = d["setting"]
            self.__dict__[attr_name] = _lt_settings.get(settings_name)

        lt_attr.update(watch_attr)

        self._init_list_add_on_change(_name, view_attr, lt_attr)
        update_packages_str(init=True)
        update_preamble_str(init=True)
        update_template_file(init=True)

    def _read_latex_template_file(self, refresh=False):
        with self.template_lock:
            if not self.latex_template_file:
                return

            if self.latex_template_file in self.template_contents:
                if not refresh:
                    return
                try:
                    mtime = os.path.getmtime(self.latex_template_file)
                    old_mtime = self.template_mtime[self.latex_template_file]
                    if old_mtime == mtime:
                        return
                except:
                    return

            mtime = 0
            try:
                with open(self.latex_template_file, "r", encoding="utf8") as f:
                    file_content = f.read()
                mtime = os.path.getmtime(self.latex_template_file)
                print(
                    "LaTeXTools preview_math: "
                    "Load template file for '{0}'"
                    .format(self.latex_template_file)
                )
            except Exception as e:
                print(
                    "LaTeXTools preview_math: "
                    "Error while reading template file: {0}"
                    .format(e)
                )
                file_content = None
            self.template_contents[self.latex_template_file] = file_content
            self.template_mtime[self.latex_template_file] = mtime

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

    def on_after_modified_async(self):
        self.update_phantoms()

    def _validate_after_modified(self):
        self._modifications -= 1
        if self._modifications == 0:
            sublime.set_timeout_async(self.on_after_modified_async)

    def on_modified(self):
        self._modifications += 1
        sublime.set_timeout(self._validate_after_modified, 600)

    def on_after_selection_modified_async(self):
        if self.visible_mode == "selected" or not self.phantoms:
            self.update_phantoms()

    def _validate_after_selection_modified(self):
        self._selection_modifications -= 1
        if self._selection_modifications == 0:
            sublime.set_timeout_async(self.on_after_selection_modified_async)

    def on_selection_modified(self):
        if self._modifications:
            return
        self._selection_modifications += 1
        sublime.set_timeout(self._validate_after_selection_modified, 600)

    #########
    # METHODS
    #########

    def on_navigate(self, href):
        if href == "check_system":
            self.view.window().run_command("latextools_system_check")
        elif href.startswith("report-"):
            file_path = href[len("report-"):]
            if not os.path.exists(file_path):
                sublime.error_message(
                    "Report file missing: {0}.".format(file_path)
                )
                return
            self.view.window().open_file(file_path)

    def reset_phantoms(self):
        self.delete_phantoms()
        self.update_phantoms()

    def delete_phantoms(self):
        view = self.view
        _cancel_image_jobs(view.id())
        with self._phantom_lock:
            for p in self.phantoms:
                view.erase_phantom_by_id(p.id)
            self.phantoms = []

    def update_phantoms(self):
        with self._phantom_lock:
            self._update_phantoms()

    def _update_phantoms(self):
        if not self.view.is_primary():
            return
        # not sure why this happens, but ignore these cases
        if self.view.window() is None:
            return
        if not convert_installed():
            return

        view = self.view

        if not any(view.window().active_view_in_group(g) == view
                   for g in range(view.window().num_groups())):
            return
        # TODO we may only want to apply if the view is visible
        # if view != view.window().active_view():
        #     return

        # update the regions of the phantoms
        self._update_phantom_regions()

        new_phantoms = []
        job_args = []
        if self.visible_mode == "all":
            scopes = view.find_by_selector(
                "text.tex.latex meta.environment.math")
        elif self.visible_mode == "selected":
            math_scopes = view.find_by_selector(
                "text.tex.latex meta.environment.math")
            scopes = [scope for scope in math_scopes
                      if any(scope.contains(sel) for sel in view.sel())]
        elif self.visible_mode == "none":
            if not self.phantoms:
                return
            scopes = []
        else:
            self.visible_mode = "none"
            scopes = []

        # avoid creating a preview if someone just inserts $|$ and
        # most likely want to create an inline and not a block block
        def is_dollar_snippet(scope):
            is_selector = view.score_selector(
                scope.begin(), "meta.environment.math.block.dollar")
            sel_at_start = any(
                sel.empty() and sel.b == scope.begin() + 1
                for sel in view.sel()
            )
            return is_selector and sel_at_start
        scopes = [scope for scope in scopes if not is_dollar_snippet(scope)]

        color = self.color
        # if no foreground color is defined use the default test color
        if not color:
            color = get_color(view)

        style_kwargs = {
            "color": color,
            "background_color": self.background_color
        }

        for scope in scopes:
            content = view.substr(scope)
            multline = "\n" in content

            layout = (sublime.LAYOUT_BLOCK
                      if multline or self.visible_mode == "selected"
                      else sublime.LAYOUT_INLINE)
            BE_BLOCK = view.score_selector(
                scope.begin(), "meta.environment.math.block.be")

            # avoid jumping around in begin end block
            if multline and BE_BLOCK:
                region = sublime.Region(scope.end() + 4)
            else:
                region = sublime.Region(scope.end())

            try:
                p = next(e for e in self.phantoms if e.region == region)
                if p.content == content:
                    new_phantoms.append(p)
                    continue

                # update the content and the layout
                p.content = content
                p.layout = layout
            except:
                p = types.SimpleNamespace(
                    id=None,
                    region=region,
                    content=content,
                    layout=layout,
                    update_time=0
                )

            # generate the latex template
            latex_document = self._create_document(scope, color)

            # create a string, which uniquely identifies the compiled document
            id_str = "\n".join([
                str(_version),
                self.latex_program,
                str(_density),
                color,
                latex_document
            ])
            base_name = cache.hash_digest(id_str)
            image_path = os.path.join(temp_path, base_name + _IMAGE_EXTENSION)

            # if the file exists as an image update the phantom
            if os.path.exists(image_path):
                if p.id is not None:
                    view.erase_phantom_by_id(p.id)
                    _cancel_image_jobs(view.id(), p)
                html_content = _generate_html(view, image_path, style_kwargs)
                p.id = view.add_phantom(
                    self.key, region, html_content, layout,
                    on_navigate=self.on_navigate)
                new_phantoms.append(p)
                continue
            # if neither the file nor the phantom exists, create a
            # placeholder phantom
            elif p.id is None:
                p.id = view.add_phantom(
                    self.key, region, _wrap_html("\u231B", **style_kwargs),
                    layout, on_navigate=self.on_navigate)

            job_args.append({
                "latex_document": latex_document,
                "base_name": base_name,
                "color": color,
                "p": p,
                "cont": self._make_cont(
                    p, image_path, time.time(), style_kwargs)
            })

            new_phantoms.append(p)

        # delete deprecated phantoms
        delete_phantoms = [x for x in self.phantoms if x not in new_phantoms]
        for p in delete_phantoms:
            if p.region != sublime.Region(-1):
                view.erase_phantom_by_id(p.id)
        _cancel_image_jobs(view.id(), delete_phantoms)

        # set the new phantoms
        self.phantoms = new_phantoms

        # run the jobs to create the remaining images
        if job_args:
            _extend_image_jobs(view.id(), self.latex_program, job_args)
            _run_image_jobs()

    def _create_document(self, scope, color):
        view = self.view
        content = view.substr(scope)
        env = None

        # calculate the leading and remaining characters to strip off
        # if not present it is surrounded by an environment
        if content[0:2] in ["\\[", "\\(", "$$"]:
            offset = 2
        elif content[0] == "$":
            offset = 1
        else:
            offset = 0
            # if there is no offset it must be surrounded by an environment
            # get the name of the environment
            scope_end = scope.end()
            line_reg = view.line(scope_end)
            after_reg = sublime.Region(scope_end, line_reg.end())
            after_str = view.substr(line_reg)
            m = re.match(r"\\end\{([^\}]+?)(\*?)\}", after_str)
            if m:
                env = m.group(1)

        # strip the content
        if offset:
            content = content[offset:-offset]
        content = content.strip()

        # create the wrap string
        open_str = "\\("
        close_str = "\\)"
        if env:
            star = "*" if env not in self.no_star_env or m.group(2) else ""
            # add a * to the env to avoid numbers in the resulting image
            open_str = "\\begin{{{env}{star}}}".format(**locals())
            close_str = "\\end{{{env}{star}}}".format(**locals())

        document_content = (
            "{open_str}\n{content}\n{close_str}"
            .format(**locals())
        )

        try:
            latex_template = self.template_contents[self.latex_template_file]
            if not latex_template:
                raise Exception("Template must not be empty!")
        except:
            latex_template = default_latex_template

        if color.startswith("#"):
            color = color[1:].upper()
            set_color = "\\color[HTML]{{{color}}}".format(color=color)
        else:
            set_color = "\\color{{{color}}}".format(color=color)

        latex_document = (
            latex_template
            .replace("<<content>>", document_content, 1)
            .replace("<<set_color>>", set_color, 1)
            .replace("<<packages>>", self.packages_str, 1)
            .replace("<<preamble>>", self.preamble_str, 1)
        )

        return latex_document

    def _make_cont(self, p, image_path, update_time, style_kwargs):
        def cont():
            # if the image does not exists do nothing
            if os.path.exists(image_path):
                # generate the html
                html_content = _generate_html(
                    self.view, image_path, style_kwargs)
            elif os.path.exists(image_path + _ERROR_EXTENSION):
                # inform the user about the error
                html_content = _generate_error_html(
                    self.view, image_path, style_kwargs)
            else:
                return
            # move to main thread and update the phantom
            sublime.set_timeout(
                self._update_phantom_content(p, html_content, update_time)
            )
        return cont

    def _update_phantom_regions(self):
        regions = self.view.query_phantoms([p.id for p in self.phantoms])
        for i in range(len(regions)):
            self.phantoms[i].region = regions[i]

    def _update_phantom_content(self, p, html_content, update_time):
        # if the current phantom is newer than the change ignore it
        if p.update_time > update_time:
            return
        view = self.view
        # update the phantom region
        p.region = view.query_phantom(p.id)[0]

        # if the region is -1 the phantom does not exists anymore
        if p.region == sublime.Region(-1):
            return

        # erase the old and add the new phantom
        view.erase_phantom_by_id(p.id)
        p.id = view.add_phantom(
            self.key, p.region, html_content, p.layout,
            on_navigate=self.on_navigate)

        # update the phantoms update time
        p.update_time = update_time
