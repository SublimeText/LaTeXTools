# the purpose of this package is to make upgrading cleaner by ensuring that this 
# package properly cleans-up after itself, particularly to unload the "global"
# state modules on upgrade

import sublime
import sys

PACKAGE_NAME = 'LaTeXTools'

def plugin_unloaded():
    try:
        from package_control import events
    except ImportError:
        return
    else:
        if events.pre_upgrade(PACKAGE_NAME) or events.remove(PACKAGE_NAME):
            for module in ['latextools_plugin_internal']:
                module_name = get_module_name(module)
                if module_name in sys.modules:
                    del sys.modules[module_name]

if sublime.version() < '3000':
    unload_handler = plugin_unloaded

    def get_module_name(module):
        return module
else:
    def get_module_name(module):
        return '{0}.{1}'.format(PACKAGE_NAME, module)
