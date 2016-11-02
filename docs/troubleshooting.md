# Troubleshooting

## System Check

To aid in troubleshooting a range of issues, we have added a feature that wil check your current system setup to give you an idea of what your current configuration looks like to LaTeXTools. In particular, it tests for key environment variables, the availability of key executables, the selected builder and the selected viewer. This command can be run by invoking **LaTeXTools: Check system** from the **Command Palette**. If it is run with a LaTeX document as the visible window, the information provided will reflect the settings for the current project.

## Path issues

Many LaTeXTools problems are path-related. The `LaTeXTools.sublime-settings` file attempts to set up default path locations for MiKTeX, TeXLive and MacTeX, but these are not guaranteed to cover all possibilities. Please let me know if you have any difficulties.

On Mac OS X, just having your `$PATH` set up correctly in a shell (i.e., in Terminal) does *not* guarantee that things will work when you invoke commands from ST. If something seems to work when you invoke `pdflatex` or `latexmk` from the Terminal, but building from within ST fails, you most likely have a path configuration issue. One way to test this is to launch ST from the Terminal, typing

	/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl

(and then Return; this is for ST23of course) at the prompt. If things do work when you run ST this way, but they fail if you launch ST from the Dock or the Finder, then there is a path problem. From the Terminal, type

	echo $PATH

and take note of what you get. Then, run ST from the Dock or Finder, open the console (with ``Ctrl+ ` ``) and type
	
	import os; os.environ['PATH']

and again take note of what you see in the output panel (right above the line where you typed the above command). Finally, look at the `texpath` keyword in the `osx` section of the `LaTeXTools.sublime-settings` file  For things to work, every directory that you see listed from the Terminal must be either in the list displayed when you type the `import os...` command in the ST console, or else it must be explicitly specified in the `texpath` setting found in `LaTeXTools.sublime-settings`. If this is not the case, add the relevant paths to the `texpath` setting and *please let me know*, so I can decide whether to add the path specification to the default build file. Thanks!

On Linux, do note that your login shell may be different from the shell that launched Sublime Text. This can mean that LaTeXTools does not inherit your `$PATH` correctly, particularly if you modify your `$PATH` in `.bash_profile` or `.bashrc` or other, shell-specific files (X Windows is run via `/bin/sh` rather than `/bin/bash`). If you have a similar problem, follow the same procedure as above, although you should launch the `sublime_text` executable from a shell.

## Non-ASCII characters and spaces in path and file names ###

Another *significant* source of issues are **Unicode characters in path and file names**. On TeXLive-based platforms, LaTeXTools tries to handle these by telling `latexmk` to `cd` to each source file's directory before running `pdflatex`. This seems to help some. However, things seem to vary by platform and locale, so we cannot make any guarantees that your Unicode path names will work. Keep in mind that TeX itself has issues with Unicode characters in file names (as a quick Google search will confirm).

Spaces in paths and file names *are* supported, but see the notes on log parsing below.

## Compilation hangs on Windows

On Windows, sometimes a build seems to succeed, but the PDF file is not updated. This is most often the case if there is a stale `pdflate`x process running; a symptom is the appearence of a file with extension `.synctex.gz(busy)`. If so, launch the Task Manager and end the `pdflatex.exe` process; if you see a `perl.exe` process, end that, too. This kind of behavior is probably a bug: LaTeXTools should be able to see that something went wrong in the earlier compilation. So, *please let use know*, and provide as much detail as you can (ideally, with a test case). Thanks!

## Log parsing issues, and good vs. bad path/file names (again!)

The log parser is fairly robust and flexible---it "understands" the log file format much, much better. This is the result of *manually* and *painstakingly* debugging a fair number of users' log files. The many possible exceptions, idiosyncrasies, warts, etc. displayed by TeX packages is mind-boggling, and the parsing code reflects this :-(

Anyway, hopefully, errors should now occur only in strange edge cases. Please *let us know on github* if you see an error message. We need a log file to diagnose the problem; please upload it to gist, dropbox, or similar, and paste a link in your message on github. Issue #104 is open for that purpose.

There are *two exceptions* to this request. First, the *xypic* package is very, very badly behaved. I have spent more time debugging log files contaminated by xypic than I have spent fixing all other issues. Seriously. Therefore, first, parsing issues are now reported as "warnings" if the xypic package is used (so compilation and previewing continues); second, I cannot promise I will fix the issue even if you report it. Thanks for your understanding. 

The second exception has to do with file and path names. In order to accommodate the many possible naming conventions across platforms and packages, as well as the different ways in which file names can occur in logs, I had to make some assumptions. The key one is that *extensions cannot contain spaces*. The reason is that the regex matching file names uses a period (".") followed by non-space characters, followed by a space as denoting the end of the file name. Trust me, it's the most robust regex I could come up with. So, you can have spaces in your base names, and you can even have multiple extensions; however, you cannot have spaces in your extensions. So, "This is a file.ver-1.tex" is OK; "file.my ext" (where "my ext" is supposed to be the extension) is *not OK*.

Finally, I have done my best to accommodate non-ASCII characters in logs. I cannot promise that everything works, but I'd like to know if you see issues with this.

## Other issues

While we have tried to provide some guidance in this section on commonly-encountered issues, please feel free to [open a new issue](https://github.com/SublimeText/LaTeXTools/issues/new) if you have come across an issue with LaTeXTools. However, please [search for existing issue](https://github.com/SublimeText/LaTeXTools/issues/?q=is%3Aopen) before opening a new one, as we may have already covered it somewhere.
