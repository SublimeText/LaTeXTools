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
		root = getTeXRoot.get_tex_root(self.view.file_name())
		print "!TEX root = ", root
		rootName, rootExt = os.path.splitext(root)
		pdffile = rootName + u'.pdf'
		(line, col) = self.view.rowcol(self.view.sel()[0].end())
		print "Jump to: ", line,col
		# column is actually ignored up to 0.94
		# HACK? It seems we get better results incrementing line
		line += 1
		# the last params are flags. In part. the last is 0 if no focus, 1 to focus

		# platform-specific code:
		plat = sublime_plugin.sys.platform
		if plat == 'darwin':
			subprocess.call(["/Applications/Skim.app/Contents/SharedSupport/displayline", 
								"-g", "-r", str(line), pdffile, srcfile])
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
			command = "[ForwardSearch(\"%s\",\"%s\",%d,%d,0,0)]" % (pdffile, srcfile, line, col)
			print command
			self.view.run_command("send_dde",
					{ "service": "SUMATRA", "topic": "control", "command": command})
		else: # Linux
			pass