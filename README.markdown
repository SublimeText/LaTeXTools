LaTeX Plugin for Sublime Text 2 and 3
=====================================

by Marciano Siniscalchi
[http://tekonomist.wordpress.com]

Additional contributors (*thank you thank you thank you*): first of all, Wallace Wu and Juerg Rast, who contributed code for multifile support in ref and cite completions, "new-style" ref/cite completion, and project file support. Also, skuroda (Preferences menu), Sam Finn (initial multifile support for the build command); Daniel Fleischhacker (Linux build fixes), Mads Mobaek (universal newline support), Stefan Ollinger (initial Linux support), RoyalTS (aka Tobias Schidt?) (help with bibtex regexes and citation code, various fixes), Juan Falgueras (latexmk option to handle non-ASCII paths), Jeremy Jay (basic biblatex support), Ray Fang (texttt snippet), Ulrich Gabor (tex engine selection and cleaning aux files), Wes Campaigne and 'jlegewie' (ref/cite completion 2.0!). **Huge** thanks to Daniel Shannon (aka phyllisstein) who first ported LaTeXTools to ST3. Also thanks for Charley Peng, who has been assisting users and generating great pull requests; I'll merge them as soon as possible. Also William Ledoux (various Windows fixes, env support), Sean Zhu (find Skim.app in non-standard locations), Maximilian Berger (new center/table snippet), Lucas Nanni (recursively delete temp files), Sergey Slipchenko (`$` auto-pairing with Vintage) ig0774 (use `kpsewhich` to find bib files in the `TEXMF` tree).

*If you have contributed and I haven't acknowledged you, email me!*

*Latest revision:* 2015-4-12. 

*Highlight*: New, fully customizable build system! See below for a complete description. Note that, for now, things work more or less as before, but the infrastructure is there to customize things beyond your wildest dreams!

**NOTE**: due to the change in the build system, I had to overhaul the preferences settings. If you are already using LaTeXTools, please **read this** before proceeding any further:

* From now on, LaTeXTools will use a single settings file, called `LaTeXTools.sublime-settings`, which *must* exist in the `User` directory. By this I mean that LaTeXTools *will not work* until you have a proper `LaTeXTools.sublime-settings` file in the `User` directory.
* Because of this, LaTeXtools provides an easy way to create it, and even *automagically* migrate your settings from any old `LaTeXTools Preferences.sublime-settings` file you may have. In Sublime Text, open the command palette from the Tools menu, search for "LaTeXTools: Reconfigure and migrate settings," and hit Return. That's it! See the Settings section for other ways to migrate or reconfigure settings.
* The old settings file, `LaTeXTools Preferences.sublime-settings`, will no longer be honored.
* The `LaTeX.sublime-build` file is now for *internal use only*. Do *not* modify it! If you have a customized copy in `User`, delete it (but do *not* delete the original in the `LaTeXTools` directory). See the Settings section below for ways to *easily* customize the build command. 



Introduction
------------
This plugin provides several features that simplify working with LaTeX files:

* The ST build command takes care of compiling your LaTeX source to PDF using `texify` (Windows/MikTeX) or `latexmk` (OSX/MacTeX, Windows/TeXlive, Linux/TeXlive). Then, it parses the log file and lists errors and warning. Finally, it launches (or refreshes) the PDF viewer (SumatraPDF on Windows, Skim on OSX, and Evince on Linux) and jumps to the current cursor position.
* Forward and inverse search with the named PDF previewers is fully supported
* Easy insertion of references and citations (from BibTeX files)
* Plugs into the "Goto anything" facility to make jumping to any section or label in your LaTeX file(s)
* Smart command completion for a variety of text and math commands is provided
* Additional snippets and commands are also provided
* The build command is fully customizable. In the near future, so will be the PDF previewer.

Requirements and Setup
----------------------

First, you need to be running Sublime Text 2 or 3 (ST2 and ST3 henceforth, or simply ST to refer to either ST2 or ST3). For ST3, I have only tested build 3047 and will of course test subsequent builds.

Second, get the LaTeXTools plugin. These days, the easiest way to do so is via Package Control: see [here](https://sublime.wbond.net) for details on how to set it up (it's very easy). Once you have Package Control up and running, invoke it (via the Command Palette from the Tools menu, or from Preferences), select the Install Package command, and look for LaTeXTools.

If you prefer a more hands-on approach, you can always clone the git repository, or else just grab this plugin's .zip file from GitHub and extract it to your Packages directory (you can open it easily from ST, by clicking on Preferences|Browse Packages). Then, (re)launch ST.

I encourage you to install Package Control anyway, because it's awesome, and it makes it easy to keep your installed packages up-to-date (see the aforelinked page for details). 

Third, if you are installing LaTeXTools for the first time, you need to create a configuration file, `LaTeXTools.sublime-settings`, in your `User` directory (off the `Packages`) directory. To do so, open the command palette from the Tools menu, search for "LaTeXTools: Reconfigure and migrate settings," and hit Return. That's it! See the Settings section for details on configuration options.

Fourth, follow the OS-specific instructions below.

<br>

On **OSX**, you need to be running the MacTeX distribution (which is pretty much the only one available on the Mac anyway) and the Skim PDF previewer. Just download and install these in the usual way. I have tested MacTeX versions 2010, 2011 and 2012, both 32 and 64 bits; these work fine. On the other hand, MacTeX 2008 does *not* seem to work out of the box (compilation fails), so please upgrade. 

If you don't want to install the entire MacTeX distro, which is pretty big, BasicTeX will also work (of course, as long as the latex packages you need are included). **However**, you need to explicitly add the `latexmk` utility, which is not included by default: from the Terminal, type `sudo tlmgr install latexmk` (you will need to provide your password, assuming you are Administrator on your machine).

To configure inverse search, open the Preferences dialog of the Skim app, select the Sync tab, then:

* uncheck the "Check for file changes" option
* choose the Sublime Text 2 or Sublme Text 3 preset (yes, Skim now supports both ST2 and ST3 by default!)

In case you are using an old version of Skim, you can always choose the Custom preset and enter `/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl` (for ST3) in the Command field, and `"%file":%line` in the Arguments field. (This is correct as of 7/18/2013; you may want to double-check that ST3 is indeed in `/Applications/Sublime Text`; just go to the Applications folder in the Finder. Adapt as needed for ST2).

If you have installed Skim in a non-standard location, there is not much you can do short of hacking the `jumpToPDF.py` file (**not supported!**). This will change in the near future. 

Finally, edit the file `LaTeX.sublime-settings` in the `User` directory to make sure that the configuration reflects your preferred TeX distribution. Open the file and scroll down to the  section titled "Platform settings." Look at the block for your OS, namely `"osx"`. Within that block, verify that the `"texpath"` setting is correct. Note that `"texpath"` **must** include `$PATH` somewhere.

<br>

On **Windows**, both MikTeX and TeXlive are supported. You must be running a current (>=1.4) version of the Sumatra PDF previewer. Install these as usual; then, add the SumatraPDF directory to your PATH or set the `sumatra` command in the `windows` platform setting.

You now need to set up inverse search in Sumatra PDF. However, the GUI for doing this is hidden in Sumatra until you open a PDF file that has actual synchronization information (that is, an associated `.synctex.gz` file): see [here](http://forums.fofou.org/sumatrapdf/topic?id=2026321). If you have one such file, then open it, go to Settings|Options, and enter `"C:\Program Files\Sublime Text 2\sublime_text.exe" "%f:%l"` for ST2, and `"C:\Program Files\Sublime Text 3\sublime_text.exe" "%f:%l"` for ST3, as the inverse-search command line (in the text-entry field at the bottom of the options dialog). If you don't already have a file with sync information, you can easily create one: compile any LaTex file you already have (or create a new one) with `pdflatex -synctex=1 <file.tex>`, and then open the resulting PDF file in SumatraPDF. 

As an alternative, you can open a command-line console (run `cmd.exe`), and issue the following command:

	sumatrapdf.exe -inverse-search "\"C:\Program Files\Sublime Text 2\sublime_text.exe\" \"%f:%l\""

(this assumes that sumatraPDF is in your path; replace 2 with 3 for ST3 of course). I'm sorry this is not straightforward---it's not my fault :-)

Recent versions of MikTeX add themselves to your path automatically, but in case the build system does not work, that's the first thing to check. TeXlive can also add itself to your path.

Finally, edit the file `LaTeX.sublime-settings` in the `User` directory to make sure that the configuration reflects your preferred TeX distribution. Open the file and scroll down to the  section titled "Platform settings." Look at the block for your OS, namely `windows`. Within that block, verify that the `texpath` setting is correct; for MiKTeX, you can leave this empty, i.e., `""`. If you do specify a path, note that it **must** include the system path variable, i.e., `$PATH` (this syntax seems to be OK). Also verify that the `distro` setting is correct: the possible values are `"miktex"` and `"texlive"`.

TeXlive has one main advantage over MikTeX: it supports file names and paths with spaces.


<br>

**Linux** support is coming along nicely. However, as a general rule, you will need to do some customization before things work. This is due to differences across distributions (a.k.a. "fragmentation"). Do not expect things to work out of the box.

You need to install TeXlive; if you are on Ubuntu, note that `apt-get install texlive` will get you a working but incomplete setup. In particular, it will *not* bring in `latexmk`, which is essential to LaTeXTools. You need to install it via `apt-get install latexmk`. If on the other hand you choose to install the TeXlive distro from TUG, `latexmk` comes with it, so you don't need to do anything else. Also, to get inverse search working on ST3, make sure you set the `sublime` option in `LaTeXTools.sublime-settings` correctly; the Ubuntu package from the ST web page uses `subl`, but check from the command line first.

You also need to edit the file `LaTeX.sublime-settings` in the `User` directory to make sure that the configuration reflects your preferred TeX distribution.  Open that file and scroll down to the  section titled "Platform settings." Look at the block for your OS, namely `"linux"`. Within that block, verify that the `"texpath"` setting is correct. Notice that this **must** include `$PATH` somewhere, or things will not work.

You may also have to set the `command` option in `"builder_settings"`, which tells the builder how to invoke `latexmk`. By default (i.e., if `command` is empty or not given) it is `["latexmk", "-cd", "-e", "$pdflatex = '%E -interaction=nonstopmode -synctex=1 %S %O'", "-f", "-pdf"]`. Users have reported the following possible issues and fixes (thanks!), so if you get a "Cannot compile!" error, try the following.

* some distros do *not* want a space before and after the `=` in `$pdflatex = %E`. But some *do* want the space there (sigh!)
* sometimes `latexmk` is not on the `PATH`, or the path is not correctly picked up by ST. In this case, instead of `"latexmk"`, use `"/usr/bin/latexmk"` or wherever `latexmk` is in your system. 
* some distros require quoting the `$pdflatex` assignment, as in `"$pdflatex = \"'%E -interaction=nonstopmode -synctex=1 %S %O'\""`

There are several variants to deal with; each distro is a little bit different, so there are basically no universal defaults. There's not much I can do about it. Good luck! 

Only the Evince PDF viewer is supported; it's installed by default on Ubuntu or, more generally, any distro that provides the Gnome desktop, and you don't need to configure anything. Backward and forward search Work For Me (TM). Hopefully they will work for you, too, but let me know if this is not the case.

Note: I already have patches to support Okular. Indeed, Okular is very easy to support, as it provides a sane command-line interface; Evince insists on using DBus, which requires considerable gyrations (luckily, it was relatively easy to adapt solutions already existing for other editors to ST). What is harder is supporting *both* Evince and Okular. This would need a revamp of the building-related facilites of the plugin, basically supporting user settings to select a particular viewer. But the incentive to add such support is very low as far as other platforms are concerned: only SumatraPDF supports forward/inverse search on Windows, and Skim is the easiest-to-control and most powerful/complete PDF viewer on OS X that does. Bottom line: multiple viewer support is probably not coming in the near future. Sorry!


Keybindings
-----------

Keybindings have been chosen to make them easier to remember, and also to minimize clashes with existing (and standard) ST bindings. I am taking advantage of the fact that ST supports key combinations, i.e. sequences of two (or more) keys. The basic principle is simple:

- **Most LaTeXTools facilities are triggered using `Ctrl+l` (Windows, Linux) or `Cmd+l` (OS X), followed by some other key or key combination**

- Compilation uses the standard ST "build" keybinding, i.e. `Ctrl-b` on Windows and Linux and `Cmd-b` on OS X. So does the "goto anything" facility (though this may change).

For example: to jump to the point in the PDF file corresponding to the current cursor position, use `Ctrl-l, j`: that is, hit `Ctrl-l`, then release both the `Ctrl` and the `l` keys, and quickly type the `j` key (OS X users: replace `Ctrl` with `Cmd`). To wrap the selected text in an `\emph{}` command, use `Ctrl-l, Ctrl-e`: that is, hit `Ctrl-l`, release both keys, then hit `Ctrl-e` (again, OS X users hit `Cmd-l` and then `Cmd-e`). 

`Ctrl-l` (`Cmd-l` on OS X) is the standard ST keybinding for "expand selection to line"; this is **remapped** to `Ctrl-l,Ctrl-l` (`Cmd-l,Cmd-l` on OS X). This is the *only* standard ST keybinding that is affected by the plugin---an advantage of new-style keybindings.

Most plugin facilities are invoked using sequences of 2 keys or key combinations, as in the examples just given. A few use sequences of 3 keys or key combinations.

Henceforth, I will write `C-` to mean `Ctrl-` for Linux or Windows, and `Cmd-` for OS X. You know your platform, so you know what you should use. In a few places, to avoid ambiguities, I will spell out which key I mean.


Compiling LaTeX files
---------------------

**Keybinding:** `C-b` (standard ST keybinding)

Beginning with the 3/2014 releases, LaTeXTools offers a fully customizable build process. This section describes the default process, also called "traditional" because it is the same (with minor tweaks) as the one used in previous releases. However, see below for how to customize the build process.

The default ST Build command takes care of the following:

* It saves the current file
* It invokes the tex build command (`texify` for MikTeX; `latexmk` for TeXlive and MacTeX).
* It parses the tex log file and lists all errors and warnings in an output panel at the bottom of the ST window: click on any error/warning to jump to the corresponding line in the text, or use the ST-standard Next Error/Previous Error commands.
* It invokes the PDF viewer for your platform and performs a forward search: that is, it displays the PDF page where the text corresponding to the current cursor position is located.

**Multi-file documents** are supported as follows. If the first line in the current file consists of the text `%!TEX root = <master file name>`, then tex & friends are invoked on the specified master file, instead of the current one. Note: the only file that gets saved automatically is the current one. Also, the master file name **must** have a `.tex` extension, or it won't be recognized.

There is also support for project files; this is to be documented.

**TeX engine selection** is supported. If the first line of the current file consists of the text `%!TEX program = <program>`, where `program` is `pdflatex`, `lualatex` or `xelatex`, the corresponding engine is selected. If no such directive is specified, `pdflatex` is the default. Multi-file documents are supported: the directive must be in the *root* (i.e. master) file. Also, for compatibility with TeXshop, you can use `TS-program` instead of `program`. **Note**: for this to work, you must **not** customize the `"command"` option in `LaTeX.sublime-settings`. If you do, you will not get this functionality. 

**Customizing or replacing the compilation command** (`latexmk` or `texify`) is also possible by setting the `command` option under Builder Settings. If you do, the TeX engine selection facility will no longer work (because it relies on a specific compilation command). However, if you want to customize or replace `latexmk`/`texify`, you probably know how to select the right TeX engine, so this shouldn't be a concern. See the Settings option below for details. *Note*: if you change the compilation command, you are responsible for making it work on your setup. Only customize the compilation command if you know what you're doing. 


### Toggling window focus following a build ###

**Keybinding:** `C-l,t,f` (yes, this means `C-l`, then `t`, then `f`)

By default, after compilation, the focus stays on the ST window. This is convenient if you like to work with the editor and PDF viewer window open side by side, and just glance at the PDF output to make sure that all is OK. If however the editor and viewer windows overlap (e.g. if you have a small screen), you may prefer the viewer window to get the focus (i.e. become the foremost window) after compiling. To this end, you can use the `toggle_focus` command to change this behavior. The first time you invoke this command, the focus will shift to the viewer window after compiling the current file; if you invoke the command again, the post-compilation focus reverts to the editor window. Every time you invoke `toggle_focus`, a message will appear in the status bar.

You can change the default focus behavior via the `keep_focus` option: see the "Settings" section below.

### Toggling PDF syncing (forward search) following a build ###

**Keybinding:** `C-l,t,s`

By default, after compilation, LaTeXTools performs a 'forward search' so that the PDF viewer shows the point in the PDF file corresponding to the current cursor position in ST (by the way, you can trigger a forward search at any other time, not just when you are compiling: see below). If for whatever reason you don't like this behavior, you can turn it off using the `toggle_fwdsync` command. As for `toggle_focus`, a message will appear in the status bar to reflect this.

You can also change the default sync behavior via the `forward_sync` option: see the "Settings" section below.

### Checking the status of toggles and defaults ###

**Keybinding:** `C-l,t,?`

This causes the status message to list the default settings of the focus and sync options, and their current toggle values. It also display the status of the ref/cite auto trigger toggles (see below).

### Removing temporary files from build ###

**Keybinding:** `C-l,backspace`

This deletes all temporary files from a previous build (the PDF file is kept).

Forward and Inverse Search
---------------------------

**Keybinding:** `C-l,j` (for forward search; inverse search depends on the previewer)

When working in an ST view on a TeX document, `C-l,j` will display the PDF page where the text corresponding to the current cursor position is located; this is called a "forward search". The focus is controlled by the `C-l,t,f` toggle setting and the `keep_focus` option.

If you are viewing a PDF file, then hitting `CMD+Shift+Click` in Skim (OSX), double-clicking in Sumatra (Windows), or hitting `Ctrl+click` in Evince (Linux) will bring you to the location in the source tex file corresponding to the PDF text you clicked on. This is called "inverse search".

To open a PDF file without performing a forward search, use `C-l,v`. I'm not sure this is very useful, but the facility is there for now.

References and Citations
------------------------

**Keybinding:** *autotriggered* by default (see below). Otherwise, `C-l,x` for 'cross-reference,' or ( *deprecated* )  `C-l, Ctrl-space` (on OS X, this means `Cmd-l,Ctrl-space`).

The basic idea is to help you insert labels in `\ref{}` commands and bibtex keys in `\cite{}` commands. The appropriate key combination shows a list of available labels or keys, and you can easily select the appropriate one. Full filtering facilities are provided. 

**Notes**: 

1. In order to find all applicable labels and bibtex keys, the plugin looks at the **saved** file. So, if you invoke this command and do not see the label or key you just entered, perhaps you haven't saved the file.

2. Only bibliographies in external `.bib` files are supported: no `\bibitem...`. Sorry. It's hard as it is. 

3. Multi-file documents are fully supported.

Now for the details. As of 6/29/2013, I have incorporated a fantastic set of much-needed improvements contributed by Wes Campaigne (Westacular) and jlewegie, whom I thank profusely.

By default, as soon as you type, for example, `\ref{` or `\cite`, a quick panel is shown (this is the fancy drop-down list ST displays at the top of the screen), listing, respectively, all the labels in your files, or all the entries in the bibliographies you reference your file(s) using the `\bibliography{}` command. This is the default *auto-trigger* behavior, and it can be a big time saver. You can, however, turn it off, either temporarily using a toggle, or permanently by way of preference settings: see below. Once the quick panel is shown, you can narrow down the entries shown by typing a few characters. As with any ST quick panel, what you type will be fuzzy-matched against the label names or, for citations, the content of the first displayed line in each entry (by default, the author names, year of publication, short title and citation key: see below). This is *wildly* convenient, and one of the best ST features: try it!

If auto-triggering is off, when you type e.g. `\ref{`, ST helpfully provides the closing brace, leaving your cursor between the two braces. Now, you need to type `C-l,x` to get the quick panel  showing all labels in the current file. You can also type e.g. `\ref{aa` [again, the closing brace is provided by ST], then `C-l, x`, and LaTeXTools will show a list of labels that fuzzy-match the string `aa`. 

In either case, you then select the label you want, hit Return, and LaTeXTools inserts the **full ref command**, as in `\ref{my-label}`. The LaTeX command `\eqref` works the same way.  Citations from bibtex files are also supported in a similar way. Use `\cite{}`,  `\citet{}`,  `\citeyear{}` etc.

One often needs to enter **multiple citations**, as e.g. in `\cite{paper1,paper2}`. This is easy to do: either cite the first paper, e.g. `\cite{paper1}` and then, *with your cursor immediately before the right brace*, type a comma (`,`). Again, the default auto-trigger behavior is that the quick panel with appear, and you can select the second paper. If auto-trigger is off, then you enter the comma, then use the shortcut `C-l,x` to bring up the quick panel (note: you *must* add the comma before invoking the shortcut, or you won't get the intended result). Of course, you can enter as many citations as you want.

The display of bibliographic entries is *customizable*. There is a setting, `cite-panel-format`, that controls exactly what to display in each of the two lines each entry gets in the citation quick panel. Options include author, title, short title, year, bibtex key, and journal. This is useful because people may prefer to use different strategies to refer to papers---author-year, short title-year, bibtex key (!), etc. Since only the first line in each quick panel entry is searchable, how you present the information matters. The default should be useful for most people; if you wish to change the format, check the `LaTeXTools.sublime-settings` file for detailed information. (As usual, copy that file to the `User` directory and edit your copy, not the original). s

Thanks to recent contributed code, **multi-file documents** are *fully supported*. If you have a `% !TEX root = ...` directive at the top of the current file, LaTeXTools looks for references, as well as `\bibliography{}` commands, in the root file and in all recursively included files. You can also use a project file to specify the root file (to be documented). 

LaTeXTools now also looks `\addbibresource{}` commands, which provides basic compatibility with biblatex.

### Toggle auto trigger mode on/off ###

**Keybinding:** `C-l,t,a,r` for references; `C-l,t,a,c` for citations

These toggles work just like the sync and focus toggles above. Indeed, `C-l,t,?` will now also display the status of the auto trigger toggles. Check the status bar for feedback (i.e. to see what the current state of the toggle is), but remember the message stays on for only a few seconds. `C-l,t,?` is your friend.



### Old-style, deprecated functionality ###

If auto-trigger is off, you can use either `C-l,x` or `C-l, Ctrl-Space`. I'm **deprecating** `C-l,Ctrl-Space`. It is not as nice to use on the Mac, and the only reason it was there was that it was reminiscent of ST's autocomplete shortcut, `Ctrl-Space` (actually, on the Mac, I think it's `Cmd-Space`, so even that was not much of a mnemonic!). Bottom line: start using `C-l,x`, or better yet, auto trigger.

Earlier versions of LaTeXTools used a different way to trigger ref/cite completions. For references, you typed `ref_`, then `C-l,Ctrl-x`; you could filter by typing, e.g., `ref_a`. Using `refp_` instead of `ref_` would surround the reference with parentheses. You could also use `eqref` to generate `\eqref{my-equation}`. Citations worked the same way: you used `cite_`, etc. If you wanted fancy citations, as in the natbib package, that was allowed, but you had to replace asterisks with `X`: so, to get `\cite*{...}` with old-style completions, you needed to start by typing `citeX_`. This style of ref/cite completion is also **deprecated**. It works for now, but it will almost certainly be removed, unless enough people make a strong enough case for it.

Another note: **for now**, completions are also injected into the standard ST autocompletion system. Thus, if you hit `Ctrl-space` immediately after typing, e.g., `\ref{}`, you get a drop-down menu at the current cursor position (not a quick-panel) showing all labels in your document. This also works with old-style citations. However, the width of this menu is OK for (most) labels, but not really for paper titles. In other words, it is workable for references, but not really for citations. Furthermore, there are other limitations dictated by the ST autocompletion system. So, this is **deprecated**, and I encourage you to use auto-trigger mode or the `C-l,x` keybinding instead.


Jumping to sections and labels
------------------------------

**Keybinding:** `C-r` (standard ST keybinding)

The LaTeXtools plugin integrates with the awesome ST "Goto Anything" facility. Hit `C-r`to get a list of all section headings, and all labels. You can filter by typing a few initial letters. Note that section headings are preceded by the letter "S", and labels by "L"; so, if you only want section headings, type "S" when the drop-down list appears.

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
- `C-l,C-t` gives you `\texttt{blah}`
- `C-l,C-n` wraps the selected text in a LaTeX environment structure. You get `\begin{env}`,`blah`, `\end{env}` on three separate lines, with `env` selected. Change `env` to whatever environment you want, then hit Tab to move to the end of the environment.

These commands also work if there is no selection. In this case, they try to do the right thing; for example, `C-l,C-e` gives `\emph{}` with the cursor between the curly braces.

Command completion, snippets, etc.
----------------------------------

By default, ST provides a number of snippets for LaTeX editing; the LaTeXTools plugin adds a few more. You can see what they are, and experiment, by selecting Tools|Snippets|LaTeX and Tools|Snippets|LaTeXTools from the menu.

In addition, the LaTeXTools plugin provides useful completions for both regular and math text; check out files `LaTeX.sublime-completions` and `LaTeX math.sublime-completions` in the LaTeXTools directory for details. Some of these are semi-intelligent: i.e. `bf` expands to `\textbf{}` if you are typing text, and to `\mathbf{}` if you are in math mode. Others allow you to cycle among different completions: e.g. `f` in math mode expands to `\phi` first, but if you hit Tab again you get `\varphi`; if you hit Tab a third time, you get back `\phi`.


Settings
--------

LaTeXTools now supports user-defined settings. The *default* settings file is called `LaTeXTools.sublime-settings`. This **must** be in the `User` directory. As described above, when you first install LaTeXTools, the file `LaTeXTools.sublime-settings` does not exist anywhere. A migration / reconfiguration command is provided to create this settings file in `User`, and automatically migrate your existing settings from the old file (`LaTeXTools Preferences.sublime-settings`). . You can run it in three ways:

* from the Command Palette (in the Tools) menu, search for "LaTeXTools: Reconfigure and migrate settings"
* from the "Reconfigure LaTeXTools and migrate settings" item in the Preferences, Package Settings, LaTeXTools menu
* from the Sublime Text console (`Ctrl+backtick` on all platforms), typing `sublime.run_command("latextools_migrate")`.

If you ever want to revert your settings to their default state, just invoke the migration command again, as above.

*Warning*:  in general, tweaking options can cause breakage. For instance, if on Linux you change the default `python2` setting (empty by default) to a non-existent binary, forward and inverse search will stop working. With great power comes great responsibility! If you think you have found a bug, *delete your settings file in the `User` directory and rerun the `latextools_migrate` command before reporting it!* Thanks :-)

The following options are currently available (defaults in parentheses):

**General settings**:
- `cite-auto-trigger` (`true`): if `true`, typing e.g. `\cite{` brings up the citation completion quick panel, without the need to type `C-l,x`. If `false`, you must explicitly type `C-l,x`.
- `ref-auto-trigger` (`true`): ditto, but for `\ref{` and similar reference commands
- `keep_focus` (`true`): if `true`, after compiling a tex file, ST retains the focus; if `false`, the PDF viewer gets the focus. Also note that you can *temporarily* toggle this behavior with `C-l,t,f`.
- `forward_sync` (`true`): if `true`, after compiling a tex file, the PDF viewer is asked to sync to the position corresponding to the current cursor location in ST. You can also *temporarily* toggle this behavior with `C-l,t,s`.

**Platform settings**:
- all platforms:
  * `texpath`: the path to TeX & friends
- `windows`-specific settings:
  * `distro`: either `miktex` or `texlive`, depending on your TeX distribution
  * `sumatra`: leave blank or omit if the SumatraPDF executable is in your `PATH` and is called `SumatraPDF.exe`, as in a default installation; otherwise, specify the *full path and file name* of the SumatraPDF executable.
- `linux`-specific settings:
  * `python2` (`""`, i.e. empty string): name of the Python 2 executable. This is useful for systems that ship with both Python 2 and Python 3. The forward/backward search used with Evince require Python 2.
  * `sublime` (`sublime-text`): name of the ST executable. Ubuntu supports both `sublime-text` and `subl`; other distros may vary.
  * `sync_wait` (1.5): when you ask LaTeXTools to do a forward search, and the PDF file is not yet open (for example, right after compiling a tex file for the first time), LaTeXTools first launches evince, then waits a bit for it to come up, and then it performs the forward search. This parameter controls how long LaTeXTools should wait. If you notice that your machine opens the PDF, then sits there doing nothing, and finally performs the search, you can decrease this value to 1.0 or 0.5; if instead the PDF file comes up but the forward search does not seem to happen, increase it to 2.0.

**Build engine settings**:

NOTE: for the time being, you will need to refer to the `LaTeX.sublime-settings` file for detailed explanations. Also, since the new build system is meant to be fully customizable, if you use a third-party builder (which hopefully will become available!), you need to refer to its documentation.
- `builder`: the builder you want to use. Leave blank (`""`) or set to `"default"` or `"traditional"` for the traditional (`latexmk`/`texify`) behavior.
- `builder_path`: builders can reside anywhere Sublime Text can access. Specify a path *relative to the Sublime text Packages directory*. In particular, `User` is a good choice. If you use a third-party builder, specify the builder-provided directory.
- `builder-settings`: these are builder-specific settings. For the `default`/`traditional` builder, the following settings are useful:
  * `program`: one of `pdflatex` (the default), `xelatex` or `lualatex`. This selects the TeX engine.
  * `command`: the precise `latexmk` or `texify` command to be invoked. This is specified exactly as in the `cmd` entry of the old `LaTeX.sublime-build` file (which is no longer honored): it must be a list of strings. The defaults (hardcoded, not shown in the settings file) are `["latexmk", "-cd", "-e", "$pdflatex = '%E -interaction=nonstopmode -synctex=1 %S %O'", "-f", "-pdf"]` for TeXLive, and `["texify", "-b", "-p", "--tex-option=\"--synctex=1\""]` for MiKTeX.
  * In addition, there can be platform-specific settings. An important one for Windows is `distro`, which must be set to either `miktex` or `texlive`.
  * A platform-specific setting that is common to all builders is `env`. This can be used to set environment variables *before* running the actual builder. Setting e.g. `TEXINPUTS` is a possible use case.

**Bibliographic references settings**:

- `cite-panel-format` and `cite_autocomplete_format`: see the section on ref/cite completion, and the comments in `LaTeXTools.sublime-settings`


Customizing the Build System
----------------------------

Starting with the 3/2014 versions, LaTeXTools allows you to fully customize the build process using Python. The default builder (called `traditional`) works like the one in prior releases. 

For minor customizations of the default builder, as noted in the Settings section above, there are two key options. If you want to use, say, `xelatex` instead of `pdflatex` (the default), set the `program` option in `builder-settings`. If instead you want to change the build command completely, set the `command` option there. *There is no longer any need to fiddle with the `LaTeX.sublime-build` file!* In fact, if you have a copy of that file in your User directory, it's best to delete it. However, do *not* delete the `LaTeX.sublime-build` file in the plugin's own directory! That file is now *internal* and shold not be modified. 

Some information on the new flexible builder system: to create and use a new builder, you place the code somewhere off the ST `Packages` directory (for instance, in `User`), then set the `builder` and `builder_path` options in your `LaTeXTools.sublime-settings` file accordingly. A builder can define its own options, also in `LaTeXTools.sublime-settings`, which will be passed whenever a build is invoked.

Due to time constraints, I have not yet been able to document how to write a builder. The basic idea is that you subclass the `PdfBuilder` class in the file `LaTeXTools/builders/pdfBuilder.py`. The comments in that file describe how builders interact with the build command (hint: they use Pyton's `yield` command). I provide three builders (one is in progress and not usable yet). The code is in the `LaTeXTools/builders` directory. You can use them as examples:
- `traditional` is the traditional builder. 
- `simple` does not use external tools, but invokes `pdflatex` and friends, each time checking the log file to figure out what to do next. It is a very, very simple "make" tool, but it demonstrates the back-and-forth interaction between LaTeXTools and a builder.
- `script` (in progress!) will eventually allow the user to specify a list of compilation commands in the settings file, and just execute them in sequence. 

Let me know if you are interested in writing a custom builder!

Troubleshooting
---------------

### Path issues ###

Many LaTeXTools problems are path-related. The `LaTeX.sublime-build` file attempts to set up default path locations for MikTeX, TeXlive and MacTeX, but these are not guaranteed to cover all possibilities. Please let me know if you have any difficulties.

On Mac OS X, just having your `$PATH` set up correctly in a shell (i.e., in Terminal) does *not* guarantee that things will work when you invoke commands from ST. If something seems to work when you invoke `pdflatex` or `latexmk` from the Terminal, but building from within ST fails, you most likely have a path configuration issue. One way to test this is to launch ST from the Terminal, typing

	/Applications/Sublime Text 2.app/Contents/SharedSupport/bin/subl

(and then Return; this is for ST2 of course) at the prompt. If things do work when you run ST this way, but they fail if you launch ST from the Dock or the Finder, then there is a path problem. From the Terminal, type

	echo $PATH

and take note of what you get. Then, run ST from the Dock or Finder, open the console (with ``Ctrl+ ` ``) and type
	
	import os; os.environ['PATH']

and again take note of what you see in the output panel (right above the line where you typed the above command). Finally, look at the `path` keyword in the `osx` section of the `LaTeX.sublime-build` file in the LaTeXTools package directory. For things to work, every directory that you see listed from the Terminal must be either in the list displayed when you type the `import os...` command in the ST console, or else it must be explicitly specified in `LaTeX.sublime-build`. If this is not the case, add the relevant paths in `LaTeX.sublime-build` and *please let me know*, so I can decide whether to add the path specification to the default build file. Thanks!

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
 
