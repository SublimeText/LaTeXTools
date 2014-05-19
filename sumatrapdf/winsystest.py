# coding=utf-8
import os.path, subprocess

#
# Factor out invoking Windows console programs
#

def winsys(cmd, capture=True, shell=False):

	print("Running winsys: "); print(cmd); print(capture)
	startupinfo = subprocess.STARTUPINFO()
#	startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	# proc = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
	# 			startupinfo=startupinfo, creationflags=subprocess.CREATE_NEW_CONSOLE)
	if capture:
		out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=shell,
			startupinfo=startupinfo, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP).decode('UTF-8', 'ignore') #guess.
	else:
		out = ""
		subprocess.check_call(cmd, startupinfo=startupinfo, shell=shell)
	# Popen returns a byte stream, i.e. a single line. So test simply:
	# Wait! ST3 is stricter. We MUST convert to str
	
	print(out)
	return out


if __name__ == '__main__':
	
	texFile = u"C:\\Users\\Marciano\\Documents\\temp\\sublimeTests\\citeTest-ünicôde"
	quotes = "\""
	srcfile = texFile + u'.tex'
	pdffile = texFile + u'.pdf'
	(line, col) = (38, 0)
	line += 1

	ddeexec = os.path.join("C:\\Users\\Marciano\\AppData\\Roaming\\Sublime Text 3\\Packages", 
						'LaTeXTools', 'sumatrapdf', 'ddeexecute.exe')

	setfocus = 1
	# First send an open command forcing reload, or ForwardSearch won't 
	# reload if the file is on a network share
	command1 = u'[Open(\"%s\",0,%d,1)]' % (pdffile,setfocus)
	print (repr(command1))
	command2 = "[ForwardSearch(\"%s\",\"%s\",%d,%d,0,%d)]" \
				% (pdffile, srcfile, line, col, setfocus)
	print (command2)
	out = winsys([ddeexec, 'SUMATRA', 'control', command1+command2 ], capture=True, shell=True)