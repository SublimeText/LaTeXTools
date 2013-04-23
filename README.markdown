LaTeX Plugin for Sublime Text 2
===============================

by Marciano Siniscalchi
[http://tekonomist.wordpress.com]

Additional contributors (*thank you thank you thank you*): first of all, Wallace Wu and Juerg Rast, who contributed code for multifile support in ref and cite completions, "new-style" ref/cite completion, and project file support. Also, skuroda (Preferences menu), Sam Finn (initial multifile support for the build command); Daniel Fleischhacker (Linux build fixes), Mads Mobaek (universal newline support), Stefan Ollinger (initial Linux support), RoyalTS (aka Tobias Schidt?) (help with bibtex regexes and citation code, various fixes), Juan Falgueras (latexmk option to handle non-ASCII paths). *If you have contributed and I haven't acknowledged you, email me!*

Latest revision: *2012-11-18*. Highlight: The new log-file parser is now in place, and I have kept improving it over the last week or so, based on error reports from users. The new parser is a lot more robust (no more silent crashes!) and picks up files that were just silently ignored by the old one. On the other hand, right now the code is strict in the sense that, if it can't make sense of a log file, it displays an error message. Please see the troubleshooting section on this. 


Introduction
------------
This plugin provides several features that simplify working with LaTeX files:

* The ST2 build command takes care of compiling your LaTeX source to PDF using `texify` (Windows/MikTeX) or `latexmk` (OSX/MacTeX, Windows/TeXlive, Linux/TeXlive). Then, it parses the log file and lists errors and warning. Finally, it launches (or refreshes) the PDF viewer (SumatraPDF on Windows, Skim on OSX, and Evince on Linux) and jumps to the current cursor position (as of 2012-9-18, consider Linux preview support experimental; it works for me, but it may have glitches).
* Forward and inverse search with the named PDF previewers is fully supported
* Easy insertion of references and citations (from BibTeX files) via tab completion
* Plugs into the "Goto anything" facility to make jumping to any section or label in your LaTeX file(s)
* Smart command completion for a variety of text and math commands is provided
* Additional snippets and commands are also provided

Requirements and Setup
----------------------

First, you need to be running Sublime Text 2 (ST2 henceforth); either the release version or late beta builds (>2100) are fine. 

Second, get the LaTeXTools plugin. These days, the easiest way to do so is via Package Control: see [here](http://wbond.net/sublime_packages/package_control) for details on how to set it up (it's very easy). Once you have Package Control up and running, invoke it (via the Command Palette or from Preferences), select the Install Package command, and look for LaTeXTools.

If you prefer a more hands-on approach, you can always clone the git repository, or else just grab this plugin's .zip file from GitHub and extract it to your Packages directory (you can open it easily from ST2, by clicking on Preferences|Browse Packages). Then, (re)launch ST2.

I encourage you to install Package Control anyway, because it's awesome, and it makes it easy to keep your installed packages up-to-date (see the aforelinked page for details). 

Third, follow the OS-specific instructions below.

<br>

On **OSX**, you need to be running the MacTeX distribution (which is pretty much the only one available on the Mac anyway) and the Skim PDF previewer. Just download and install these in the usual way. I have tested MacTeX versions 2010 and 2011, both 32 and 64 bits; these work fine. On the other hand, MacTeX 2008 does *not* seem to work out of the box (compilation fails), so please upgrade. If you don't want to install the entire MacTeX distro, which is pretty big, BasicTeX will also work (of course, as long as the latex packages you need are included). **However**, you need to explicitly add the `latexmk` utility, which is not included by default: from the Terminal, type `sudo tlmgr install latexmk` (you will need to provide your password, assuming you are Administrator on your machine).

To configure inverse search, open the Preferences dialog of the Skim app, select the Sync tab, then:

* uncheck the "Check for file changes" option
* Preset: Custom
* Command: `"/Applications/Sublime Text 2.app/Contents/SharedSupport/bin/subl"`
* Arguments: "%file":%line

Note: in case you have created a symlink to Sublime Text somewhere in your path, you can of course use that, too in the Command field. The above will work in any case though, and does *not* require you to create a symlink or mess with the Terminal in any way!

<br>

On **Windows**, both MikTeX and TeXlive are supported, but TeXLive support is currently *better*. Also, you must be running a current (>=1.4) version of the Sumatra PDF previewer. Install these as usual; then, add the SumatraPDF directory to your PATH (this requirement will be removed at some point). 

You now need to set up inverse search in Sumatra PDF. However, the GUI for doing this is hidden in Sumatra until you open a PDF file that has actual synchronization information (that is, an associated `.synctex.gz` file): see [here](http://forums.fofou.org/sumatrapdf/topic?id=2026321). If you have one such file, then open it, go to Settings|Options, and enter `"C:\Program Files\Sublime Text 2\sublime_text.exe" "%f:%l"` as the inverse-search command line (in the text-entry field at the bottom of the options dialog). If you don't already have a file with sync information, you can easily create one: compile any LaTex file you already have (or create a new one) with `pdflatex -synctex=1 <file.tex>`, and then open the resulting PDF file in SumatraPDF. 

As an alternative, you can open a command-line console (run `cmd.exe`), and issue the following command:

	sumatrapdf.exe -inverse-search "\"C:\Program Files\Sublime Text 2\sublime_text.exe\" \"%f:%l\""

(this assumes that sumatraPDF is in your path). I'm sorry this is not straightforward---it's not my fault :-)

Recent versions of MikTeX add themselves to your path automatically, but in case the build system does not work, that's the first thing to check. TeXlive can also add itself to your path.

Finally, you **must** check the file `LaTeX.sublime-build` in the directory in which you unzipped the LaTeXTools plugin to make sure that the configuration reflects your preferred TeX distribution. Open the file and scroll down to the section beginning with the keyword "windows". You will see that there are two blocks of settings for the "cmd" and "path" keywords; by default, the MikTeX one is active, and the TeXlive one is commented out. If you use MikTeX, you don't need to change anything: congratulations, you are done!

If instead you use TeXlive, comment out the lines between the comments `*** BEGIN MikTeX 2009 ***` and `*** END MikTeX 2009 ***`, and uncomment the lines between the comments `*** BEGIN TeXlive 2011 ***` and `*** END TeXlive 2011 ***`. Do *not* uncomment the `BEGIN`/`END` lines themselves---just the lines between them. Now you are really done! (The dates "2009" and "2011" are only indicative.)

TeXlive has one main advantage over MikTeX: it supports file names and paths with spaces. Furthermore, it is easier to change the compilation engine from the default, `pdflatex`, to e.g. `xelatex`: see below for details.


<br>

**Linux** support is coming along nicely. You need to install TeXlive; if you are on Ubuntu, note that `apt-get install texlive` will get you a working but incomplete setup. In particular, it will *not* bring in `latexmk`, which is essential to LaTeXTools. You need to install it via `apt-get install latexmk`. If on the other hand you choose to install the TeXlive distro from TUG, `latexmk` comes with it, so you don't need to do anything else.

Only the Evince PDF viewer is supported; it's installed by default on Ubuntu or, more generally, any distro that provides the Gnome desktop, and you don't need to configure anything. Backward and forward search Work For Me (TM). Hopefully they will work for you, too, but let me know if this is not the case.

Note: I already have patches to support Okular. Indeed, Okular is very easy to support, as it provides a sane command-line interface; Evince insists on using DBus, which requires considerable gyrations (luckily, it was relatively easy to adapt solutions already existing for other editors to ST2). What is harder is supporting *both* Evince and Okular. This would need a revamp of the building-related facilites of the plugin, basically supporting user settings to select a particular viewer. But the incentive to add such support is very low as far as other platforms are concerned: only SumatraPDF supports forward/inverse search on Windows, and Skim is the easiest-to-control and most powerful/complete PDF viewer on OS X that does. Bottom line: multiple viewer support is probably not coming in the near future. Sorry!


New-Style Keybindings
---------------------

Beginning with the 2012-09-17 commits, keybindings have been changed to make them easier to remember, and also to minimize clashes with existing (and standard) ST2 bindings. I am taking advantage of the fact that ST2 supports key combinations, i.e. sequences of two (or more) keys. The basic principle is simple:

- **Most LaTeXTools facilities are triggered using `Ctrl+l` (Windows, Linux) or `Cmd+l` (OS X), followed by some other key or key combination**

- Compilation uses the standard ST2 "build" keybinding, i.e. `Ctrl-b` on Windows and Linux and `Cmd-b` on OS X. So does the "goto anything" facility (though this may change).

For example: to jump to the point in the PDF file corresponding to the current cursor position, use `Ctrl-l, j`: that is, hit `Ctrl-l`, then release both the `Ctrl` and the `l` keys, and quickly type the `j` key (OS X users: replace `Ctrl` with `Cmd`). To wrap the selected text in an `\emph{}` command, use `Ctrl-l, Ctrl-e`: that is, hit `Ctrl-l`, release both keys, then hit `Ctrl-e` (again, OS X users hit `Cmd-l` and then `Cmd-e`). 

`Ctrl-l` (`Cmd-l` on OS X) is the standard ST2 keybinding for "expand selection to line"; this is **remapped** to `Ctrl-l,Ctrl-l` (`Cmd-l,Cmd-l` on OS X). This is the *only* standard ST2 keybinding that is affected by the plugin---an advantage of new-style keybindings.

Most plugin facilities are invoked using sequences of 2 keys or key combinations, as in the examples just given. A few use sequences of 3 keys or key combinations.

Henceforth, I will write `C-` to mean `Ctrl-` for Linux or Windows, and `Cmd-` for OS X. You know your platform, so you know what you should use. In a few places, to avoid ambiguities, I will spell out which key I mean.

Finally, if you really, really hate the new bindings, look in the plugin's directory: there you will find files named, e.g., `Default (OSX).sublime-keybinding.OLD`. This is the old binding file. Drop it in your `User` directory, remove the `.OLD` extension, and you will get back the old bindings. However, you will miss some important functionality, such as ref-cite completion using the quick panel. Of course, you can add it back by tinkering with the keybinding file. Just remember: **do not** modify the keybinding file in the plugin directory, because it will be clobbered the next time you update LaTeXTools.

Compiling LaTeX files
---------------------

**Keybinding:** `C-b` (standard ST2 keybinding)

The ST2 Build command takes care of the following:

* It saves the current file
* It invokes the tex build command (`texify` for MikTeX; `latexmk` for TeXlive and MacTeX).
* It parses the tex log file and lists all errors and warnings in an output panel at the bottom of the ST2 window: click on any error/warning to jump to the corresponding line in the text, or use the ST2-standard Next Error/Previous Error commands.
* It invokes the PDF viewer for your platform and performs a forward search: that is, it displays the PDF page where the text corresponding to the current cursor position is located.

**Multi-file documents** are supported as follows. If the first line in the current file consists of the text `%!TEX root = <master file name>`, then tex & friends are invoked on the specified master file, instead of the current one. Note: the only file that gets saved automatically is the current one. Also, the master file name **must** have a `.tex` extension, or it won't be recognized.

There is also support for project files; this is to be documented.

### Toggling window focus following a build ###

**Keybinding:** `C-l,t,f` (yes, this means `C-l`, then `t`, then `f`)

By default, after compilation, the focus stays on the ST2 window. This is convenient if you like to work with the editor and PDF viewer window open side by side, and just glance at the PDF output to make sure that all is OK. If however the editor and viewer windows overlap (e.g. if you have a small screen), you may prefer the viewer window to get the focus (i.e. become the foremost window) after compiling. To this end, you can use the `toggle_focus` command to change this behavior. The first time you invoke this command, the focus will shift to the viewer window after compiling the current file; if you invoke the command again, the post-compilation focus reverts to the editor window. Every time you invoke `toggle_focus`, a message will appear in the status bar.

You can change the default focus behavior via the `keep_focus` option: see the "Settings" section below.

### Toggling PDF syncing (forward search) following a build ###

**Keybinding:** `C-l,t,s`

By default, after compilation, LaTeXTools performs a 'forward search' so that the PDF viewer shows the point in the PDF file corresponding to the current cursor position in ST2 (by the way, you can trigger a forward search at any other time, not just when you are compiling: see below). If for whatever reason you don't like this behavior, you can turn it off using the `toggle_fwdsync` command. As for `toggle_focus`, a message will appear in the status bar to reflect this.

You can also change the default sync behavior via the `forward_sync` option: see the "Settings" section below.

### Checking the status of toggles and defaults ###

**Keybinding:** `C-l,t,?`

This causes the status message to list the default settings of the focus and sync options, and their current toggle values.

Forward and Inverse Search
---------------------------

**Keybinding:** `C-l,j` (for forward search; inverse search depends on the previewer)

When working in an ST2 view on a TeX document, `C-l,j` will display the PDF page where the text corresponding to the current cursor position is located; this is called a "forward search". The focus remains on ST2; this is useful especially if you set up the ST2 window and the PDF viewer window side by side.

If you are viewing a PDF file, then hitting `CMD+Shift+Click` in Skim (OSX), double-clicking in Sumatra (Windows), or hitting `Ctrl+click` in Evince (Linux) will bring you to the location in the source tex file corresponding to the PDF text you clicked on. This is called "inverse search".

To open a PDF file without performing a forward search, use `C-l,v`. I'm not sure this is very useful, but the facility is there for now.

References and Citations
------------------------

**Keybinding:** `C-l, Ctrl-space` (on OS X, this means `Cmd-l,Ctrl-space`) or `C-l,x`

The basic idea is to help you insert labels in `\ref{}` commands and bibtex keys in `\cite{}` commands. The appropriate key combination shows a list of available labels or keys, and you can easily select the appropriate one. Full filtering facilities are provided. 

**Notes**: 

1. In order to find all applicable labels and bibtex keys, the plugin looks at the **saved** file. So, if you invoke this command and do not see the label or key you just entered, perhaps you haven't saved the file.

2. Only bibtex bibliographies are supported. Sorry. It's hard as it is.

3. Multi-file documents are fully supported.

Now for the details. There are two styles of reference / citation completion commands. Let me describe the "new-style" first. 

Type, for example, `\ref{`; as soon as you type the brace, ST2 helpfully provides the closing brace, leaving your cursor between the two braces. Now, type `C-l,Ctrl-space` to get a quick panel (the fancy drop-down list ST2 displays at the top of the screen) showing all labels in the current file. You can also type e.g. `\ref{aa` [again, the closing brace is provided by ST2], then `C-l, Ctrl+Space`, and LaTeXTools will show a list of labels that contain the string `aa`. You select the label you want, hit Return, and LaTeXTools inserts the **full ref command**, as in `\ref{my-label}`. The LaTeX command `\eqref` works the same way. 

Citations from bibtex files are also supported in a similar way. Use `\cite{}`,  `\citet{}`,  `\citeyear{}` etc.; again, you can filter the keys, as in e.g. `\cite{a}`. The quick panel is really useful for citations, as you get a nice display of paper titles and bibtex keys (which you can narrow down by typing a few characters, as usual in ST2), and also of the author names (not searchable, but still useful). 

The "old-style" system works as follows. For references, you type `ref_`, then `C-l,Ctrl-space`; again, you can filter by typing, e.g., `ref_a`. Using `refp_` instead of `ref_` will surround the reference with parentheses. You can also use `eqref` to generate `\eqref{my-equation}`. Citations work the same way: you use `cite_`, etc. If you want fancy citations, as in the natbib package, that's allowed, but you must replace asterisks with `X`: so, to get `\cite*{...}` with old-style completions, you need to start by typing `citeX_`. 

*Deprecation alert*: the only real advantage of old-style citations is that you don't have to enter the initial `\`. I think I will eventually remove this functionality and leave only new-style completions, i.e. `\ref{}`, `\cite{}` etc. 

*Graceful error reporting*: if a bib file is not found, LaTeXTools displays a warning message in the status bar. Note that this message goes away after a few seconds. So, if you hit `C-l,Ctrl-space` and nothing happens--or, in the case of multiple bib files, if you can't file a reference that you *know* must be there somewhere--look at the status bar (you may have to dismiss the quick panel and hitting the key combination again).

Thanks to recent contributed code, **multi-file documents** are *fully supported*. If you have a `% !TEX root = ...` directive at the top of the current file, LaTeXTools looks for references, as well as `\bibliography{}` commands, in the root file and in all recursively included files. You can also use a project file to specify the root file (to be documented).

Another note: **for now**, completions are also injected into the standard ST2 autocompletion system. Thus, if you hit `Ctrl-space` immediately after typing, e.g., `\ref{}`, you get a drop-down menu at the current cursor position (not a quick-panel) showing all labels in your document. This also works with old-style citations. However, the width of this menu is OK for (most) labels, but not really for paper titles. In other words, it is workable for references, but not really for citations. Furthermore, there are other limitations dictated by the ST2 autocompletion system. So, I encourage you to use the `C-l,Ctrl-space` keybinding instead. In fact, consider the standard autocompletion support to be *deprecated* as of today (12-09-17).


Jumping to sections and labels
------------------------------

**Keybinding:** `C-r` (standard ST2 keybinding)

The LaTeXtools plugin integrates with the awesome ST2 "Goto Anything" facility. Hit `C-r`to get a list of all section headings, and all labels. You can filter by typing a few initial letters. Note that section headings are preceded by the letter "S", and labels by "L"; so, if you only want section headings, type "S" when the drop-down list appears.

Selecting any entry in the list will take you to the corresponding place in the text.


LaTeX commands and environments
-------------------------------

**Keybindings:** `C-l,c` for commands and `C-l,e` for environments

To insert a LaTeX command such as `\color{}` or similar, type the command without backslash (i.e. `color`), then hit `C-l,c`. This will replace e.g. `color` with `\color{}` and place the cursor between the braces. Type the argument of the command, then hit Tab to exit the braces.

Similarly, typing `C-l,e` gives you an environment: e.g. `test` becomes

	\begin{test}

	\end{test}

and the cursor is placed inside the environment thus created. Again, Tab exits the environment. 

Note that all these commands are undoable: thus, if e.g. you accidentally hit `C-l,c` but you really meant `C-l,e`, a quick `C-z`, followed by `C-l,e`, will fix things.


Wrapping existing text in commands and environments
---------------------------------------------------

**Keybindings:** `C-l,C-c`, `C-l, C-n`, etc.

The tab-triggered functionality just described is mostly useful if you are creating a command or environment from scratch. However, you sometimes have existing text, and just want to apply some formatting to it via a LaTeX command or environment, such as `\emph` or `\begin{theorem}...\end{theorem}`.

LaTeXTools' wrapping facility helps you in just these circumstances. All commands below are activated via a key binding, and *require some text to be selected first*. Also, as a mnemonic aid, *all wrapping commands involve typing `C-l,C-something` (which you can achieve by just holding the `C-` key down after typing `l`).

- `C-l,C-c` wraps the selected text in a LaTeX command structure. If the currently selected text is `blah`, you get `\cmd{blah}`, and the letters `cmd` are highlighted. Replace them with whatever you want, then hit Tab: the cursor will move to the end of the command.
- `C-l,C-e` gives you `\emph{blah}`, and the cursor moves to the end of the command.
- `C-l,C-b` gives you `\textbf{blah}`
- `C-l,C-u` gives you `\underline{blah}`
- `C-l,C-n` wraps the selected text in a LaTeX environment structure. You get `\begin{env}`,`blah`, `\end{env}` on three separate lines, with `env` selected. Change `env` to whatever environment you want, then hit Tab to move to the end of the environment.

These commands also work if there is no selection. In this case, they try to do the right thing; for example, `C-l,C-e` gives `\emph{}` with the cursor between the curly braces.

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

*Warning*: if you customize your build file, you'd better move or copy it to the `User` directory. Otherwise, the next time you update LaTeXTools, your changes will be overwritten by the default file.

Settings
--------

LaTeXTools now supports user-defined settings. The *default* settings file is called `LaTeXTools Preferences.sublime-settings`, in the plugin's folder (normally `Packages/LaTeXTools`). You can take a look at it to see what options are available, but **do not edit it**. Instead, copy it to the `Packages/User` folder, and edit your copy. This way your settings won't be clobbered the next time you update the plugin.

*Warning*: tweaking options can cause breakage. For instance, if you change the default `python2` setting (empty by default) to a non-existent binary, forward and inverse search will stop working. If you think you have found a bug, *delete your settings file in the `Packages/User` folder before reporting it!* Thanks :-)

The following options are currently available (defaults in parentheses):

- `keep_focus` (`true`): if `true`, after compiling a tex file, ST2 retains the focus; if `false`, the PDF viewer gets the focus. Also note that you can *temporarily* toggle this behavior with `C-l,t,f`.
- `forward_sync` (`true`): if `true`, after compiling a tex file, the PDF viewer is asked to sync to the position corresponding to the current cursor location in ST2. You can also *temporarily* toggle this behavior with `C-l,t,s`.
- `linux` settings:
  * `python2` (`""`, i.e. empty string): name of the Python 2 executable. This is useful for systems that ship with both Python 2 and Python 3. The forward/backward search used with Evince require Python 2.
  * `sublime` (`sublime-text`): name of the ST2 executable. Ubuntu supports both `sublime-text` and `subl`; other distros may vary.
  * `sync_wait` (1.5): when you ask LaTeXTools to do a forward search, and the PDF file is not yet open (for example, right after compiling a tex file for the first time), LaTeXTools first launches evince, then waits a bit for it to come up, and then it performs the forward search. This parameter controls how long LaTeXTools should wait. If you notice that your machine opens the PDF, then sits there doing nothing, and finally performs the search, you can decrease this value to 1.0 or 0.5; if instead the PDF file comes up but the forward search does not seem to happen, increase it to 2.0.

Troubleshooting
---------------

### Path issues ###

Many LaTeXTools problems are path-related. The `LaTeX.sublime-build` file attempts to set up default path locations for MikTeX, TeXlive and MacTeX, but these are not guaranteed to cover all possibilities. Please let me know if you have any difficulties.

On Mac OS X, just having your `$PATH` set up correctly in a shell (i.e., in Terminal) does *not* guarantee that things will work when you invoke commands from ST2. If something seems to work when you invoke `pdflatex` or `latexmk` from the Terminal, but building from within ST2 fails, you most likely have a path configuration issue. One way to test this is to launch ST2 from the Terminal, typing

	/Applications/Sublime Text 2.app/Contents/SharedSupport/bin/subl

(and then Return) at the prompt. If things do work when you run ST2 this way, but they fail if you launch ST2 from the Dock or the Finder, then there is a path problem. From the Terminal, type

	echo $PATH

and take note of what you get. Then, run ST2 from the Dock or Finder, open the console (with ``Ctrl+ ` ``) and type
	
	import os; os.environ['PATH']

and again take note of what you see in the output panel (right above the line where you typed the above command). Finally, look at the `path` keyword in the `osx` section of the `LaTeX.sublime-build` file in the LaTeXTools package directory. For things to work, every directory that you see listed from the Terminal must be either in the list displayed when you type the `import os...` command in the ST2 console, or else it must be explicitly specified in `LaTeX.sublime-build`. If this is not the case, add the relevant paths in `LaTeX.sublime-build` and *please let me know*, so I can decide whether to add the path specification to the default build file. Thanks!

### Non-ASCII characters and spaces in path and file names ###

Another *significant* source of issues are **Unicode characters in path and file names**. On TeXLive-based platforms, LaTeXTools tries to handle these by telling `latexmk` to `cd` to each source file's directory before running `pdflatex`. This seems to help some. However, things seem to vary by platform and locale, so I cannot make any guarantees that your Unicode path names will work. Keep in mind that TeX itself has issues with Unicode characters in file names (as a quick Google search will confirm).

Spaces in paths and file names *are* supported. As far as I know, the only limitation has to do with multifile documents: the root document's file name cannot contain spaces, or the `%!TEX = <name>` directive will fail. I may fix this at some point, but for now it is a limitation.

### Compilation hangs on Windows ###

On Windows, sometimes a build seems to succeed, but the PDF file is not updated. This is most often the case if there is a stale pdflatex process running; a symptom is the appearence of a file with extension `.synctex.gz(busy)`. If so, launch the Task Manager and end the `pdflatex.exe` process; if you see a `perl.exe` process, end that, too. This kind of behavior is probably a bug: LaTeXTools should be able to see that something went wrong in the earlier compilation. So, *please let me know*, and provide me with as much detail as you can (ideally, with a test case). Thanks!


### Log parsing issues, and good vs. bad path/file names (again!) ###

As noted in the Highlights, the new parser is more robust and flexible than the old one---it "understands" the log file format much, much better. This is the result of *manually* and *painstakingly* debugging a fair number of users' log files. The many possible exceptions, idiosyncrasies, warts, etc. displayed by TeX packages is mind-boggling, and the parsing code reflects this :-(

Anyway, hopefully, errors should now occur only in strange edge cases. Please *let me know on github* if you see an error message. I need a log file to diagnose the problem; please upload it to gist, dropbox, or similar, and paste a link in your message on github. Issue #104 is open for that purpose.

There are *two exceptions* to this request. First, the *xypic* package is very, very badly behaved. I have spent more time debugging log files contaminated by xypic than I have spent fixing all other issues. Seriously. Therefore, first, parsing issues are now reported as "warnings" if the xypic package is used (so compilation and previewing continues); second, I cannot promise I will fix the issue even if you report it. Thanks for your understanding. 

The second exception has to do with file and path names. In order to accommodate the many possible naming conventions across platforms and packages, as well as the different ways in which file names can occur in logs, I had to make some assumptions. The key one is that *extensions cannot contain spaces*. The reason is that the regex matching file names uses a period (".") followed by non-space characters, followed by a space as denoting the end of the file name. Trust me, it's the most robust regex I could come up with. So, you can have spaces in your base names, and you can even have multiple extensions; however, you cannot have spaces in your extensions. So, "This is a file.ver-1.tex" is OK; "file.my ext" (where "my ext" is supposed to be the extension) is *not OK*.

Finally, I have done my best to accommodate non-ASCII characters in logs. I cannot promise that everything works, but I'd like to know if you see issues with this.
 
