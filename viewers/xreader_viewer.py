from base_dbus_viewer import BaseDBusViewer
from latextools_utils import get_setting


class XreaderViewer(BaseDBusViewer):
    def should_bring_viewer_forward(self):
        return get_setting('viewer_settings', {}).get('bring_forward', False)

    def __init__(self):
        super(XreaderViewer, self).__init__('org.x.reader', 'xreader')
