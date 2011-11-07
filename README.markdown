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

First of all, you need to be running a recent dev version of Sublime Text 2 (ST2 henceforth); as of 9/23/2011, I am on Build 2120. 

Second, grab this plugin's .zip file from GitHub and extract it to your Packages directory (you can open it easily from ST2, by clicking on Preferences|Browse Packages). Then, (re)launch ST2.

Third, follow the OS-specific instructions below.

<br>

On **OSX**, you need to be running the MacTeX distribution (which is pretty much the only one available on the Mac anyway) and the Skim PDF previewer. Just download and install these in the usual way. To configure inverse search with Skim, open the Preferences dialog, select the Sync tab, then:

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

If instead you use TeXlive, comment out the lines between the comments `*** BEGIN MikTeX 2009 ***` and `*** END MikTeX 2009 ***`, and uncomment the lines between the comments `*** BEGIN TeXlive 2011 ***` and `*** END TeXlive 2011 ***`. Do *not* uncomment the `BEGIN`/`END` lines themselves---just the lines between them. Now you are done!

TeXlive has one main advantage over MikTeX: it supports file names and paths with spaces. Furthermore, it is easier to change the compilation engine from the default, `pdflatex`, to e.g. `xelatex`: see below for details (TBA).

Compiling LaTeX files
---------------------

The ST2 Build command (`CMD+B` on OSX; `Ctrl+B` on Windows) takes care of the following:

* It saves the current file
* It invokes the tex build command (`texify` for MikTeX; `latexmk` for TeXlive and MacTeX).
* It parses the tex log file and lists all errors and warnings in an output panel at the bottom of the ST2 window: click on any error/warning to jump to the corresponding line in the text, or use the ST2-standard Next Error/Previous Error commands.
* It invokes the PDF viewer for your platform and performs a forward search: that is, it displays the PDF page where the text corresponding to the current cursor position is located.

Multi-file documents are supported as follows. If the first line in the current file consists of the text `%!TEX root = <master file name>`, then tex & friends are invoked on the specified master file, instead of the current one. Note: the only file that gets saved automatically is the current one.


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

Command completion, snippets, etc.
----------------------------------

By default, ST2 provides a number of snippets for LaTeX editing; the LaTeXTools plugin adds a few more. You can see what they are, and experiment, by selecting Tools|Snippets|LaTeX and Tools|Snippets|LaTeXTools from the menu.

In addition, the LaTeXTools plugin provides useful completions for both regular and math text; check out files `LaTeX.sublime-completions` and `LaTeX math.sublime-completions` in the LaTeXTools directory for details.