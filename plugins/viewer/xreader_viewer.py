from __future__ import annotations
from ...latextools.utils.settings import get_setting

from base_dbus_viewer import BaseDBusViewer


class XreaderViewer(BaseDBusViewer):
    def should_bring_viewer_forward(self) -> bool:
        return get_setting('viewer_settings', {}).get('bring_forward', False)

    def __init__(self):
        super(XreaderViewer, self).__init__('org.x.reader', 'xreader')
