# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
	import getTeXRoot
	import parseTeXlog
else:
	_ST3 = True
	from . import getTeXRoot
	from . import parseTeXlog

import sublime_plugin
import sys
import imp
import os, os.path
import threading
import functools
import subprocess
import types
import re
import codecs

DEBUG = False

# Copy settings from default file to user directory
# Try to incorporate existing user settings

DEFAULT_SETTINGS = "LaTeXTools.default-settings"
USER_SETTINGS = "LaTeXTools.sublime-settings"
OLD_SETTINGS = "LaTeXTools Preferences.sublime-settings"

class migrateCommand(sublime_plugin.ApplicationCommand):

	def run(self):
		
		# First of all, try to load new settings
		# If they exist, either the user copied them manually, or we already did this
		# Hence, quit
		# NOTE: we will move this code somewhere else, but for now, it's here

		print ("Running migrate")
		s_user = sublime.load_settings(USER_SETTINGS)
		# This will always be a well-defined object. However, it may be empty.
		# To figure out if this actually exists, look for something that *must* be there
		if s_user.get("builder"):
			print(USER_SETTINGS + " already exists!")
		else:
			print(USER_SETTINGS + " does not yet exist.")

		# Get platform settings, builder, and builder settings
		s_old = sublime.load_settings(OLD_SETTINGS)
		s_def = sublime.load_settings(DEFAULT_SETTINGS)

		return # for now

		# Copy s_old into s_user
		# Save to s_user. Hopefully this will end up in the right place!
