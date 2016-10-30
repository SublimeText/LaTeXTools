# This file is used to conditionally load plugins in Sublime Text
# to support different Sublime Text Versions.
import imp

import sublime

_load_modules = []


def _load_module_exports(module):
    for name in module.exports:
        try:
            # lift the export to this modules top level
            globals()[name] = module.__dict__[name]
        except KeyError:
            print(
                "Error: {0} not defined in {1}."
                .format(name, module.__name__)
            )


# 3118 has phantoms, ViewListener and hover effects
if sublime.version() >= "3118":

    # load the preview modules
    from .st_preview import preview_math
    _load_modules.append(preview_math)
    from .st_preview import preview_image
    _load_modules.append(preview_image)


# reload all modules
for module in _load_modules:
    imp.reload(module)

# lift the module exports to the top level
for module in _load_modules:
    if "exports" in module.__dict__:
        _load_module_exports(module)


def plugin_loaded():
    for module in _load_modules:
        try:
            module.plugin_loaded()
        except AttributeError:
            pass


def plugin_unloaded():
    for module in _load_modules:
        try:
            module.plugin_unloaded()
        except AttributeError:
            pass
