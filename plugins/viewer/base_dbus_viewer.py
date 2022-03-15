from __future__ import annotations
import os
import shutil
import sublime

from ...latextools.utils.external_command import external_command, check_call
from ...latextools.utils.settings import get_setting
from ...latextools.utils.sublime_utils import get_sublime_exe

from base_viewer import BaseViewer


class BaseDBusViewer(BaseViewer):
    _CACHED_WORKING_PYTHON = None

    def __init__(self, app_dbus_name, app_command):
        self._app_dbus_name = app_dbus_name
        self._app_command = shutil.which(app_command)
        self._monitor_processes = {}

    def should_bring_viewer_forward(self) -> bool:
        raise NotImplementedError()

    def launch_bring_viewer_forward(self, pdf_file) -> None:
        check_call([self._app_command, pdf_file], shell=False, stdin=None, stdout=None, stderr=None, use_texpath=False)

    @classmethod
    def test_python(cls, python, cache_if_successful=True):
        try:
            check_call([python, '-c', 'import dbus'], use_texpath=False)
            if cache_if_successful:
                cls._CACHED_WORKING_PYTHON = python
            return True
        except:
            pass
        return False

    @classmethod
    def get_python(cls):
        """
        Returns python path (for running the synchronization script)
        """
        if cls._CACHED_WORKING_PYTHON is None:
            # Try to use system default's python3
            if not cls.test_python(shutil.which('python3'), cache_if_successful=True):
                sublime.error_message(
                    '''Cannot find a valid Python interpreter.
                    Please set the python setting in your LaTeXTools
                    settings.'''.strip()
                )
                raise Exception('Cannot find a valid interpreter')
        return cls._CACHED_WORKING_PYTHON

    def launch_sync_script(self, pdf_file, spawn=False, forward_sync=None, backward_sync=False, wait_completion=False,
                           wait_timeout=1.):
        """
        :param pdf_file: Path to the pdf file to open
        :param spawn: If True, the pdf file will be opened if it wasn't already.
        :param forward_sync: If specified, path to the source tex file, optionally including line and column, to
            perform a forward synchronization (e.g. `my_tex_file.tex:42:1`)
        :param backward_sync: If True, the process will stay alive and monitor for backward sync from the viewer
        :param wait_completion: If True, the method will wait up to `wait_timeout` seconds for the subprocess completion
            and kill it if it does not complete by then.
        :param wait_timeout: Relavant only if `wait_completion` is True; timeout in seconds to wait for the process to
            terminate before killing it.
        :returns: Popen object.
        """
        linux_settings = get_setting('linux', {})
        # Find the python version to use
        python_bin = shutil.which(linux_settings.get('python', None))
        if python_bin is None:
            python_bin = self.get_python()
        # Find the sync script
        sync_script = os.path.normpath(os.path.join(os.path.dirname(__file__), '../dbus_viewers/sync'))
        # Find the sublime text version
        st_binary = get_sublime_exe()
        if st_binary is None:
            st_binary = linux_settings.get('sublime', 'sublime_text')
        # Further settings
        sync_wait = linux_settings.get('sync_wait', 0.5)

        cmd = [python_bin, sync_script, '--document', pdf_file, '--dbus-name', self._app_dbus_name]
        if spawn:
            cmd.append('--spawn')
        if forward_sync is not None:
            cmd += ['--sync-wait', str(sync_wait),
                    '--forward', str(forward_sync)]
        if backward_sync:
            cmd += ['--backward', st_binary, '%f:%l:%c']
        p = external_command(cmd, shell=False, use_texpath=False, stdin=None, stdout=None, stderr=None)
        if wait_completion:
            try:
                # Make sure you wait at least the sync-wait timeout
                p.wait(wait_timeout + sync_wait)
            except TimeoutError:
                p.kill()
        return p

    def is_monitor_process_running(self, pdf_file):
        p = self._monitor_processes.get(pdf_file, None)
        # Poll the return code, if None, the process is still running
        return p is not None and p.poll() is None

    def launch_monitor_process(self, pdf_file, forward_sync=None):
        """
        Replaces the existing monitor process (if present) with a new one, launched in such a way to have backward
        sync enabled. Optionally performs also a forward sync.
        :param pdf_file: Path to the pdf file
        :param forward_sync: If specified, path to the source tex file, optionally including line and column, to
            perform a forward synchronization (e.g. `my_tex_file.tex:42:1`)
        """
        # Terminate existing monitor process
        old_process = self._monitor_processes.get(pdf_file, None)
        if old_process is not None and old_process.poll() is None:
            old_process.terminate()
        else:
            old_process = None  # Discard it, we will check it has terminated later sending SIGKILL if necessary

        # Run and replace the monitor process
        self._monitor_processes[pdf_file] = self.launch_sync_script(
            pdf_file, spawn=False, forward_sync=forward_sync, backward_sync=True, wait_completion=False)

        if old_process and old_process.poll() is None:
            old_process.kill()

    def forward_sync(self, pdf_file, tex_file, line, col, **kwargs):
        forward_sync_target = '%s:%d:%d' % (tex_file, line, col)
        # Do not launch the monitor process with the forward sync option, launch it separately so you can wait for
        # completion, and refocus ST.
        if not self.is_monitor_process_running(pdf_file):
            self.launch_monitor_process(pdf_file)
        # Bring forward after spawning and syncing
        if self.should_bring_viewer_forward():
            self.launch_bring_viewer_forward(pdf_file)
        # Do not wait for completion, focus_st already schedules asynchronously to return the focus.
        self.launch_sync_script(pdf_file, spawn=True, forward_sync=forward_sync_target,
                                backward_sync=False, wait_completion=False)
        if kwargs.pop('keep_focus', True):
            self.focus_st()

    def view_file(self, pdf_file, **kwargs):
        if not self.is_monitor_process_running(pdf_file):
            self.launch_monitor_process(pdf_file)
        if self.should_bring_viewer_forward():
            self.launch_bring_viewer_forward(pdf_file)
        else:
            # Do not wait for completion, focus_st already schedules asynchronously to return the focus.
            self.launch_sync_script(pdf_file, spawn=True, forward_sync=None, backward_sync=False, wait_completion=False)
        if kwargs.pop('keep_focus', True):
            self.focus_st()

    def supports_platform(self, platform):
        return platform == 'linux'

    def supports_keep_focus(self):
        return True
