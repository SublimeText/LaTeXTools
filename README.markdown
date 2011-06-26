LaTeX Plugin for Sublime Text 2
===============================

by Marciano Siniscalchi
[http://tekonomist.wordpress.com]

Introduction
------------
This plugin provides several features that simplify working with LaTeX files:

* The ST2 build command takes care of compiling your LaTeX source to PDF using `texify` (Windows/MikTeX) or `latexmk` (OSX/MacTeX). Then, it parses the log file and lists errors and warning. Finally, it launches (or refreshes) the PDF viewer (SumatraPDF on Windows and Skim on OSX) and jumps to the current cursor position.
* Forward and inverse search with the named PDF previewers is fully supported
* Easy insertion of references and citations (from BibTeX files) via tab completion
* Plugs into the "Goto anything" facility to make jumping to any section or label in your LaTeX file(s)
* Smart command completion for a variety of text and math commands is provided
* Additional snippets and commands are also provided

Requirements and Setup
----------------------

On OSX, you need to be running the MacTeX distribution (which is pretty much the only one available on the Mac anyway) and the Skim PDF previewer. Just download and install these in the usual way.

On Windows, only the MikTeX distribution is currently supported (not TeXlive). Also, you must be running a current (>=1.4) version of the Sumatra PDF previewer. Install these as usual; then, add the SumatraPDF directory to your PATH (this requirement will be removed soon). Recent versions of MikTeX add themselves to your PATH automatically, but in case the build system does not work, that's the first thing to check.

Finally, grab this plugin's .zip file from GitHub and extract it to your Packages directory and (re)launch ST2. That's it! 

Note: older versions of the plugin required you to setup the `.MacOS/environment.plist` file. This is *no longer required*.


Compiling LaTeX files
---------------------
TBA

Backward and Forward Search
---------------------------
TBA


References and Citations
------------------------
TBA


Jumping to sections and labels
------------------------------
TBA


Command completion, snippets, etc.
----------------------------------
TBA
