import json
import os
import sublime
import shutil
import tempfile

if sublime.version() < '3000':
    def get_cache_directory():
        return os.path.join(
            sublime.packages_path(),
            'User',
            '.lt_cache'
        )

    strbase = basestring
else:
    def get_cache_directory():
        return os.path.join(
            sublime.cache_path(),
            'LaTeXTools'
        )

    strbase = str


# unfortunately, there is no reliable way to do clean-up on exit in ST
# see https://github.com/SublimeTextIssues/Core/issues/10
# here we cleanup any directories listed in the temporary_output_dirs
# file as having been previously created by the plugin

def plugin_loaded():
    temporary_output_dirs = os.path.join(
        get_cache_directory(),
        'temporary_output_dirs'
    )

    if os.path.exists(temporary_output_dirs):
        with open(temporary_output_dirs, 'r') as f:
            data = json.load(f)

        tempdir = tempfile.gettempdir()

        try:
            for directory in data['directories']:
                # shutil.rmtree is a rather blunt tool, so here we try to
                # ensure we are only deleting legitimate temporary files
                if (
                    directory is None or
                    not isinstance(directory, strbase) or
                    not directory.startswith(tempdir)
                ):
                    continue

                try:
                    shutil.rmtree(directory)
                except OSError:
                    pass
                else:
                    print(u'Deleted old temp directory ' + directory)
        except KeyError:
            pass

        try:
            os.remove(temporary_output_dirs)
        except OSError:
            pass

if sublime.version() < '3000':
    plugin_loaded()
