# -*- coding:utf-8 -*-
from __future__ import print_function
import sublime
import sublime_plugin

import subprocess as sp
import os
import json

if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
    _ST3 = False
else:
    _ST3 = True

__all__ = ['LatexGenPkgCacheCommand']

# Generates a cache for installed latex packages, classes and bst.
# Used for fill all command for \documentclass, \usepackage and
# \bibliographystyle envrioments
class LatexGenPkgCacheCommand(sublime_plugin.WindowCommand):

    def run(self):
        # Setting path
        platform_settings = sublime.load_settings(
            "LaTeXTools.sublime-settings"
        ).get(sublime.platform())
        path = platform_settings.get('texpath')
        os.environ['PATH'] = os.path.expandvars(path)

        # Search path.
        p = sp.Popen(
            "kpsewhich --show-path=tex",
            shell=True,
            stdout=sp.PIPE
        )
        pkg_path = p.communicate()[0].decode('utf-8').strip()

        p = sp.Popen(
            "kpsewhich --show-path=bst",
            shell=True,
            stdout=sp.PIPE
        )
        bst_path = p.communicate()[0].decode('utf-8').strip()

        # For installed packages.
        installed_pkg = []

        # For installed bst files.
        installed_bst = []

        # For installed class files.
        installed_cls = []

        for path in pkg_path.split(os.pathsep):
            # In OSX and Linux, there will be !! for some of the
            # results of kpsewhich strip them
            path = path.replace('!!', '')
            if not os.path.exists(path):  # Make sure path exists
                continue
            for _, _, files in os.walk(os.path.normpath(path)):
                for f in files:
                    if f.endswith('.sty'):  # Searching package files
                        installed_pkg.append(os.path.splitext(f)[0])
                    if f.endswith('.cls'):  # Searching class files
                        installed_cls.append(os.path.splitext(f)[0])

        for path in bst_path.split(os.pathsep):
            path = path.replace('!!', '')
            if not os.path.exists(path):
                continue
            for _, _, files in os.walk(os.path.normpath(path)):
                for f in files:
                    if f.endswith('.bst'):  # Searching bst files.
                        installed_bst.append(os.path.splitext(f)[0])

        # pkg_cache
        pkg_cache = {
            'pkg': installed_pkg,
            'bst': installed_bst,
            'cls': installed_cls
        }

        # For ST3, put the cache files in cache dir
        # and for ST2, put it in package dir
        if _ST3:
            cache_path = os.path.normpath(
                os.path.join(
                    sublime.cache_path(),
                    "LaTeXTools"
                ))
        else:
            cache_path = os.path.normpath(
                os.path.join(
                    sublime.packages_path(),
                    "LaTeXTools"
                ))

        if not os.path.exists(cache_path):
            os.makedirs(cache_path)

        pkg_cache_file = os.path.normpath(
            os.path.join(cache_path, 'pkg_cache.cache'))

        with open(pkg_cache_file, 'w+') as f:
            json.dump(pkg_cache, f)
