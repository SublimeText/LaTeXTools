LaTeX Plugin for Sublime Text 2
===============================

by Marciano Siniscalchi
[http://tekonomist.wordpress.com]

Introduction
------------
This plugin provides several features that simplify working with LaTeX files:

* The ST2 build command takes care of compiling your LaTeX source to PDF using `texify` (Windows/MikTeX) or `latexmk` (OSX/MacTeX or Windows/TeXlive). Then, it parses the log file and lists errors and warning. Finally, it launches (or refreshes) the PDF viewer (SumatraPDF on Windows and Skim on OSX) and jumps to the current cursor position.
* Forward and inverse search with the named PDF previewers is fully supported
* Easy insertion of references and citations (from BibTeX files) via tab completion
* Plugs into the "Goto anything" facility to make jumping to any section or label in your LaTeX file(s)
* Smart command completion for a variety of text and math commands is provided
* Additional snippets and commands are also provided

Requirements and Setup
----------------------

First, you need to be running a recent dev version of Sublime Text 2 (ST2 henceforth); as of 11/27/2011, I am on Build 2144. 

Second, get the LaTeXTools plugin. These days, the easiest way to do so is via Package Control: see [here](http://wbond.net/sublime_packages/package_control) for details on how to set it up (it's very easy). Once you have Package Control up and running, invoke it (via the Command Palette or from Preferences), select the Install Package command, and look for LaTeXTools.

If you prefer a more hands-on approach, you can always clone the git repository, or else just grab this plugin's .zip file from GitHub and extract it to your Packages directory (you can open it easily from ST2, by clicking on Preferences|Browse Packages). Then, (re)launch ST2.

I encourage you to install Package Control anyway, because it's awesome, and it makes it easy to keep your installed packages up-to-date (see the aforelinked page for details). 

Third, follow the OS-specific instructions below.

<br>

On **OSX**, you need to be running the MacTeX distribution (which is pretty much the only one available on the Mac anyway) and the Skim PDF previewer. Just download and install these in the usual way. I have tested MacTeX versions 2010 and 2011, both 32 and 64 bits; these work fine. On the other hand, MacTeX 2008 does *not* seem to work out of the box (compilation fails), so please upgrade.

To configure inverse search, open the Preferences dialog of the Skim app, select the Sync tab, then:

* uncheck the "Check for file changes" option
* Preset: Custom
* Command: `/Applications/Sublime Text 2.app/Contents/SharedSupport/bin/subl`.
* Arguments: "%file":%line

Note: in case you have created a symlink to Sublime Text somewhere in your path, you can of course use that, too in the Command field. The above will work in any case though, and does *not* require you to create a symlink or mess with the Terminal in any way!

<br>

On **Windows**, both MikTeX and TeXlive are supported (although TeXlive support is relatively recent, as of 9/23/2011). Also, you must be running a current (>=1.4) version of the Sumatra PDF previewer. Install these as usual; then, add the SumatraPDF directory to your PATH (this requirement will be removed at some point). 

You now need to set up inverse search in Sumatra PDF. However, the GUI for doing this is hidden in Sumatra until you open a PDF file that has actual synchronization information (that is, an associated `.synctex.gz` file): see [here](http://forums.fofou.org/sumatrapdf/topic?id=2026321). If you have one such file, then open it, go to Settings|Options, and enter `"C:\Program Files\Sublime Text 2\sublime_text.exe" "%f:%l"` as the inverse-search command line (in the text-entry field at the bottom of the options dialog). If you don't already have a file with sync information, you can easily create one: compile any LaTex file you already have (or create a new one) with `pdflatex -synctex=1 <file.tex>`, and then open the resulting PDF file in SumatraPDF. 

As an alternative, you can open a command-line console (run `cmd.exe`), and issue the following command:

	sumatrapdf.exe -inverse-search "\"C:\Program Files\Sublime Text 2\sublime_text.exe\" \"%f:%l\""

(this assumes that sumatraPDF is in your path). I'm sorry this is not straightforward---it's not my fault :-)

Recent versions of MikTeX add themselves to your path automatically, but in case the build system does not work, that's the first thing to check. TeXlive can also add itself to your path.

Finally, you **must** check the file `LaTeX.sublime-build` in the directory in which you unzipped the LaTeXTools plugin to make sure that the configuration reflects your preferred TeX distribution. Open the file and scroll down to the section beginning with the keyword "windows". You will see that there are two blocks of settings for the "cmd" and "path" keywords; by default, the MikTeX one is active, and the TeXlive one is commented out. If you use MikTeX, you don't need to change anything: congratulations, you are done!

If instead you use TeXlive, comment out the lines between the comments `*** BEGIN MikTeX 2009 ***` and `*** END MikTeX 2009 ***`, and uncomment the lines between the comments `*** BEGIN TeXlive 2011 ***` and `*** END TeXlive 2011 ***`. Do *not* uncomment the `BEGIN`/`END` lines themselves---just the lines between them. Now you are really done!

TeXlive has one main advantage over MikTeX: it supports file names and paths with spaces. Furthermore, it is easier to change the compilation engine from the default, `pdflatex`, to e.g. `xelatex`: see below for details.

Compiling LaTeX files
---------------------

The ST2 Build command (`CMD+B` on OSX; `Ctrl+B` on Windows) takes care of the following:

* It saves the current file
* It invokes the tex build command (`texify` for MikTeX; `latexmk` for TeXlive and MacTeX).
* It parses the tex log file and lists all errors and warnings in an output panel at the bottom of the ST2 window: click on any error/warning to jump to the corresponding line in the text, or use the ST2-standard Next Error/Previous Error commands.
* It invokes the PDF viewer for your platform and performs a forward search: that is, it displays the PDF page where the text corresponding to the current cursor position is located.

Multi-file documents are supported as follows. If the first line in the current file consists of the text `%!TEX root = <master file name>`, then tex & friends are invoked on the specified master file, instead of the current one. Note: the only file that gets saved automatically is the current one.

### Toggling window focus following a build ###

By default, after compilation, the focus stays on the ST2 window. This is convenient if you like to work with the editor and PDF viewer window open side by side, and just glance at the PDF output to make sure that all is OK. If however the editor and viewer windows overlap (e.g. if you have a small screen), you may prefer the viewer window to get the focus (i.e. become the foremost window) after compiling. To this end, you can use the `toggle_focus` command (`Ctrl+Cmd+F` on OSX; `Shift+Win+B` on Windows) to change this behavior. The first time you invoke this command, the focus will shift to the viewer window after compiling the current file; if you invoke the command again, the post-compilation focus reverts to the editor window. Every time you invoke `toggle_focus`, a message will appear in the status bar.

Forward and Inverse Search
---------------------------

When working in an ST2 view on a TeX document, `CMD+Shift+j` (OSX), `Alt+Shift+j` (Windows) will display the PDF page where the text corresponding to the current cursor position is located; this is called a "forward search". The focus remains on ST2; this is useful especially if you set up the ST2 window and the PDF viewer window side by side.

If you are viewing a PDF file, then hitting `CMD+Shift+Click` in Skim (OSX), or double-clicking in Sumatra (Windows) will bring you to the location in the source tex file corresponding to the PDF text you clicked on. This is called "inverse search".

References and Citations
------------------------

Type `ref_`, then `Ctrl+Space` to get a drop-down list of all labels in the current file. You can filter the list: e.g., if you type `ref_a`, then `Ctrl+Space`, you get only labels beginning with the letter "a". Find the label you want and click on it, or hit Return. The correct reference command will be generated: e.g., `\ref{my-label}`.

Using `refp_` instead of `ref_` will surround the reference with parentheses. You can also use `eqref` to generate `\eqref{my-equation}`.

Citations **from bibtex files** are also supported in a similar way. Use `cite_`, as well as `citet_`, `citeyear_` etc.; again, you can filter the keys, as in e.g. `cite_a`. If you want e.g. `\cite*{...}`, use `citeX_`; that is, use X instead of an asterisk.


Jumping to sections and labels
------------------------------

The LaTeXtools plugin integrates with the awesome ST2 "Goto Anything" facility. Hit `CMD+R` (OSX) / `Ctrl+R` (Windows) to get a list of all section headings, and all labels. You can filter by typing a few initial letters. Note that section headings are preceded by the letter "S", and labels by "L"; so, if you only want section headings, type "S" when the drop-down list appears.

Selecting any entry in the list will take you to the corresponding place in the text.


LaTeX commands and environments
-------------------------------

To insert a LaTeX command such as `\color{}` or similar, type the command without backslash (i.e. `color`), then hit `CMD+Shift+]` (OSX) / `Ctrl+Shift+]` (Windows). This will replace e.g. `color` with `\color{}` and place the cursor between the braces. Type the argument of the command, then hit Tab to exit the braces.

Similarly, typing `CMD+Shift+[` (OSX) / `Ctrl+Shift+[` (Windows) gives you an environment: e.g. `test` becomes

	\begin{test}

	\end{test}

and the cursor is placed inside the environment thus created. Again, Tab exits the environment. 

Note that all these commands are undoable: thus, if e.g. you accidentally hit `CMD+Shift+[` but you really meant `CMD+Shift+]`, a quick `CMD+Z`, followed by `CMD+Shift+]`, will fix things.


Wrapping existing text in commands and environments
---------------------------------------------------

The tab-triggered functionality just described is mostly useful if you are creating a command or environment from scratch. However, you sometimes have existing text, and just want to apply some formatting to it via a LaTeX command or environment, such as `\emph` or `\begin{theorem}...\end{theorem}`.

LaTeXTools' wrapping facility helps you in just these circumstances. All commands below are activated via a key binding, and *require some text to be selected first*.

- `Shift+Alt+w,c` wraps the selected text in a LaTeX command structure. If the currently selected text is `blah`, you get `\cmd{blah}`, and the letters `cmd` are highlighted. Replace them with whatever you want, then hit Tab: the cursor will move to the end of the command.
- `Shift+Alt+w,e` gives you `\emph{blah}`, and the cursor moves to the end of the command.
- `Shift+Alt+w,b` gives you `\textbf{blah}`
- `Shift+Alt+w,u` gives you `\underline{blah}`
- `Shift+Alt+w,n` wraps the selected text in a LaTeX environment structure. You get `\begin{env}`,`blah`, `\end{env}` on three separate lines, with `env` selected. Change `env` to whatever environment you want, then hit Tab to move to the end of the environment.

On OSX, replace `Alt` with `Option`: e.g. to emphasize, use `Shift+Option+w,e`.


Command completion, snippets, etc.
----------------------------------

By default, ST2 provides a number of snippets for LaTeX editing; the LaTeXTools plugin adds a few more. You can see what they are, and experiment, by selecting Tools|Snippets|LaTeX and Tools|Snippets|LaTeXTools from the menu.

In addition, the LaTeXTools plugin provides useful completions for both regular and math text; check out files `LaTeX.sublime-completions` and `LaTeX math.sublime-completions` in the LaTeXTools directory for details. Some of these are semi-intelligent: i.e. `bf` expands to `\textbf{}` if you are typing text, and to `\mathbf{}` if you are in math mode. Others allow you to cycle among different completions: e.g. `f` in math mode expands to `\phi` first, but if you hit Tab again you get `\varphi`; if you hit Tab a third time, you get back `\phi`.


Using different TeX engines
---------------------------

In short: on OS X, or on Windows if you use TeXLive, changing the TeX engine used to build your files is very easy. Open the file `LaTeX.sublime-build` and look for the following text (correct as of 11/8/11):

	"cmd": ["latexmk", 
		"-e", "\\$pdflatex = 'pdflatex %O -synctex=1 %S'",
		"-silent",
		"-f", "-pdf"],

(note the final comma). On Mac OS X, the relevant entry is in the `osx` section; on Windows, it is in the `windows` section, between `*** BEGIN TeXlive 2011 ***` and `*** END TeXlive 2011 ***`, and (per the above instructions) it should be uncommented if you are using TeXlive.

The trick is to change the *second* line: e.g.

	"-e", "\\$pdflatex = 'pdflatex %O -synctex=1 %S'",

becomes

	"-e", "\\$pdflatex = 'xelatex %O -synctex=1 %S'",

I have very little experience with "exotic" TeX engines. You probably know more than I do. Anyway, the key is to customize the `latexmk` parameters so they do what you want it to. Please, do **not** ask for assistance doing so: most likely I won't be able to help you. I just want to point out where to change the build variables.

If you use MikTeX, you are out of luck. The `texify` command can read an environment variable to decide which engine to use, but setting this variable requires Windows- and MikTeX-specific additions to the build command. Alternatively, you can try to use `latexmk` with MikTeX, and configure the build command as above. Again, I have not tried this, and you probably know more than I do on the subject. Sorry, and thanks for your understanding!

Troubleshooting
---------------

Many LaTeXTools problems are path-related. The `LaTeX.sublime-build` file attempts to set up default path locations for MikTeX, TeXlive and MacTeX, but these are not guaranteed to cover all possibilities. Please let me know if you have any difficulties.

On Mac OS X, just having your `$PATH` set up correctly in a shell (i.e., in Terminal) does *not* guarantee that things will work when you invoke commands from ST2. If something seems to work when you invoke `pdflatex` or `latexmk` from the Terminal, but building from within ST2 fails, you most likely have a path configuration issue. One way to test this is to launch ST2 from the Terminal, typing

	/Applications/Sublime Text 2.app/Contents/SharedSupport/bin/subl

(and then Return) at the prompt. If things do work when you run ST2 this way, but they fail if you launch ST2 from the Dock or the Finder, then there is a path problem. From the Terminal, type

	echo $PATH

and take note of what you get. Then, run ST2 from the Dock or Finder, open the console (with ``Ctrl+ ` ``) and type
	
	import os; os.environ['PATH']

and again take note of what you see in the output panel (right above the line where you typed the above command). Finally, look at the `path` keyword in the `osx` section of the `LaTeX.sublime-build` file in the LaTeXTools package directory. For things to work, every directory that you see listed from the Terminal must be either in the list displayed when you type the `import os...` command in the ST2 console, or else it must be explicitly specified in `LaTeX.sublime-build`. If this is not the case, add the relevant paths in `LaTeX.sublime-build` and *please let me know*, so I can decide whether to add the path specification to the default build file. Thanks!

On Windows, sometimes a build seems to succeed, but the PDF file is not updated. This is most often the case if there is a stale pdflatex process running; a symptom is the appearence of a file with extension `.synctex.gz(busy)`. If so, launch the Task Manager and end the `pdflatex.exe` process; if you see a `perl.exe` process, end that, too. This kind of behavior is probably a bug: LaTeXTools should be able to see that something went wrong in the earlier compilation. So, *please let me know*, and provide me with as much detail as you can (ideally, with a test case). Thanks!

