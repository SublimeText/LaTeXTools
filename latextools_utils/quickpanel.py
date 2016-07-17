"""
The MIT License (MIT)

Copyright (c) 2016 Richard Stein

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files
(the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import sublime

_ST3 = sublime.version() >= '3000'

if _ST3:
    from .utils import run_after_loading
else:
    from latextools_utils.utils import run_after_loading

# positions to add items
AT_START, AT_END = -1, -2


def show_quickpanel(captions, entries, show_cancel=False):
    """
    Creates a panel to navigate between the entries.
    Each entry can either be a class or a dict, but must have the
    properties:
    - file_name the absolute path to the file, which contain the entry
    - region the region inside the file as sublime.Region

    Arguments:
    captions -- The captions to display for each entry
    entries -- A list of the entries inside the quickpanel
    show_cancel -- Whether a cancel option should be added
    """
    if show_cancel:
        Quickpanel = CancelEntriesQuickpanel
    else:
        Quickpanel = EntriesQuickpanel
    Quickpanel(captions, entries).show_quickpanel()


def _convert_entries(entries):
    if any(isinstance(entry, dict) for entry in entries):
        entries = [Entry(**entry) if isinstance(entry, dict) else entry
                   for entry in entries]
    return entries


class Entry():
    """
    Duck type to show entries in a quickpanel, consists of
    - the file_name as str
    - the region as sublime.Region
    """
    def __init__(self, file_name, region, **kwargs):
        """
        Arguments
        file_name -- the name of the file of the entry
        region -- the sublime.Region inside the file
        """
        self.file_name = file_name
        self.region = region
        self.start = self.region.begin()
        self.end = self.region.end()


class EntriesQuickpanel(object):
    """
    A Class to show latex commands in a quickpanel
    """
    def __init__(self, captions, entries):
        # store all necessary values
        self.window = sublime.active_window()
        self.view = self.window.active_view()
        self.captions = captions
        self.entries = entries
        self.viewport_position = self.view.viewport_position()

        # can be used to add own entries to the list in a subclass
        # entries below the offset will have a special treatment defined by
        # the handlers
        self._offset = 0

        # Handlers for subclasses, who adds own list entries
        self.change_handler = {}
        self.done_handler = {}

    def add_item(self, position, name, done_handler=None, change_handler=None):
        """
        Adds an item to the list in the overlay before the entries.

        Arguments:
        position -- The position where to add the item. This must be before
            the content. The use of AT_START and AT_END is recommended
        name -- The caption of the item. Must be unique for all non-entries.
        done_handler -- This handler will be executed, when the item is
            selected and affirmed.
        change_handler -- This handler will be executed, when the item is
            highlighted
        """
        index = {
            AT_START: 0,
            AT_END: self._offset
        }.get(position, position)
        # force the index to be between 0 and the offset
        index = min(max(0, index), self._offset)

        self.captions.insert(index, name)
        self._offset += 1
        if done_handler:
            self.done_handler[name] = done_handler
        if change_handler:
            self.change_handler[name] = change_handler

    def show_quickpanel(self, selected_index=0):
        """
        Opens a quickpanel based on the initialized data
        """
        if _ST3:
            flags = {
                "selected_index": selected_index,
                "on_highlight": self._on_changed
            }
        else:
            flags = {}
        self.window.show_quick_panel(self.captions, self._on_done, **flags)

    def _remove_highlight(self, view=None):
        """
        Removes the highlight from the view.
        If the view None, then the highlight of the active view will be
        removed.
        """
        if not view:
            view = self.window.active_view()
        view.erase_regions("temp_highlight_command")

    def _add_highlight(self, view, region):
        """Add the highlight to the region"""
        flags = sublime.DRAW_NO_FILL
        view.add_regions("temp_highlight_command", [region], "comment",
                         flags=flags)

    def _open_transient(self, command):
        """
        Opens the file of a command in transient mode, focuses and highlights
        the region of the command
        """
        file_name = command.file_name
        v = self.window.open_file(file_name, sublime.TRANSIENT)

        # add the highlight and focus the view after it has been loading
        run_after_loading(v, lambda: self._add_highlight(v, command.region))
        run_after_loading(v, lambda: v.show(command.region))

    def _on_changed(self, index):
        """
        Handles a item change in the quickpanel:
        Calls the handler if the item is below the offset.
        Otherwise it opens the file and highlights the command.
        """
        if index < self._offset:
            # if the index is smaller than the offset
            # then it is a special entry and we execute the corresponding
            # handle
            key = self.captions[index]
            handle = self.change_handler.get(key, lambda: None)
            handle()
            return

        self._remove_highlight()
        self._open_transient(self.entries[index - self._offset])

    def _restore_viewport(self):
        """
        Restores the viewport (and file) from before the quickpanel
        """
        self._remove_highlight()

        self.window.focus_view(self.view)
        self.view.set_viewport_position(self.viewport_position, False)

    def _move_viewport(self, command):
        """
        Move the viewport to focus the region of a command.
        If the file of the command is not opened, then it will also open the
        file.
        """
        self._remove_highlight()

        # open the file (change from transient to normal)
        # we must not await the loading, because it is already open
        # due to the on_change event
        file_name = command.file_name
        view = self.window.open_file(file_name)

        def move():
            # at a caret to the section position and move the viewport
            # to the position
            view.sel().clear()
            view.sel().add(command.region)
            # view.show_at_center(command.start)
            view.show(command.start)
            # erase the regions
            self._remove_highlight(view)
        run_after_loading(view, move)

    def _on_done(self, index):
        """
        Handles a item select in the quickpanel:
        Calls the handler if the item is below the offset.
        Otherwise it opens the file and focus the command.
        """
        if index == -1:
            # if it was canceled restore the state before
            self._restore_viewport()
            return
        elif index < self._offset:
            # if the index is smaller than the offset
            # then it is a special entry and we execute the corresponding
            # handle
            self._remove_highlight()
            key = self.captions[index]
            handle = self.done_handler.get(key, lambda: None)
            handle()
            return

        self._move_viewport(self.entries[index - self._offset])


class CancelEntriesQuickpanel(EntriesQuickpanel):
    """
    A Class to show entries in a quickpanel, which adds a cancel button
    """
    def __init__(self, *args):
        super(CancelEntriesQuickpanel, self).__init__(*args)

        # add "Cancel" to the quickpanel
        # if it is pressed the initial viewport is restored
        self.add_item(AT_START, "Cancel", done_handler=self._restore_viewport,
                      change_handler=self._restore_viewport)
