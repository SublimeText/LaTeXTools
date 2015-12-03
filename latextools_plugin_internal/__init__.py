'''
This is internal global-state storage used by the latextools_plugin module

This separate module is required because STs reload semantics make it impossible
to implement something like this within that module itself.
'''
_REGISTRY = None
# list of tuples consisting of a path and a glob to load in the plugin_loaded() method
# to handle the case where `add_plugin_path` is called before this module has been fully
# loaded.
_REGISTERED_PATHS_TO_LOAD = []

# a list of tuples consisting of a module name and a module object used in the
# _latextools_modules_hack context manager to provide an API for adding modules
_WHITELIST_ADDED = []
