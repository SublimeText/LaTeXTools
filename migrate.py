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
#import sys
#import imp
import os, os.path
import shutil
#import threading
#import functools
#import subprocess
#import types
import re
import codecs

DEBUG = False

# Copy settings from default file to user directory
# Try to incorporate existing user settings

DEFAULT_SETTINGS = "LaTeXTools.sublime-settings"
USER_SETTINGS = "LaTeXTools.sublime-settings"
OLD_SETTINGS = "LaTeXTools Preferences.sublime-settings"

# Settings to be ported over
# "key" is the preference key
# "type" is the type, for fixups (e.g. true vs. True)
# "line" is the line in the .default-settings file (starting from 0, not 1);
#        the code below looks for it, but set to -1 to flag errors, issues, etc.
# "tabs" is the number of tabs before the key
# "last" is True if it's the last line in a {...} block (so must omit comma at the end)
# WARNING: obviously, this works ONLY with a known default-settings file.
settings = [	{"key": "cite_auto_trigger", "type": "bool", "line": -1, "tabs": 1, "last": False},
				{"key": "ref_auto_trigger", "type": "bool", "line": -1, "tabs": 1, "last": False},
				{"key": "keep_focus", "type": "bool", "line": -1, "tabs": 1, "last": False},
				{"key": "forward_sync", "type": "bool", "line": -1, "tabs": 1, "last": False},
				{"key": "python2", "type": "string", "line": -1, "tabs": 2, "last": False},
				{"key": "sublime", "type": "string", "line": -1, "tabs": 2, "last": False},
				{"key": "sync_wait", "type": "num", "line": -1, "tabs": 2, "last": True},
				{"key": "cite_panel_format", "type": "list", "line": -1, "tabs": 1, "last": False },
				{"key": "cite_autocomplete_format", "type": "string", "line": -1, "tabs": 1, "last": True}
				]

class latextoolsMigrateCommand(sublime_plugin.ApplicationCommand):

	def run(self):
		
		# First of all, try to load new settings
		# If they exist, either the user copied them manually, or we already did this
		# Hence, quit
		# NOTE: we will move this code somewhere else, but for now, it's here

		print ("Running settings reset")
		sublime.status_message("Resetting user settings to default...")
		ltt_path = os.path.join(sublime.packages_path(),"LaTeXTools")
		user_path = os.path.join(sublime.packages_path(),"User")
		default_file = os.path.join(ltt_path,DEFAULT_SETTINGS)
		user_file = os.path.join(user_path,USER_SETTINGS)
		old_file = os.path.join(user_path,OLD_SETTINGS)

		killall = False # So final message check works even if there is no existing setting file
		if os.path.exists(user_file):
			killall = sublime.ok_cancel_dialog(USER_SETTINGS + " already exists in the User directory!\n"
				"Are you sure you want to DELETE YOUR CURRENT SETTINGS and reset them to default?",
				"DELETE current settings")
			if not killall:
				sublime.message_dialog("OK, I will preserve your existing settings.")
				return
		
		with codecs.open(default_file,'r','UTF-8') as def_fp:
			def_lines = def_fp.readlines()

		quotes = "\""

		# Find lines where keys are in the default file
		comments = False
		for i in range(len(def_lines)):
			l = def_lines[i].strip() # Get rid of tabs and leading spaces
			# skip comments
			# This works as long as multiline comments do not start/end on a line that
			# also contains code.
			# It's also safest if a line with code does NOT also contain comments
			beg_cmts = l[:2]
			end_cmts = l[-2:]
			if comments:
				if beg_cmts == "*/":
					comments = False
					l = l[2:] # and process the line just in case
				elif end_cmts == "*/":
					comments = False
					continue
				else: # HACK: this fails if we have "...*/ <code>", which however is bad form
					continue
			if beg_cmts=="//": # single-line comments
				continue
			if beg_cmts=="/*": # Beginning of multiline comment.
				comments = True # HACK: this fails if "<code> /* ..." begins a multiline comment
				continue
			for s in settings:
				# Be conservative: precise match.
				m = quotes + s["key"] + quotes + ":"
				if m == l[:len(m)]:
					s["line"] = i
					print(s["key"] + " is on line " + str(i) + " (0-based)")

		# Collect needed modifications
		def_modify = {}
		s_old = sublime.load_settings(OLD_SETTINGS)
		for s in settings:
			key = s["key"]
			print("Trying " + key)
			s_old_entry = s_old.get(key)
			if s_old_entry is not None: # Checking for True misses all bool's set to False!
				print("Porting " + key)
				l = s["tabs"]*"\t" + quotes + key + quotes + ": "
				if s["type"]=="bool":
					l += "true" if s_old_entry==True else "false"
				elif s["type"]=="num":
					l += str(s_old_entry)
				elif s["type"]=="list": # HACK HACK HACK! List of strings only!
					l += "["
					for el in s_old_entry:
						l += quotes + el + quotes + ","
					l = l[:-1] + "]" # replace last comma with bracket
				else:
					l += quotes + s_old_entry + quotes
				if s["last"]: # Add comma, unless at the end of a {...} block
					l+= "\n"
				else:
					l += ",\n"
				print(l)
				def_lines[s["line"]] = l

		# Modify text saying "don't touch this!" in the default file
		def_lines[0] = '// LaTeXTools Preferences\n'
		def_lines[2] = '// Keep in the User directory. Personalize as needed\n'
		for i in range(3,10):
			def_lines.pop(3) # Must be 3: 4 becomes 3, then 5 becomes 3...

		with codecs.open(user_file,'w','UTF-8') as user_fp:
			user_fp.writelines(def_lines)

		if killall:
			msg_preserved = ""
		else:
			msg_preserved = "Old-style, pre-2014 settings (if any) have been migrated."
		sublime.status_message("Settings reset to default.")
		sublime.message_dialog("LaTeXTools settings successfully reset to default. " + msg_preserved)
		return

