# LaTeXTools: A LaTeX Plugin for Sublime Text 2 and 3

# Introduction

LaTeXTools plugin provides several features that simplify working with LaTeX files:

* The ST build command takes care of compiling your LaTeX source to PDF using `texify` (Windows/MikTeX) or `latexmk` (OSX/MacTeX, Windows/TeXlive, Linux/TeXlive). Then, it parses the log file and lists errors and warning. Finally, it launches the PDF viewer and, on supported viewers ([Sumatra PDF](http://sumatrapdfreader.org/free-pdf-reader.html) on Windows, [Skim](http://skim-app.sourceforge.net/) on OSX, and [Evince](https://wiki.gnome.org/Apps/Evince) on Linux by default) jumps to the current cursor position.
* Forward and inverse search with the named PDF previewers is fully supported
* Fill everything including references, citations, packages, graphics, figures, etc.
* Plugs into the "Goto anything" facility to make jumping to any section or label in your LaTeX file(s)
* Smart command completion for a variety of text and math commands
* Additional snippets and commands are also provided
* Fully customizable build command
* Fully customizable PDF viewers
* Full support for project files and multi-file documents
* Easily view package documentation
* Word counts

# Bugs, issues & feature requests

Please read the [Installation](install.md) section carefully to ensure you get up and running as quickly as possible. Help for troubleshooting common issues can be found in the [Troubleshooting](troubleshooting.md) section. For other bugs, issues or to request new features, please get in touch with us via [Github](https://github.com/SublimeText/LaTeXTools).

**Please** [search for existing issues and pull requests](https://github.com/SublimeText/LaTeXTools/issues/?q=is%3Aopen) before [opening a new issue](https://github.com/SublimeText/LaTeXTools/issues/new).
