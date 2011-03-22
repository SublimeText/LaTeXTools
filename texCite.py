import sublime, sublimeplugin, os, os.path, re

# References and citations

class TexCiteCommand(sublimeplugin.TextCommand):
	def run(self, view, args):
		print "entering texCite"
		# test only for now
		# get current point
		# assume no selection, or a singe selection (for now)
		currsel = view.sel()[0]
		point = currsel.b
		prefix = view.substr(view.word(point)).strip()
		print currsel, point, prefix,len(prefix)
		completions = []
		# For now we only get completions from bibtex file
		bibcmd = view.substr(view.find(r'\\bibliography\{(.+)\}',0))
		print bibcmd
		bibp = re.compile(r'\{(.+)\}')
		bibmatch = bibp.search(bibcmd)
		if not bibmatch:
			print "Cannot parse bibliography command: " + bibcmd
			return
		bibfname = bibmatch.group(1)
		print bibfname
		if bibfname[-4:] != ".bib":
			bibfname = bibfname + ".bib"
		texfiledir = os.path.dirname(view.fileName())
		bibfname = os.path.normpath(texfiledir + os.path.sep + bibfname)
		print bibfname 
		try:
			bibf = open(bibfname)
		except IOError:
			sublime.errorMessage("Cannot open bibliography file %s !" % (bibfname,))
			return
		else:
			bib = bibf.readlines()
			bibf.close()
		kp = re.compile(r'@[^\{]+\{(.+),')
		tp = re.compile(r'\btitle\s*=\s*(.+)', re.IGNORECASE)
		kp2 = re.compile(r'([^\t]+)\t*')
		keywords = [kp.search(line).group(1) for line in bib if line[0] == '@']
		titles = [tp.search(line).group(1) for line in bib if tp.search(line)]
		if len(keywords) != len(titles):
			print "Bibliography " + bibfname + " is broken!"
		completions = ["%s\t\t%s" % kt for kt in zip(keywords, titles)]
		# need ",}" for multiple citations
		# support is limited: this only OK if there is no prefix after the
		# comma.
		multicites = False
		if not prefix in ["", "{}", ",}"]:
			fcompletions = [comp for comp in completions if prefix in comp]
		else:
			if prefix == ",}":
				multicites = True
			prefix = "" # in case it's {}
			fcompletions = completions
		# are there any completions?
		if len(fcompletions) == 0:
			sublime.errorMessage("No bibliography keys start with %s!" % (prefix,))
			return
		
		def onSelect(i):
			key = kp2.search(fcompletions[i]).group(1)
			# if no selection, and current character is not space, 
			# extend to word
			# Note: we crash if currsel.a=0, but that means that we are trying
			# to enter a reference as the very first character of the file!
			if currsel.a == currsel.b and view.substr(currsel.a-1) != ' ': 
				newsel = view.word(point)
			else:
				newsel = currsel
			view.erase(newsel)
			# Use all-powerful insertInlineSnippet! woot!
			# Note: must escape '\' twice
			if not multicites:
				snippet = "\\\\${1:cite}{" + key + "} $0"
			else:
				snippet = "," + key + "}"
			view.runCommand('insertInlineSnippet', [snippet])
			
		if len(fcompletions) == 1:
			onSelect(0)
		else:
			view.window().showSelectPanel(fcompletions, onSelect, None, 0)
		print "done"