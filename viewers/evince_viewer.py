from base_dbus_viewer import BaseDBusViewer
from latextools_utils import get_setting


class EvinceViewer(BaseDBusViewer):
    def should_bring_viewer_forward(self):
        viewer_settings = get_setting('viewer_settings', {})
        return viewer_settings.get('bring_forward', viewer_settings.get('bring_evince_forward', False))

    def __init__(self):
        super(EvinceViewer, self).__init__('org.gnome.evince', 'evince')
