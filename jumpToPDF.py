# ST2/ST3 compat
from __future__ import print_function 
import sublime
from functools import partial
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
	import getTeXRoot
else:
	_ST3 = True
	from . import getTeXRoot


import sublime_plugin, os.path, subprocess, time

# attempts to locate the sublime executable to refocus on ST if keep_focus
# is set.
def get_sublime_executable():
	s = sublime.load_settings('LaTeXTools.sublime-settings')
	sublime_executable = sublime.active_window().active_view().\
		settings().get('sublime_executable',
			s.get('sublime_executable', None))

	if sublime_executable is not None:
		return sublime_executable

	# we cache the results of the other checks, if possible
	if hasattr(get_sublime_executable, 'result'):
		return get_sublime_executable.result

	# are we on ST3
	if hasattr(sublime, 'executable_path'):
		get_sublime_executable.result = sublime.executable_path()
		return get_sublime_executable.result

	# guess-work for ST2
	startupinfo = None
	shell = False
	if sublime.platform() == 'windows':
		startupinfo = subprocess.STARTUPINFO()
		startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		shell = True

	if subprocess.call(
			['subl', '-v'],
			startupinfo=startupinfo,
			shell=shell,
			env=os.environ
		) == 0:
		get_sublime_executable.result = 'subl'
		return get_sublime_executable.result

	if subprocess.call(
			['sublime_text', '-v'],
			startupinfo=startupinfo,
			shell=shell,
			env=os.environ
		) == 0:
		get_sublime_executable.result = 'sublime_text'
		return get_sublime_executable.result

	get_sublime_executable.result = None

	sublime.status_message(
		'Cannot determine the path to your Sublime installation. Please ' +
		'set the "sublime_executable" setting in your LaTeXTools.sublime-settings ' +
		'file.'
	)

	return None


# Jump to current line in PDF file
# NOTE: must be called with {"from_keybinding": <boolean>} as arg

class jump_to_pdfCommand(sublime_plugin.TextCommand):

	def focus_st(self):
		sublime_command = get_sublime_executable()

		if sublime_command is not None:
			s = sublime.load_settings('LaTeXTools.sublime-settings')
			wait_time = view.settings().get('keep_focus_delay',
				s.get('keep_focus_delay', 500))

			def keep_focus():
				startupinfo = None
				shell = False
				if sublime.platform() == 'windows':
					startupinfo = subprocess.STARTUPINFO()
					startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
					shell = True

				subprocess.call(
					sublime_command,
					startupinfo=startupinfo,
					shell=shell,
					env=os.environ
				)

			if hasattr(sublime, 'set_async_timeout'):
				sublime.set_async_timeout(keep_focus, wait_time)
			else:
				sublime.set_timeout(keep_focus, wait_time)

	def run(self, edit, **args):
		# Check prefs for PDF focus and sync
		s = sublime.load_settings("LaTeXTools.sublime-settings")
		prefs_keep_focus = s.get("keep_focus", True)
		keep_focus = self.view.settings().get("keep focus",prefs_keep_focus)
		prefs_forward_sync = s.get("forward_sync", True)
		forward_sync = self.view.settings().get("forward_sync",prefs_forward_sync)

		prefs_lin = s.get("linux")
		prefs_win = s.get("windows")

		# If invoked from keybinding, we sync
		# Rationale: if the user invokes the jump command, s/he wants to see the result of the compilation.
		# If the PDF viewer window is already visible, s/he probably wants to sync, or s/he would have no
		# need to invoke the command. And if it is not visible, the natural way to just bring up the
		# window without syncing is by using the system's window management shortcuts.
		# As for focusing, we honor the toggles / prefs.
		from_keybinding = args["from_keybinding"] if "from_keybinding" in args else False
		if from_keybinding:
			forward_sync = True
		print (from_keybinding, keep_focus, forward_sync)

		texFile, texExt = os.path.splitext(self.view.file_name())
		if texExt.upper() != ".TEX":
			sublime.error_message("%s is not a TeX source file: cannot jump." % (os.path.basename(view.fileName()),))
			return
		quotes = "\""
		srcfile = texFile + u'.tex'
		root = getTeXRoot.get_tex_root(self.view)
		print ("!TEX root = ", repr(root) ) # need something better here, but this works.
		rootName, rootExt = os.path.splitext(root)
		pdffile = rootName + u'.pdf'
		(line, col) = self.view.rowcol(self.view.sel()[0].end())
		print ("Jump to: ", line,col)
		# column is actually ignored up to 0.94
		# HACK? It seems we get better results incrementing line
		line += 1

		# Query view settings to see if we need to keep focus or let the PDF viewer grab it
		# By default, we respect settings in Preferences
		

		# platform-specific code:
		plat = sublime_plugin.sys.platform
		if plat == 'darwin':
			options = ["-r","-g"] if keep_focus else ["-r"]		
			if forward_sync:
				path_to_skim = '/Applications/Skim.app/'
				if not os.path.exists(path_to_skim):
					path_to_skim = subprocess.check_output(
						['osascript', '-e', 'POSIX path of (path to app id "net.sourceforge.skim-app.skim")']
					).decode("utf8")[:-1]
				subprocess.Popen([os.path.join(path_to_skim, "Contents/SharedSupport/displayline")] + 
								  options + [str(line), pdffile, srcfile])
			else:
				skim = os.path.join(sublime.packages_path(),
								'LaTeXTools', 'skim', 'displayfile')
				subprocess.Popen(['sh', skim] + options + [pdffile])
		elif plat == 'win32':
			# determine if Sumatra is running, launch it if not
			print ("Windows, Calling Sumatra")

			si = subprocess.STARTUPINFO()
			if setfocus == 0:
				si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
				si.wShowWindow = 4 #constant for SHOWNOACTIVATE

			su_binary = prefs_win.get("sumatra", "SumatraPDF.exe") or 'SumatraPDF.exe'
			startCommands = [su_binary, "-reuse-instance"]
			if forward_sync:
				startCommands.append("-forward-search")
				startCommands.append(srcfile)
				startCommands.append(str(line))

			startCommands.append(pdffile)

			subprocess.Popen(startCommands, startupinfo = si)

			if keep_focus:
				self.focus_st()
		elif 'linux' in plat: # for some reason, I get 'linux2' from sys.platform
			print ("Linux!")
			
			# the required scripts are in the 'evince' subdir
			ev_path = os.path.join(sublime.packages_path(), 'LaTeXTools', 'evince')
			ev_fwd_exec = os.path.join(ev_path, 'evince_forward_search')
			ev_sync_exec = os.path.join(ev_path, 'evince_sync') # for inverse search!
			#print ev_fwd_exec, ev_sync_exec
			
			# Run evince if either it's not running, or if focus PDF was toggled
			# Sadly ST2 has Python <2.7, so no check_output:
			running_apps = subprocess.Popen(['ps', 'xw'], stdout=subprocess.PIPE).communicate()[0]
			# If there are non-ascii chars in the output just captured, we will fail.
			# Thus, decode using the 'ignore' option to simply drop them---we don't need them
			running_apps = running_apps.decode(sublime_plugin.sys.getdefaultencoding(), 'ignore')
			
			# Run scripts through sh because the script files will lose their exec bit on github

			# Get python binary if set:
			py_binary = prefs_lin["python2"] or 'python'
			sb_binary = prefs_lin["sublime"] or 'sublime-text'
			# How long we should wait after launching sh before syncing
			sync_wait = prefs_lin["sync_wait"] or 1.0

			evince_running = ("evince " + pdffile in running_apps)
			if (not keep_focus) or (not evince_running):
				print ("(Re)launching evince")
				subprocess.Popen(['sh', ev_sync_exec, py_binary, sb_binary, pdffile], cwd=ev_path)
				print ("launched evince_sync")
				if not evince_running: # Don't wait if we have already shown the PDF
					time.sleep(sync_wait)
			if forward_sync:
				subprocess.Popen([py_binary, ev_fwd_exec, pdffile, str(line), srcfile])
			if keep_focus:
				self.focus_st()
		else: # ???
			pass