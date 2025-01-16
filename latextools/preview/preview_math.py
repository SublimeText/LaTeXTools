import base64
import html
import os
import re
import struct
import subprocess
import threading
import time
import types

import sublime

from ..utils import cache
from ..utils.external_command import execute_command
from ..utils.logging import logger
from ..utils.settings import get_setting
from ..utils.settings import subscribe_settings_change
from ..utils.settings import unsubscribe_settings_change
from ..utils.tex_log import parse_tex_log
from ..utils.utils import cpu_count
from .preview_utils import ghostscript_installed
from .preview_utils import get_ghostscript_version
from .preview_utils import run_ghostscript_command
from . import preview_threading as pv_threading

# increase this number if you change the convert command to mark the
# generated images as expired
_version = 2

# use this variable to disable the plugin for a session
# (until ST is restarted)
_IS_ENABLED = True

try:
    import mdpopups

    def get_color(view):
        try:
            color = mdpopups.scope2style(view, "").get("color", "#CCCCCC")
        except Exception:
            color = "#CCCCCC"
        return color

except Exception:

    def get_color(view):
        return "#CCCCCC"


# the default and usual template for the latex file
default_latex_template = """
\\documentclass[preview,border=0.3pt]{standalone}
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
temp_path = ""

# we use png files for the html popup
_IMAGE_EXTENSION = ".png"
# we add this extension to log error information
_ERROR_EXTENSION = ".err"

_name = "preview_math"


def latextools_plugin_loaded():
    global temp_path

    # register the temp folder for auto deletion
    temp_path = os.path.join(cache._global_cache_path(), _name)
    pv_threading.register_temp_folder(_name, temp_path)


def _create_image(
    latex_program,
    latex_document,
    base_name,
    color,
    density,
    hires,
    max_bitmap,
    bufferspace,
    **kwargs
):
    """Create an image for a latex document."""
    rel_source_path = base_name + ".tex"
    pdf_path = os.path.join(temp_path, base_name + ".pdf")
    image_path = os.path.join(temp_path, base_name + _IMAGE_EXTENSION)

    # do nothing if the image already exists
    if os.path.exists(image_path):
        return

    err_log = []
    gs_error_occurred = False

    # write the latex document
    source_path = os.path.join(temp_path, rel_source_path)
    with open(source_path, "w", encoding="utf-8") as f:
        f.write(latex_document)

    # compile the latex document to a pdf
    execute_command(
        [latex_program, "-interaction=nonstopmode", rel_source_path],
        cwd=temp_path,
        shell=sublime.platform() == "windows",
    )

    pdf_exists = os.path.exists(pdf_path)
    if not pdf_exists:
        dvi_path = os.path.join(temp_path, base_name + ".dvi")
        if os.path.exists(dvi_path):
            pdf_path = dvi_path
            pdf_exists = True

    if pdf_exists:
        # get the cropping boundaries; note that the relevant output is
        # written to STDERR rather than STDOUT; we specify 72 dpi in order to
        # speed up processing; the user-supplied density will be used in
        # making the actual conversion
        rc, _, output = run_ghostscript_command(
            ["-sDEVICE=bbox", "-r72", "-dLastPage=1", pdf_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        if rc == 0:
            # we only check the first line of output which should be in the
            # format:
            # %%BoundingBox: int int int int
            try:
                bbox = [int(x) for x in output.splitlines()[0].lstrip("%%BoundingBox: ").split()]
            except ValueError:
                bbox = None
        else:
            bbox = None

        # hires renders the image at 8 times the dpi, then scales it down
        scale_factor = 8 if hires else 1

        # allow Ghostscript to use multiple CPUs, up to two less than the
        # total number (so that sublime_text and plugin_host are minimally
        # affected)
        cpus = max(cpu_count() - 2, 1)

        # convert the pdf to a png image
        command = [
            "-sDEVICE=pngalpha",
            "-dLastPage=1",
            "-sOutputFile={image_path}".format(image_path=image_path),
            "-r{density}".format(density=density * scale_factor),
            "-dDownScaleFactor={0}".format(scale_factor),
            "-dTextAlphaBits=4",
            "-dGraphicsAlphaBits=4",
            "-dNumRenderingThreads={0}".format(cpus),
            "-dMaxBitmap={0}".format(max_bitmap),
            "-dBufferSpace={0}".format(bufferspace),
        ]

        # calculate and apply cropping boundaries, if we have them
        if bbox:
            # coordinates in bounding box given in the form:
            # (ll_x, ll_y), (ur_x, ur_y)
            # where ll is lower left and ur is upper right
            # 4pts are added to each length for some padding
            # these are then multiplied by the ratio of the final density to
            # the PDFs DPI (72) to get the final size of the image in pixels
            width = round((bbox[2] - bbox[0] + 4) * density * scale_factor / 72)
            height = round((bbox[3] - bbox[1] + 4) * density * scale_factor / 72)
            command.extend(
                [
                    "-g{width}x{height}".format(**locals()),
                    "-c",
                    # this is the command that does the clipping starting from
                    # the lower left of the displayed contents; we subtract 2pts
                    # to properly center the final image with our padding
                    "<</Install {{{0} {1} translate}}>> setpagedevice".format(
                        -1 * (bbox[0] - 2), -1 * (bbox[1] - 2)
                    ),
                    "-f",
                ]
            )

        command.append(pdf_path)

        rc, output, _ = run_ghostscript_command(
            command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )

        if rc != 0:
            gs_error_occurred = True
            err_log.append("Error while running Ghostscript. {0}".format(output))

        # Ghostscript will output a 0 byte sized image if certain issues
        # occur. Deal with this here.
        if os.path.exists(image_path) and os.path.getsize(image_path) < 1:
            os.remove(image_path)
            gs_error_occurred = True
            err_log.append(
                "Ghostscript could not produce an image. "
                "Please try changing the preview_math_bufferspace setting "
                "to a larger value. Currently: {0}. ".format(bufferspace)
                + "This setting can be found in the LaTeXTools (Advanced) "
                "settings file."
            )

        if gs_error_occurred:
            err_log.append("")

    if not pdf_exists:
        err_log.append(
            "Failed to run '{latex_program}' to create pdf to preview.".format(**locals())
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
            except Exception as e:
                err_log.append("Error while parsing log file: {0}".format(e))
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
    elif not gs_error_occurred and not os.path.exists(image_path):
        err_log.append("Failed to convert pdf to png to preview.")

    if err_log:
        err_file_path = image_path + _ERROR_EXTENSION
        with open(err_file_path, "w", encoding="utf-8") as f:
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
    # validate the temporary file directory is available
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    if not pv_threading.has_function(_name):
        pv_threading.register_function(_name, _execute_job)
    pv_threading.run_jobs(_name)


class PhantomNamepace(types.SimpleNamespace):
    """
    A hashable SimpleNamespace required for python 3.8 compatibility
    """

    def __hash__(self):
        return self.id


class MathPreviewPhantomProvider:
    key = "preview_math"
    # a dict from the file name to the content to avoid storing it for
    # every view
    template_contents = {}
    # cache to check refresh the template
    template_mtime = {}

    def __init__(self, view):
        self.view = view
        self.phantoms = []

        self._phantom_lock = threading.Lock()

        self.mode = "selected"
        self.latex_compile_program = ""
        self.no_star_envs = []
        self.color = None
        self.background_color = None
        self.scope = ""
        self.scale_quotient = 1
        self.density = 150
        self.hires = True
        self.max_bitmap = 1000000
        self.bufferspace = 4000000

        self.template_file = ""
        self.template_packages = ""
        self.template_preamble = ""

        subscribe_settings_change(self.key, self._on_settings_changed, view)
        self._on_settings_changed()

    def unsubscribe(self):
        unsubscribe_settings_change(self.key, self.view)
        self.delete_phantoms()

    def _on_settings_changed(self):
        reset = False
        prefix_len = len("preview_math_")
        for key in (
            "preview_math_mode",
            "preview_math_latex_compile_program",
            "preview_math_no_star_envs",
            "preview_math_color",
            "preview_math_background_color",
            "preview_math_scope",
            "preview_math_scale_quotient",
            "preview_math_density",
            "preview_math_hires",
            "preview_math_max_bitmap",
            "preview_math_bufferspace",
        ):
            value = get_setting(key, view=self.view)
            attr = key[prefix_len:]
            if value is not None and getattr(self, attr) != value:
                setattr(self, attr, value)
                reset = True

        # custom setter

        value = get_setting("preview_math_template_packages", view=self.view)
        if isinstance(value, list):
            value = "\n".join(value)
        if value is not None and self.template_packages != value:
            self.template_packages = value
            reset = True

        value = get_setting("preview_math_template_preamble", view=self.view)
        if isinstance(value, list):
            value = "\n".join(value)
        if value is not None and self.template_preamble != value:
            self.template_preamble = value
            reset = True

        value = get_setting("preview_math_template_file", view=self.view)
        if value is not None and self.template_file != value:
            self.template_file = value
            reset = True
            self._read_latex_template_file(refresh=True)

        if reset:
            sublime.set_timeout_async(self.reset_phantoms)

    def _read_latex_template_file(self, refresh=False):
        if not self.template_file:
            return

        if self.template_file in self.template_contents:
            if not refresh:
                return
            try:
                mtime = os.path.getmtime(self.template_file)
                old_mtime = self.template_mtime[self.template_file]
                if old_mtime == mtime:
                    return
            except Exception:
                return

        mtime = 0
        try:
            with open(self.template_file, "r", encoding="utf-8") as f:
                file_content = f.read()
            mtime = os.path.getmtime(self.template_file)
            logger.info("Load math preview template file for '%s'", self.template_file)
        except Exception as e:
            logger.error("Error while reading math preview template file: %s", e)
            file_content = None
        self.template_contents[self.template_file] = file_content
        self.template_mtime[self.template_file] = mtime

    def on_navigate(self, href):
        global _IS_ENABLED
        if href == "check_system":
            self.view.window().run_command("latextools_system_check")
        elif href == "disable":
            answer = sublime.yes_no_cancel_dialog(
                "The math-live preview will be temporary disabled until "
                "you restart Sublime Text. If you want to disable it "
                "permanent open your LaTeXTools settings and set "
                '"preview_math_mode" to "none".',
                yes_title="Open LaTeXTools settings",
                no_title="Disable for this session",
            )
            if answer == sublime.DIALOG_CANCEL:
                # do nothing
                return
            _IS_ENABLED = False
            self.update_phantoms()
            if answer == sublime.DIALOG_YES:
                self.view.window().run_command("latextools_open_user_settings")
        elif href.startswith("report-"):
            file_path = href[len("report-") :]
            if not os.path.exists(file_path):
                sublime.error_message("Report file missing: {0}.".format(file_path))
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
        view = self.view
        if not view.is_primary():
            return
        # not sure why this happens, but ignore these cases
        window = view.window()
        if window is None:
            return
        if not ghostscript_installed():
            return

        # update the regions of the phantoms
        self._update_phantom_regions()

        new_phantoms = []
        job_args = []
        if not _IS_ENABLED or self.mode == "none" or self.scope is None:
            if not self.phantoms:
                return
            scopes = []
        elif self.mode == "all":
            scopes = view.find_by_selector(self.scope)
        elif self.mode == "selected":
            math_scopes = view.find_by_selector(self.scope)
            scopes = [
                scope for scope in math_scopes if any(scope.contains(sel) for sel in view.sel())
            ]
        else:
            self.mode = "none"
            scopes = []

        # avoid creating a preview if someone just inserts $|$ and
        # most likely want to create an inline and not a block block
        def is_dollar_snippet(scope):
            is_selector = view.match_selector(scope.begin(), "meta.environment.math.block.dollar")
            sel_at_start = any(sel.empty() and sel.b == scope.begin() + 1 for sel in view.sel())
            return is_selector and sel_at_start

        scopes = [scope for scope in scopes if not is_dollar_snippet(scope)]

        color = self.color
        # if no foreground color is defined use the default test color
        if not color:
            color = get_color(view)

        hires = self.hires and get_ghostscript_version() >= (9, 14)

        for scope in scopes:
            content = view.substr(scope)
            multline = "\n" in content

            layout = (
                sublime.LAYOUT_BLOCK
                if multline or self.mode == "selected"
                else sublime.LAYOUT_INLINE
            )
            region = sublime.Region(scope.end())

            try:
                p = next(e for e in self.phantoms if e.region == region)
                if p.content == content:
                    new_phantoms.append(p)
                    continue

                # update the content and the layout
                p.content = content
                p.layout = layout
            except Exception:
                p = PhantomNamepace(
                    id=None,
                    region=region,
                    content=content,
                    layout=layout,
                    update_time=0,
                )

            # generate the latex template
            latex_document = self._create_document(scope, color)

            # create a string, which uniquely identifies the compiled document
            id_str = "\n".join(
                [
                    str(_version),
                    self.latex_compile_program,
                    str(self.density),
                    str(hires),
                    color,
                    latex_document,
                ]
            )
            base_name = cache.hash_digest(id_str)
            image_path = os.path.join(temp_path, base_name + _IMAGE_EXTENSION)

            # if the file exists as an image update the phantom
            if os.path.exists(image_path):
                if p.id is not None:
                    view.erase_phantom_by_id(p.id)
                    _cancel_image_jobs(view.id(), p)
                html_content = self._generate_html(image_path)
                p.id = view.add_phantom(
                    self.key, region, html_content, layout, on_navigate=self.on_navigate
                )
                new_phantoms.append(p)
                continue
            # if neither the file nor the phantom exists, create a
            # placeholder phantom
            elif p.id is None:
                p.id = view.add_phantom(
                    self.key,
                    region,
                    self._wrap_html("\u231B"),
                    layout,
                    on_navigate=self.on_navigate,
                )

            job_args.append(
                {
                    "latex_document": latex_document,
                    "base_name": base_name,
                    "color": color,
                    "density": self.density,
                    "hires": self.hires,
                    "max_bitmap": self.max_bitmap,
                    "bufferspace": self.bufferspace,
                    "p": p,
                    "cont": self._make_cont(p, image_path, time.time()),
                }
            )

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
            _extend_image_jobs(view.id(), self.latex_compile_program, job_args)
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
            after_str = view.substr(after_reg)
            m = re.match(r"\\end\{([^\}]+?)(\*?)\}", after_str)
            if m:
                env = m.group(1)

        # create the opening and closing string
        if offset:
            open_str = content[:offset]
            close_str = content[-offset:]
            # strip those strings from the content
            content = content[offset:-offset]
        elif env:
            star = "*" if env not in self.no_star_envs or m.group(2) else ""
            # add a * to the env to avoid numbers in the resulting image
            open_str = "\\begin{{{env}{star}}}".format(**locals())
            close_str = "\\end{{{env}{star}}}".format(**locals())
        else:
            open_str = "\\("
            close_str = "\\)"

        # strip the content
        content = content.strip()

        document_content = "{open_str}\n{content}\n{close_str}".format(**locals())

        try:
            latex_template = self.template_contents[self.template_file]
            if not latex_template:
                raise Exception("Template must not be empty!")
        except Exception:
            latex_template = default_latex_template

        if color.startswith("#"):
            color = color[1:].upper()
            set_color = "\\color[HTML]{{{color}}}".format(color=color)
        else:
            set_color = "\\color{{{color}}}".format(color=color)

        latex_document = (
            latex_template.replace("<<content>>", document_content, 1)
            .replace("<<set_color>>", set_color, 1)
            .replace("<<packages>>", self.template_packages, 1)
            .replace("<<preamble>>", self.template_preamble, 1)
        )

        return latex_document

    def _make_cont(self, p, image_path, update_time):
        def cont():
            # if the image does not exists do nothing
            if os.path.exists(image_path):
                # generate the html
                html_content = self._generate_html(image_path)
            elif os.path.exists(image_path + _ERROR_EXTENSION):
                # inform the user about the error
                html_content = self._generate_error_html(image_path)
            else:
                return
            # move to main thread and update the phantom
            sublime.set_timeout(lambda: self._update_phantom_content(p, html_content, update_time))

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
            self.key, p.region, html_content, p.layout, on_navigate=self.on_navigate
        )

        # update the phantoms update time
        p.update_time = update_time

    def _generate_error_html(self, image_path):
        content = "ERROR: "
        err_file = image_path + _ERROR_EXTENSION
        with open(err_file, "r") as f:
            content += f.readline()

        html_content = html.escape(content, quote=False) + (
            "<br>"
            '<a href="check_system">(Check System)</a> '
            '<a href="report-{err_file}">(Show Report)</a> '
            '<a href="disable">(Disable)</a>'.format(err_file=err_file)
        )

        return self._wrap_html(html_content)

    def _generate_html(self, image_path):
        with open(image_path, "rb") as f:
            image_raw_data = f.read()

        if len(image_raw_data) < 24:
            width = height = 0
        else:
            width, height = struct.unpack(">ii", image_raw_data[16:24])

        if width <= 1 and height <= 1:
            html_content = "&nbsp;"
        else:
            if self.scale_quotient != 1:
                width /= self.scale_quotient
                height /= self.scale_quotient
                style = 'style="width: {width}; height: {height};"'.format(**locals())
            else:
                style = ""
            img_data_b64 = base64.b64encode(image_raw_data).decode("ascii")
            html_content = '<img {style} src="data:image/png;base64,{img_data_b64}">'.format(**locals())

        # wrap the html content in a body and style
        return self._wrap_html(html_content)

    def _wrap_html(self, html_content):
        if self.color or self.background_color:
            style = "<style> body {"
            if self.color:
                style += "color: {0};".format(self.color)
            if self.background_color:
                style += "background-color: {0};".format(self.background_color)
            style += "} </style>"
        else:
            style = ""

        return '<body id="latextools-preview-math-phantom">' + style + html_content + "</body>"
