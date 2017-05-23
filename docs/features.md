# General Features

## Project Files

**Project files** are fully supported! You should consult the [subsection on project-specific settings](settings.md#project-specific-settings) for further details.

## Multi-file documents

**Multi-file documents** are supported as follows. If the first line in the current file consists of the text `%!TEX root = <master file name>`, then tex & friends are invoked on the specified master file, instead of the current one. Note: the only file that gets saved automatically is the current one. Also, the master file name **must** have a valid tex extension (i.e., one configured in the `tex_file_exts` settings), or it won't be recognized. 

As an alternative, to using the `%!TEX root = <master file name>` syntax, if you use a Sublime project, you can set the `TEXroot` option (under `settings`):
	
```json
{
	... <folder-related settings> ...

	"settings": {
		"TEXroot": "yourfilename.tex"
	}
}
```

Note that if you specify a relative path as the `TEXroot` in the project file, the path is determined *relative to the location of the project file itself*. It may be less ambiguous to specify an absolute path to the `TEXroot` if possible.

## Previewing

**Preview functions are only available in Sublime Text Build 3118 and newer.**

LaTeXTools has the ability to preview images included in the document using a popup or equations as they are typed using phantoms. Both of these functions rely on [Ghostscript](http://www.ghostscript.com/) and [ImageMagick](http://www.imagemagick.org) being installed and available on your `texpath`.

### Math-Live preview

While editing equations LaTeXTools will preview the result using phantoms. By default this will only preview the currently edited environment, but you can also preview all math environments by adjusting the appropriate settings. See the documentation on [Preview Settings](settings.md#preview-settings)

### Preview images

You can preview images included via the `\includegraphics` command. By default, when you hover over the name of the image, a popup will appear to show the image. Links are provided to open the image itself or the folder containing the image. It is also possible to show all images at once via phantoms. See the documentation on [Preview Settings](settings.md#preview-settings) for details.

## Spell-checking

LaTeXTools parses the `%!TEX spellcheck` directive to set the language for the spell-checker integrated in Sublime Text. The [Dictionaries](https://github.com/titoBouzout/Dictionaries) package is recommended and supported. If you have additional dictionaries, you can add them using the `tex_spellcheck_paths` setting, which is a mapping from the locales to the dictionary paths. Each locale must be lowercase and use only a hyphen as a separator. The dictionary paths must be compatible with those used by Sublime Text's spell-checker. For example `{"en-us": "Packages/Language - English/en_US.dic"}` would be a valid value. For more on Sublime Text support for spell checking, see [the relevant online documentation](http://www.sublimetext.com/docs/3/spell_checking.html).

Since the dictionary package is no longer available via Package Control, you can follow these steps to install it:

1. Open the command palette (`C-shift-p`) and select the entry `Package Control: Add Repository`
2. Paste the url: `https://github.com/titoBouzout/Dictionaries` and press enter
3. Now you can install it as any other package: First select `Package Control: Install Package` in the command panel and afterwards select `Dictionaries` to install it

## Support for non-`.tex` files

LaTeXTools has some degree of support for LaTeX documents that are in files with an extension other than `.tex`. In particular, this feature is designed to work  well with alternative extensions, such as `.ltx`. Other extensions such as `.Rnw` and `.tikz` are supported, but, for now they will be treated as standard LaTeX documents (patches are always welcome!).

This behaviour is controlled through two settings, `tex_file_exts` and `latextools_set_syntax`. For more on these settings, see the documentation on [General Settings](settings.md#general-settings).

Note that while the extension detection is used by features of LaTeXTools, including, other features---especially the completions---depend on the syntax of the file being set to `LaTeX` as well.

## Package Documentation

You can consult the documentation for any LaTeX package by invoking the `View Package Documentation` command via the Command Palette (for now). This relies on your system's `texdoc` command.

## Support for Editing Bibliographies

LaTeXTools has some enhanced support for editing either BibTeX or BibLaTeX `.bib` files. Snippet completions are provided for every entry type supported by either BibTeX or BibLaTeX, as are completions for field names. In addition, LaTeXTools provides smart completions for name fields (such as `author`, `editor`, etc.) and crossrefs. When auto-completions are triggered in a name field, a list of all entered names in the current file is presented. Similarly, when auto-completions are triggered in a crossref field, a list of all current entry keys will be provided.

This behaviour is controlled by a single setting, `use_biblatex` (default: `false`), which indicates whether LaTeXTools should use the BibTeX versions of the auto-completions (this is the default behavior) or the BibLaTeX versions of the auto-completions (if `use_biblatex` is set to `true`).

## Caching

LaTeXTools uses a cache to store relevant information about your document and improve the performance of commands. By default, we try to keep them invisible, so they are stored in the Sublime cache path. Settings relevant to the cache can be found in the [settings section](settings.md#cache-settings)

# Builder Features

Most of the builder features are controlled through the `LaTeXTools.sublime-settings` file. See, in particular, the [section on builder settings](settings.md#builder-settings).

## Default Builder

The default builder (called the `traditional` builder) supports several additional features.

### TeX Engine Selection
If the first line of the current file consists of the text `%!TEX program = <program>`, where `program` is `pdflatex`, `lualatex` or `xelatex`, the corresponding engine is selected. If no such directive is specified, `pdflatex` is the default. Multi-file documents are supported: the directive must be in the *root* (i.e. master) file. Also, for compatibility with TeXshop, you can use `TS-program` instead of `program`.

**Note**: for this to work, you must **not** customize the `command` option in `LaTeXTools.sublime-settings`. If you do, you will not get this functionality. Finally, if you use project files, the `program` builder setting can also be customized there, under `settings`.

### TeX Options
You can pass command-line options to your engine in two ways (thanks Ian Bacher!). One is to use a `%!TEX options = ...` line at the top of your file. The other is to use the `options` builder setting in your settings file. This can be useful, for instance, if you need to allow shell escape. Finally, if you use project files, the `options` builder setting can also be customized there (again, under `settings`).

### Output Directory and Auxiliary Directory
The `--output-directory` and `--aux-directory` flags can be set in several ways:
 * Using a TEX directive, such as `%!TEX output_directory = <path>` near the top of the file.
 * Using the [TeX Options](#tex-options) feature to set `--output-directory` and / or `--aux-directory`.
 * Using the corresponding `output_directory` and `aux_directory` settings detailed in [the settings section](settings.md#output-directory-settings).

There are three special values that can be used, `<<temp>>` `<<project>>` and `<<cache>>`. Their meaning is the same as that found in the [settings section](settings.md#output-directory-settings) and they are described there.

**Note**: the `--aux-directory` flag is only implemented by MiKTeX, so the corresponding settings will only be valid if you are using MiKTeX, as indicated by your `distro` setting. To get similar behavior on TeXLive / MacTeX, you can use the `copy_output_on_build` setting described in the [settings section](settings.md#output-directory-settings) with any of the `output_directory` settings. This will run `pdflatex` / `xelatex` / `lualatex` with the `--output-directory` flag and then copy the resulting PDF to the same directory as your main TeX document.

**Note**: These flags can only be set when using `latexmk` (i.e., the `traditional` builder on OS X and Linux), the `basic` builder or the `script` builder (see below [for documentation on using the script builder](available-builders.md#script-builder)). If you are using `texify` (i.e. the `traditional` builder on MiKTeX) or the simple builder, the `output_directory` and `aux_directory` settings will be ignored.

### Jobname
The `--jobname` flag can be set in several ways:
 * Using a TEX directive, such as `%!TEX jobname = <jobname>` near the top of the file.
 * Using the [TeX Options](#tex-options) feature to set `--jobname`
 * Using the corresponding `jobname` setting detailed in [the settings section](settings.md#output-directory-settings).

**Note**: Jobname can only be set when using `latexmk` (i.e., the `traditional` builder on OS X and Linux), the `basic` builder or the `script` builder (see below [for documentation on using the script builder](available-builders.md#script-builder)). If you are using `texify` (i.e. the `traditional` builder on MiKTeX) or the simple builder, the `jobname` setting wil be ignored.

### Customizing the compilation command
It is possible to customize the command run by setting the `command` option under Builder Settings. See the section on [Builder Settings](settings.md#builder-settings) for details.

**Note**: If you customize the command, the TeX engine selection facility may no longer work because it relies on a specific compilation command. However, if you want to customize or replace `latexmk`/`texify`, you probably know how to select the right TeX engine, so this shouldn't be a concern. Also note that if you are using `latexmk` and you set the `$pdflatex` variable, the TeX options facility will not function, as `latexmk` does not support this.

If you change the compilation command, you are responsible for making it work on your setup. Only customize the compilation command if you know what you're doing.

## Other Builders

If the default builder doesn't meet your needs for any reason, please see the page on [available builders](available-builders.md).

# Viewers

By default, LaTeXTools supports the following viewers, depending on platform:

 * On OS X, Skim
 * On Windows, Sumatra
 * On Linux, Evince

However, it is possible to use other programs to view PDF files. Currently, there are viewers available for Preview.app, Okular and Zathura. These viewers can be chosen by changing the `"viewer"` setting. See the [Viewer Settings](settings.md#viewer-settings) section for details. If you are using an alternate viewer, please see the relevant section under [Available Viewers](available-viewers.md) for any caveats or other instructions. In addition, there is a viewer, called the Command Viewer which can be used to launch a PDF document using the command line.


