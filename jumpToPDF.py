import sublime, sublime_plugin, os.path, subprocess

# Jump to current line in PDF file

class jump_to_pdfCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		texFile, texExt = os.path.splitext(self.view.file_name())
		if texExt.upper() != ".TEX":
			sublime.error_message("%s is not a TeX source file: cannot jump." % (os.path.basename(view.fileName()),))
			return
		quotes = "\""
		srcfile = texFile + u'.tex'
		pdffile = texFile + u'.pdf'
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
			print "Windows, Calling Sumatra"
			command = "[ForwardSearch(\"%s\",\"%s\",%d,%d,0,0)]" % (pdffile, srcfile, line, col)
			print command
			self.view.run_command("send_dde",
					{ "service": "SUMATRA", "topic": "control", "command": command})
		else: # Linux
			pass