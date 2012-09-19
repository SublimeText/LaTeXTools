import sublime, sublime_plugin, os.path, subprocess, time
import getTeXRoot

# Jump to current line in PDF file

class jump_to_pdfCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		texFile, texExt = os.path.splitext(self.view.file_name())
		if texExt.upper() != ".TEX":
			sublime.error_message("%s is not a TeX source file: cannot jump." % (os.path.basename(view.fileName()),))
			return
		quotes = "\""
		srcfile = texFile + u'.tex'
		root = getTeXRoot.get_tex_root(self.view)
		print "!TEX root = ", root
		rootName, rootExt = os.path.splitext(root)
		pdffile = rootName + u'.pdf'
		(line, col) = self.view.rowcol(self.view.sel()[0].end())
		print "Jump to: ", line,col
		# column is actually ignored up to 0.94
		# HACK? It seems we get better results incrementing line
		line += 1

		# Query view settings to see if we need to keep focus or let the PDF viewer grab it
		# By default, we keep it
		keep_focus = self.view.settings().get("keep focus",True)
		print keep_focus

		# platform-specific code:
		plat = sublime_plugin.sys.platform
		if plat == 'darwin':
			options = ["-r","-g"] if keep_focus else ["-r"]
			subprocess.Popen(["/Applications/Skim.app/Contents/SharedSupport/displayline"] + 
								options + [str(line), pdffile, srcfile])
		elif plat == 'win32':
			# determine if Sumatra is running, launch it if not
			print "Windows, Calling Sumatra"
			# hide console
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			tasks = subprocess.Popen(["tasklist"], stdout=subprocess.PIPE,
					startupinfo=startupinfo).communicate()[0]
			# Popen returns a byte stream, i.e. a single line. So test simply:
			if "SumatraPDF.exe" not in tasks:
				print "Sumatra not running, launch it"
				self.view.window().run_command("view_pdf")
				time.sleep(0.5) # wait 1/2 seconds so Sumatra comes up
			setfocus = 0 if keep_focus else 1
			# First send an open command forcing reload, or ForwardSearch won't 
			# reload if the file is on a network share
			command = u'[Open(\"%s\",0,%d,1)]' % (pdffile,setfocus)
			print command
			self.view.run_command("send_dde",
					{ "service": "SUMATRA", "topic": "control", "command": command})
			# Now send ForwardSearch command
			command = "[ForwardSearch(\"%s\",\"%s\",%d,%d,0,%d)]" \
						% (pdffile, srcfile, line, col, setfocus)
			print command
			self.view.run_command("send_dde",
					{ "service": "SUMATRA", "topic": "control", "command": command})
		
		elif 'linux' in plat: # for some reason, I get 'linux2' from sys.platform
			print "Linux!"
			
			# the required scripts are in the 'evince' subdir
			ev_path = os.path.join(sublime.packages_path(), 'LaTeXTools', 'evince')
			ev_fwd_exec = os.path.join(ev_path, 'evince_forward_search')
			ev_sync_exec = os.path.join(ev_path, 'evince_sync') # for inverse search!
			#print ev_fwd_exec, ev_sync_exec
			
			# Run evince if either it's not running, or if focus PDF was toggled
			# Sadly ST2 has Python <2.7, so no check_output:
			running_apps = subprocess.Popen(['ps', '-xw'], stdout=subprocess.PIPE).communicate()[0]
			#print running_apps
			if (not keep_focus) or (not ("evince " + pdffile in running_apps)):
				print "(Re)launching evince"
				subprocess.Popen([ev_sync_exec, pdffile], cwd=ev_path)
				time.sleep(0.5)
			subprocess.Popen([ev_fwd_exec, pdffile, str(line), srcfile])
		else: # ???
			pass