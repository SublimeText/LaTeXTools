import json
import os
import shutil
import sublime
import sublime_plugin
import tempfile
import traceback

from .deprecated_command import deprecate

from .utils import cache
from .utils.logging import logger
from .utils.output_directory import get_aux_directory
from .utils.output_directory import get_output_directory
from .utils.settings import get_setting
from .utils.tex_directives import get_tex_root

__all__ = [
    "LatextoolsClearCacheCommand",
    "LatextoolsClearLocalCacheCommand",
    "LatextoolsDeleteTempFilesCommand",
]


def latextools_plugin_loaded():
    """
    unfortunately, there is no reliable way to do clean-up on exit in ST
    see https://github.com/SublimeTextIssues/Core/issues/10
    here we cleanup any directories listed in the temporary_output_dirs
    file as having been previously created by the plugin
    """
    temporary_output_dirs = os.path.join(
        sublime.cache_path(), "LaTeXTools", "temporary_output_dirs"
    )

    if os.path.exists(temporary_output_dirs):
        with open(temporary_output_dirs, "r") as f:
            data = json.load(f)

        tempdir = tempfile.gettempdir()

        try:
            for directory in data["directories"]:
                # shutil.rmtree is a rather blunt tool, so here we try to
                # ensure we are only deleting legitimate temporary files
                if (
                    directory is None
                    or not isinstance(directory, str)
                    or not directory.startswith(tempdir)
                ):
                    continue

                try:
                    shutil.rmtree(directory)
                except OSError:
                    pass
                else:
                    logger.info("Deleted old temp directory %s", directory)
        except KeyError:
            pass

        try:
            os.remove(temporary_output_dirs)
        except OSError:
            pass


class LatextoolsClearCacheCommand(sublime_plugin.WindowCommand):
    def run(self):
        try:
            shutil.rmtree(cache._global_cache_path())
        except FileNotFoundError:
            pass
        except OSError as e:
            logger.error("Can't delete global cache: %s", e)

        tex_root = get_tex_root(self.window.active_view())
        if not tex_root:
            return

        try:
            cache.LocalCache(tex_root).invalidate()
        except Exception:
            logger.error("Error while trying to delete local cache")
            traceback.print_exc()


class LatextoolsClearLocalCacheCommand(sublime_plugin.WindowCommand):
    def is_visible(self, *args):
        view = self.window.active_view()
        return view and view.match_selector(0, "text.tex.latex")

    def run(self):
        tex_root = get_tex_root(self.window.active_view())
        if not tex_root:
            return

        try:
            cache.LocalCache(tex_root).invalidate()
        except Exception:
            logger.error("Error while trying to delete local cache")
            traceback.print_exc()


class LatextoolsDeleteTempFilesCommand(sublime_plugin.WindowCommand):
    def is_visible(self, *args):
        view = self.window.active_view()
        return view and view.match_selector(0, "text.tex.latex")

    def run(self):
        # Retrieve root file and dirname.
        view = self.window.active_view()
        root_file = get_tex_root(view)
        if root_file is None:
            msg = (
                "Could not find TEX root. Please ensure that either you "
                + "have configured a TEX root in your project settings or "
                + "have a LaTeX document open."
            )
            sublime.status_message(msg)
            logger.error(msg)
            return

        if not os.path.isfile(root_file):
            message = "Could not find TEX root {0}.".format(root_file)
            sublime.status_message(message)
            logger.error(message)
            return

        # clear the cache
        try:
            cache.LocalCache(root_file).invalidate()
        except Exception:
            logger.error("Error while trying to delete local cache")
            traceback.print_exc()

        aux_directory, aux_directory_setting = get_aux_directory(view, return_setting=True)

        output_directory, output_directory_setting = get_output_directory(view, return_setting=True)

        deleted = True

        if aux_directory is not None:
            # we cannot delete the output directory on Windows in case
            # Sumatra is holding a reference to it
            if sublime.platform() != "windows" or aux_directory != output_directory:
                if aux_directory_setting.startswith("<<"):
                    self._rmtree(aux_directory)
                else:
                    deleted = self.delete_temp_files(aux_directory)

        if output_directory is not None:
            if output_directory_setting.startswith("<<"):
                # we cannot delete the output directory on Windows in case
                # Sumatra is holding a reference to it
                if sublime.platform() == "windows":
                    self._clear_dir(output_directory)
                else:
                    self._rmtree(output_directory)
            else:
                deleted = self.delete_temp_files(output_directory)
        else:
            # if there is no output directory, we may need to clean files
            # in the main directory, even if aux_directory is used
            deleted = self.delete_temp_files(os.path.dirname(root_file))

        if deleted:
            sublime.status_message("Deleted temp files")

    def delete_temp_files(self, path):
        view = self.window.active_view()
        # Load the files to delete from the settings
        temp_files_exts = get_setting(
            "temp_files_exts",
            [
                ".blg",
                ".bbl",
                ".aux",
                ".log",
                ".brf",
                ".nlo",
                ".out",
                ".dvi",
                ".ps",
                ".lof",
                ".toc",
                ".fls",
                ".fdb_latexmk",
                ".pdfsync",
                ".synctex.gz",
                ".ind",
                ".ilg",
                ".idx",
            ],
            view,
        )

        ignored_folders = set(
            get_setting("temp_files_ignored_folders", [".git", ".svn", ".hg"], view)
        )

        files = []
        for dir_path, dir_names, file_names in os.walk(path):
            dir_names[:] = [d for d in dir_names if d not in ignored_folders]
            for file_name in file_names:
                for ext in temp_files_exts:
                    if file_name.endswith(ext):
                        files.append(os.path.join(dir_path, file_name))

        if not files:
            return False

        if get_setting("temp_files_prompt_on_delete", False, view):
            msg = "Are you sure you want to delete the following files?\n\n" + "\n".join(files[:20])
            if len(files) > 20:
                msg += "\n..."
            if not sublime.ok_cancel_dialog(msg):
                return False

        for file in files:
            self._rmfile(file)

        return True

    def _rmtree(self, path):
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
        except OSError:
            # report the exception if the folder didn't end up deleted
            logger.error("Error while trying to delete %s", path)
            traceback.print_exc()

    def _rmfile(self, path):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError:
            # basically here for locked files in Windows,
            # but who knows what we might find?
            logger.error("Error while trying to delete %s", path)
            traceback.print_exc()

    def _clear_dir(self, path):
        for root, directories, file_names in os.walk(path):
            for directory in directories:
                self._rmtree(os.path.join(root, directory))
            for file_name in file_names:
                self._rmfile(os.path.join(root, file_name))


deprecate(globals(), "ClearLocalLatexCacheCommand", LatextoolsClearLocalCacheCommand)
deprecate(globals(), "DeleteTempFilesCommand", LatextoolsDeleteTempFilesCommand)
