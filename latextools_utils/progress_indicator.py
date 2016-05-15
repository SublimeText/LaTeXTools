# Note modified from code licensed as follows:

# Copyright (c) 2011-2015 Will Bond <will@wbond.net>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import sublime
import threading


class ProgressIndicator():

    """
    Animates an indicator, [=   ], in the status area while a thread runs

    :param thread:
        The thread to track for activity

    :param message:
        The message to display next to the activity indicator

    :param success_message:
        The message to display once the thread is complete
    """

    def __init__(self, thread, message, success_message, **kwargs):
        self.thread = thread
        self.message = message
        self._success_message = success_message
        self._success_message_lock = threading.RLock()
        self.display_message_length = kwargs.get(
            'display_message_length', 1000
        )

        if self.display_message_length < 0:
            self.display_message_length = 1000

        self.addend = 1
        self.size = 8
        self.last_view = None
        self.window = None
        sublime.set_timeout(lambda: self.run(0), 100)

    def run(self, i):
        if self.window is None:
            self.window = sublime.active_window()
        active_view = self.window.active_view()

        if self.last_view is not None and active_view != self.last_view:
            self.last_view.erase_status('_latextools')
            self.last_view = None

        if not self.thread.is_alive():
            def cleanup():
                active_view.erase_status('_latextools')
            if hasattr(self.thread, 'result') and not self.thread.result:
                cleanup()
                return
            with self._success_message_lock:
                active_view.set_status('_latextools', self.success_message)

            sublime.set_timeout(cleanup, self.display_message_length)
            return

        before = i % self.size
        after = (self.size - 1) - before

        active_view.set_status(
            '_latextools',
            '{0} [{1}={2}]'.format(self.message, ' ' * before, ' ' * after)
        )
        if self.last_view is None:
            self.last_view = active_view

        if not after:
            self.addend = -1
        if not before:
            self.addend = 1
        i += self.addend

        sublime.set_timeout(lambda: self.run(i), 100)

    @property
    def success_message(self):
        with self._success_message_lock:
            return self._success_message

    @success_message.setter
    def success_message(self, success_message):
        with self._success_message_lock:
            self._success_message = success_message
