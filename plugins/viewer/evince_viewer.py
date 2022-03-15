from __future__ import annotations
import os
import shutil

from ...latextools.utils.settings import get_setting

from base_dbus_viewer import BaseDBusViewer


class EvinceViewer(BaseDBusViewer):
    def should_bring_viewer_forward(self) -> bool:
        viewer_settings = get_setting('viewer_settings', {})
        return viewer_settings.get('bring_forward', viewer_settings.get('bring_evince_forward', False))

    def __init__(self):
        # On Mint /usr/bin/evince symlinks to xreader; in that case we need to use the right dbus name
        dbus_name = 'org.gnome.evince'

        evince_exe_name = shutil.which('evince')
        if evince_exe_name is not None:
            evince_exe_name = os.path.basename(os.path.realpath(evince_exe_name))
            if evince_exe_name == 'xreader':
                print('On this platform, Xreader provides Evince, will use Xreader DBus name')
                dbus_name = 'org.x.reader'

        super(EvinceViewer, self).__init__(dbus_name, 'evince')
