#LyTeXTools: LilyPond-aware LaTeXTools for Sublime Text 2

This package forks and adds `lilypond-book` support to [Marciano Siniscalchi’s](http://tekonomist.wordpress.com/) [LaTeXTools](http://github.com/SublimeText/LaTeXTools) package for [Sublime Text 2](http://www.sublimetext.com/2).

A component of [GNU LilyPond](http://lilypond.org), the formidable music typesetter, `lilypond-book` enables LaTeX writers to include LilyPond code snippets within LaTeX documents, thereby freely mixing text with musical notation. It is a command-line preprocessor that “extracts snippets of music from your document, runs LilyPond on them, and outputs the document with pictures substituted for the music.”

Overall, LyTeXTools extends LaTeXTools in the following ways:

* It accepts `.lytex` (LaTeX with inline Lilypond) in addition to `.tex` (plain LaTeX) source files.
* It instructs `lilypond-book` to preprocess the current document, and to produce a `.tex` file if applicable, prior to invoking latexmk.
* It extends the SyncTeX functionality, with seamless “forward” and “inverse” search capabilities regardless of the source file extension (`.tex` or `.lytex`). Unfortunately, as `lilypond-book` provides no native support for SyncTeX, this functionality would be best described as a hack and relies on a bash script for OS X (see below). Users are warmly invited to contribute a port of this short and straightforward script to Windows.

As a functional extension of LaTeXTools, LyTeXTools is intended to behave identically with its original counterpart when invoked with plain `.tex` files.

## Installation (OS X)

To avoid confusion, and given its lack of support for Windows at present, LyTeXTools has not been submitted to [Will Bond’s](http://wbond.net) [Package Control](http://wbond.net/sublime_packages/package_control). You may install the package manually by cloning (or copying the unzipped contents of) this repository into your `./Packages` folder:

	git clone https://github.com/yrammos/LyTeXTools.git

New users unfamiliar with Marciano Siniscalchi’s LaTeXTools are advised to read his detailed and lucid [documentation](http://github.com/SublimeText/LaTeXTools#requirements-and-setup first The following notes only address areas where the two packages diverge.

## Settings specific to the LyTeXTools fork

The following settings override those of the original LaTeXTools. All other LaTeXTools settings still apply to LyTeXTools.

### Inverse search

“Forward-” and “inverse” search with `.lytex` files are non-trivial because SyncTeX only provides a mapping between the PDF and the preprocessed `.tex`, whereas the actual source file is the `.lytex`. LyTeXTools undertakes the missing link, namely a bidirectional mapping between `.tex` and `.lytex` line numbers.

The package relies on the `sublsync` script to provide inverse search from the PDF (Skim.app) to the `.lytex` or `.tex` source. `sublsync` is provided as part of LyTeXTools. Its purpose is to store the SyncTeX-generated coordinates (source file name, line number) into a file whence LyTeXTools can then retrieve them.

By default, LyTeXTools expects this file to be `~/.sublatex.txt`. This may be overriden via a synctex_output key-value pair in a LyTeXTools.sublime-settings JSON file, for example:

	{
    	"synctex_output":   "~/path/file.extension"
	}

Please ensure you have adequate write privileges in that path.

But enough with theory and preliminaries. To actually set up Skim.app:

1. Go to Skim > Preferences > Sync.
2. Under "Preset" select "Custom."
3. Deselect the "Check for file changes" box.
4. In the Command field enter `<full_path_to_LyTeXTools_Package>/sublsync`.
5. In the Arguments field enter `~/.sublatex.txt "%file" %line "/usr/local/bin/"`. <br>Optionally, replace:<br>
	a. The `~/.sublatex.txt` default with whatever setting you have overriden it with (per instructions above).<br>
	b. `"/usr/local/bin/"` with the full path to the subl binary (which launches Sublime Text from the command line). Remember to enclose it in quotation marks if your path includes spaces!

### Path considerations

The process will likely fail unless the path to the `lilypond-book` binary is included in the path key-value pair in LaTeX.sublime-build, for example:

	"osx":  {
    	        ...
        	    "path" : "$PATH:/usr/texbin:/usr/local/bin:/Applications/LilyPond.app/Contents/Resources/bin/"
            	...
	        }

### Technical note: Detection of LilyPond scopes in LaTeX code

In order to accurately map `.tex` line numbers to `.lytex` line numbers and vice-versa, LyTeXTools must be able to unambiguously identify LilyPond scopes, both within the source (`.lytex`) file and within the LilyPond-generated `.tex` file.

LilyPond scopes in the `.lytex` file are trivial to identify:

	\begin[...]{lilypond}
		...
	\end{lilypond}

The situation appears less straightforward on the `.tex` side. So far, I have been able to identify only two pairs of delimiters that may wrap the generated LilyPond code:

	\begin{quote}
	...
	\end{quote}

and a rather bland pair of curly brackets:

	{
		...
	}

It is obvious that neither pair can be unambiguously attributed to LilyPond. To address possible mismatches, I am considering to propose a "comment-based" pair of delimiters, for example `#! \LYTEX` and `#! LYTEX\`. Depending on user feedback, I may implement such a scheme in the future. So far, I have found the current lightweight implementation to be adequate.

© 2012 [Yannis Rammos](twitter.com/yannisrammos)