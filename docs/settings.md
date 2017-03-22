# Settings

LaTeXTools supports user-defined settings. The settings file is called `LaTeXTools.sublime-settings`. A default version resides in the LaTeXTools plugin directory and **must not be edited** (any edits you make to this file will be overwritten when the package is upgraded). This contains default settings that will work in many cases for standard configurations of TeX distros and PDF viewers.

You can however create another settings file in your `User` directory which can override any of the default settings. You can create and edit such a file manually. However, the *simplest way to create a settings file* is to open the **Preferences | Package Settings | LaTeXTools** submenu and select the **Settings - User** option. If you do not currently have a `LaTeXTools.sublime-settings` settings file in your `User` directory (e.g., if you are installing LaTeXTools for the first time), you will be given the option to create one. The newly created settings file can be an exact copy of the default one, and will open in a tab for you to customize. 

If you *do* already have an existing `LaTeXTools.sublime-settings` file in your `User` directory, the **Settings - User** option will open that file in a tab for you to further customize. Similarly, the **Settings - Default** option will open the default settings file in a tab, in *read-only mode*. This may be useful for you to copy from, or if you want to see what other options may be available without consulting this README file.

If at any time you wish to erase your customizations and start afresh, you can simply delete the `LaTeXTools.sublime-settings` file in your `User` directory. (Again, *warning*: do *not* touch the settings file in the LaTeXTools plugin directory!) Alternatively, from the **Preferences | Package Settings | LaTeXTools** submenu, or from the Command Palette, you can choose **Reset user settings to default**. This will delete any existing settings file in `User` and create a copy of the default one. This will  *remove all your customizations*.  (Historical note: This is no longer relevant in 2016, but just for the record, if you have a pre-2014, old-style settings file, this option will migrate it).

**Warning**:  in general, tweaking options can cause breakage. For instance, if on Linux you change the default `python` setting (empty by default) to a non-existent binary, forward and inverse search will stop working. With great power comes great responsibility! If you think you have found a bug, *delete your settings file in the `User` directory, or use the **Reset user settings to default** command before reporting it!* Thanks :-)

## General Settings

* `cite_auto_trigger` (`true`): if `true`, typing e.g. `\cite{` brings up the citation completion quick panel, without the need to type `C-l,x`. If `false`, you must explicitly type `C-l,x`.
* `ref_auto_trigger` (`true`): ditto, but for `\ref{` and similar reference commands
* `fill_auto_trigger` (`true`): ditto, but for package and file inclusion commands (see Fill Helper feature above)
* `env_auto_trigger` (`true`): ditto, but for environment completions
* `glossary_auto_trigger` (`true`): ditto, but for glossary completions
* `tex_directive_auto_trigger` (`true`): ditto, but for tex directive completions
* `cwl_autoload` (`true`): whether to load cwl completions based on packages (see the LaTeX-cwl feature) 
* `cwl_completion` (`prefixed`): when to activate the cwl completion poput (see LaTeX-cwl feature above)
* `cwl_list` (`["latex-document.cwl", "tex.cwl", "latex-dev", "latex-209.cwl", "latex-l2tabu.cwl", "latex-mathsymbols.cwl"]`): list of cwl files to load
* `keep_focus` (`true`): if `true`, after compiling a tex file, ST retains the focus; if `false`, the PDF viewer gets the focus. Also note that you can *temporarily* toggle this behavior with `C-l,t,f`.This can also be overridden via a key-binding by passing a `keep_focus` argument to `jump_to_pdf`.
 **Note**: In general, `keep_focus` set to `true` tries to mean "do not *change* the focus". This isn't always possible, since several of the viewers will steal focus by default. In those circumstances, LaTeXTools tries to actively return the focus to Sublime. To disable this, set the `disable_focus_hack` setting to `true`.
 **Note**: If you are on either Windows or Linux you may need to adjust the `sublime_executable` setting for this to work properly. See the [Platform settings](#platform-specific-settings) below.
* `forward_sync` (`true`): if `true`, after compiling a tex file, the PDF viewer is asked to sync to the position corresponding to the current cursor location in ST. You can also *temporarily* toggle this behavior with `C-l,t,s`. This can also be overridden via a key-binding by passing a `forward_sync` argument to `jump_to_pdf`.
* `tex_file_exts` (`['.tex']`): a list of extensions that should be considered TeX documents. Any extensions in this list will be treated exactly the same as `.tex` files. See the section on [Support for non-`.tex` files](#support-for-non-tex-files).
* `latextools_set_syntax` (`true`): if `true` LaTeXTools will automatically set the syntax to `LaTeX` when opening or saving any file with an extension in the `tex_file_exts` list.
* `overwrite_goto_overlay` (`true`): Set this to `false` to disable the overwriting of the goto overlay for the hotkey `C-r` and `C-shift-r` You can still access the "table of content quickpanel" via `C-l, C-r` and `C-shift-l, C-r
* `use_biblatex`: (`false`): if `true` LaTeXTools will use BibLaTeX defaults for editing `.bib` files. If `false`, LaTeXTools will use BibTeX defaults. See the section on [Support for Editing Bibliographies](#support-for-editing-bibliographies) for details.
* `tex_spellcheck_paths` (`{}`): A mapping from the locales to the paths of the dictionaries. See the section [Spell-checking](#spell-checking).
* `word_count_sub_level` (`"none"`): controls the level at which subcounts of words can be generated. Valid values are: `"none"`, `"part"`, `"chapter"`, and `"section"`.
* `temp_files_exts`: list of file extensions to be considered temporary, and hence deleted using the `C-l, backspace` command.
* `temp_files_ignored_folders`: subdirectories to skip when deleting temp files.

## Preview Settings

### Math-Live Preview Settings

* `preview_math_mode` (`"selected"`): The mode to preview math environments, possible values are:
  * `"all"`:       to show a phantom for each math environment
  * `"selected"`:  to show a phantom only for the currently selected math environment
  * `"none"`:      to disable math live preview
* `preview_math_latex_compile_program` (`"pdflatex"`): The program to compile the latex template files, possible values are `"pdflatex"`, `"xelatex"`, `"lualatex"`, `"latex"`.
* `preview_math_color` (`""`): The color of the text in the preview math phantoms. The format can either be RGB based "#RRGGBB" (e.g. `"#FFFF00"`)
or a color name (e.g. `"yellow"`) If it is the empty string `""` it will be guessed based in the color scheme.
* `preview_math_background_color` (`""`): The background color of the preview math phantoms. In contrast to the foreground color you may also edit your colorscheme to change this. The format can either be RGB(A) based `"#RRGGBB"` (e.g. `"#0000FF"` or `"#0000FF50"`) or a color name (e.g. `"blue"`). If it is the empty string `""` the default color will be used.
* `preview_math_template_packages`: An array containing the used packages for the template as latex code.
* `preview_math_template_preamble` (`""`): An string of the remaining preamble (not packages) for the file, which generates the math live preview. Can also be an array, with an string for each line (as in the packages). This is useful, if you define math commands or operators on your own. You may change this per project basis.
* `preview_math_density` (`300`): The density of the preview image. The higher the density the larger the phantom.
* `preview_math_scale_quotient` (`2`): If the image is not sharp enough increase this scale to get a better resolution. However also change the density by the same factor to keep the size.

#### Preview Image Settings

* "preview_image_mode": (`"hover"`),
   The preview mode for image preview, possible values are:
  * `"all"`:       to show a phantom for each `\includegraphics` command
  * `"selected"`:  to show a phantom only for the currently selected `\includegraphics` command
  * `"hover"`:     to show a popup if you hover over an `\includegraphics` command
  * `"none"`:      to disable image preview
* `preview_popup_image_size` (`200`) and `preview_phantom_image_size` (`150`): The image size in the preview image popup and phantoms. These are the outer dimensions of the maximal size. The image will be scaled down to fit into these dimensions. It can either be an number or an array, which consist of two numbers (x and y), e.g. [200, 150].
* `preview_image_scale_quotient` (`1`): Increase this number to get a better resolution on high dpi displays. Control the thumbnail image size, which will be generated to preview images, that are not natively supported (like pdf files). E.g. a image size of 300 with a scale quotient of 2 will create a thumbnail with the size 600, which is scaled down in the popup.

## Platform-Specific Settings

This section refers to setting that can be found in a platform-specific block for each platform, i.e., `"osx"`, `"windows"`, or `"linux"`.

### All Platforms

  * `texpath` (varies): the path to TeX & friends. Note that this should always include `$PATH` to ensure the default path is loaded as well.

### Windows

  * `distro` (`miktex`): either `miktex` or `texlive`, depending on your TeX distribution
  * `sumatra` (`""`): leave blank or omit if the SumatraPDF executable is in your `PATH` and is called `SumatraPDF.exe`, as in a default installation; otherwise, specify the *full path and file name* of the SumatraPDF executable.
  * `sublime_executable` (`""`): this is used if `keep_focus` is set to true and the path to your sublime_text executable cannot be discovered automatically. It should point to the full path to your executable `sublime_text.exe`.
  * `keep_focus_delay` (`0.5`): this is used if `keep_focus` is set to true. It controls how long (in seconds) the delay is between the completion of the `jump_to_pdf` command and the attempt to refocus on Sublime Text. This may need to be adjusted depending on your machine or configuration.

### Linux
  * `python` (`""`, i.e. empty string): name of the Python executable. This is useful if you've installed Python in a non-standard location or want to ensure that LaTeXTools uses a particular Python version. Note that the Python interpreter you select must have the DBus bindings installed.
  * `sublime` (`sublime-text`): name of the ST executable. Ubuntu supports both `sublime-text` and `subl`; other distros may vary.
  * `sync_wait` (1.0): when you ask LaTeXTools to do a forward search, and the PDF file is not yet open (for example, right after compiling a tex file for the first time), LaTeXTools first launches evince, then waits a bit for it to come up, and then it performs the forward search. This parameter controls how long LaTeXTools should wait. If you notice that your machine opens the PDF, then sits there doing nothing, and finally performs the search, you can decrease this value to 1.0 or 0.5; if instead the PDF file comes up but the forward search does not seem to happen, increase it to 2.0.
  * `sublime_executable`: this is used if `keep_focus` is set to true and the path to your sublime_text executable cannot be discovered automatically. It should point to the full path to your executable `sublime_text`.
  * `keep_focus_delay`: this is used if `keep_focus` is set to true. It controls how long (in seconds) the delay is between the completion of the `jump_to_pdf` command and the attempt to refocus on Sublime Text. This may need to be adjusted depending on your machine or configuration.

## Output Directory Settings

* `aux_directory` (`""`): specifies the auxiliary directory to store any auxiliary files generated during a LaTeX build. Note that the auxiliary directory option is only useful if you are using MiKTeX. Path can be specified using either an absolute path or a relative path. If `aux_directory` is set from the project file, a relative path will be interpreted as relative to the project file. If it is set in the settings file, it will be interpreted relative to the main tex file. In addition, the following special values are honored:
  * `<<temp>>`: uses a temporary directory in the system temp directory instead of a specified path; this directory will be unique to each main file, but does not persist across restarts.
  * `<<cache>>`: uses the ST cache directory (or a suitable directory on ST2) to store the output files; unlike the `<<temp>>` option, this directory can persist across restarts.
  * `<<project>>`: uses a sub-directory in the same folder as the main tex file with what should be a unique name; note, this is probably not all that useful and you're better off using one of the other two options or a named relative path
* `output_directory` (`""`): specifies the output directory to store any file generated during a LaTeX build. Path can be specified using either an absolute path or a relative path. If `output_directory` is set from the project file, a relative path will be interpreted as relative to the project file. If it is set in the settings file, it will be interpreted relative to the main tex file. In addition, output_directory honors the same special values as `auxiliary_directory`.
* `jobname` (`""`): specifies the jobname to use for the build, corresponding to the pdflatex `--jobname` argument.
* `copy_output_on_build` (`true`): if `true` and you are using an `output_directory`, either set via the setting or the `%!TEX` directive, this instructs LaTeXTools to copy to resulting pdf to the same folder as the main tex file. If you are not using `output_directory` or it is set to `false`, it does nothing. If it is a list of extensions, it will copy each file with the same name as your main tex file and the given extension to the same folder as your main tex file. This is useful for copying, e.g., .synctex.gz or .log files.

## Builder Settings

**Note:** Since the build system is meant to be fully customizable, if you use a third-party builder (which hopefully will become available!), you need to refer to its documentation.

* `builder` (`"traditional"`): the builder you want to use. Possible values:
	* `"default"` or `""` or `"traditional"`: this is the standard LaTeXTools builder, which builds the document using `texify` on MiKTeX or `latexmk` on TeXLive or MacTeX. The majority of the documentation is written assuming you are using this builder.
	* `"basic"`: invokes `pdflatex` / `xelatex` / `lualatex` to build the document. If the log indicates it is necessary, it then runs  `biber` or `bibtex` and then two additional runs of `pdflatex` / `xelatex` / `lualatex`. Mostly supports the same features as the `traditional` builder.
	* `"script"`: invokes the set of commands specified in the `"script_commands"` setting in the platform-specific part of the `"builder_settings"`. See [the documentation](available-builders.md#script-builder) for details.
	* `"simple"`: invokes `pdflatex` 1x or 2x as needed, then `bibtex` and `pdflatex` again if needed; intended mainly as a simple example for people writing their own build engines.
	* Other values can be used to indicate the use of a custom build system. Note that custom builder **cannot** have the same name as a built-in engine. For an overview of how to write a custom builder, see [the custom builder section of the documentation](available-builders.md#custom-builder)
* `builder_path` (`""`):  if not empty, specifies a path to a custom builder, *relative to the Sublime Packages directory*. For instance, `User/builders` could be used to indicate that the custom builder is to be found in the `builder` subdirectory of the `User` package. This is only needed if you are using a third-party or custom builder.
* `builder-settings`: this contains builder-specific settings.
	* `display_log` (`false`): if `true` the output of each command will be displayed in the output panel. This can be useful for troubleshooting issues with the build system and is supported by all built-in build systems.
	*`env` (unset): a dictionary of key-values corresponding to environment variables that should be set for the environment the build is run in. Note that `env`, if it is set, must be set at the platform-specific level, e.g., under the `osx`, `windows`, or `linux` keys. This is useful for setting, e.g., `TEXINPUTS`.
	For the `default`/`traditional` builder, the following settings are useful:
		* `program` (unset): one of `pdflatex` (the default), `xelatex` or `lualatex`. This selects the TeX engine.
		* `command` (unset): the precise `latexmk` or `texify` command to be invoked. This  must be a list of strings. The defaults (hardcoded, not shown in the settings file) are:
			* (TeXLive): `["latexmk", "-cd", "-e", "-f", "-%E", "-interaction=nonstopmode", "-synctex=1"]`
			* (MiKTeX): `["texify", "-b", "-p", "--engine=%E", "--tex-option=\"--synctex=1\""]`
		* `options` (unset): allows you to specify a TeX option, such as `--shell-escape`. This must be a tuple: that is, use `options: ["--shell-escape"]`
	The `basic` builder also supports the `program` and `options` options.
	For the script builder, the following setting is **required**:
		* `script_commands` (unset): a command or list of commands to run. Each command can be either a string or a list, e.g.:
			* "pdflatex -synctex=1 -interaction=nonstopmode"
			* ["pdflatex", "-synctex=1", "-interaction=nonstopmode"]
		See the [the Script Builder documentation](available-builders.md#script-builder) for details.

## Build Panel Settings

* `highlight_build_panel` (`true`): if `true` the build panel will have a syntax applied to highlight any errors and warnings. Otherwise, the standard output panel configuration will be used.
* `hide_build_panel` (`"no_badboxes"`): controls whether or not to hide the build panel after a build is finished. Possible values:
	* `"always"`: never show the build panel at all
	* `"no_errors"`: only show the build panel if errors occur
	* `"no_warnings"`: only hide the panel if no warnings occur
	* `"no_badboxes"`: only hide the panel if no warnings or badbox messages occur; this only differs from `no_warnings` if `display_bad_boxes` is set to `true`.
	* `"never"`: never hide the build panel
Any other value will be interpretted as the default.
* `display_bad_boxes` (`false`): if `true` LaTeXTools will display any bad boxes encountered after a build. Note that this is disabled by default.
* `show_error_phantoms` (`"warnings"`): **ST3 Build 3118 or newer only** controls which errors are displayed via phantoms. Possible values:
	 * `"none"`: never show any phantoms at all
	 * `"errors"`: only show errors using phantoms
	 * `"warnings"`: only show warnings or errors using phantoms
	 * `"badboxes"`: show any warnings, errors, or bad box messages use phantoms
* `build_finished_message_length` (`2.0`): the number of seconds to display the status bar message about the completion of the build

## Viewer Settings

 * `viewer` (`""`): the viewer you want to use. Leave blank (`""`) or set to `"default"`for the platform-specific viewer. Can also be set to `"preview"` if you want to use Preview on OS X, `"okular"` if you want to use Okular on Linux, `"zathura"` is you want to use Zathura on Linux, or `"command"` to run arbitrary commands. For details on the `"command"` option, see the section on the [Command Viewer](#command-viewer).
 * `viewer_settings`: these are viewer-specific settings. Please see the section on [Viewers](#viewers) or the documentation on [Alternate Viewers](#alternate-viewers) for details of what should be set here.
 * `open_pdf_on_build` (`true`): Controls whether LaTeXTools will automatically open the configured PDF viewer on a successful build. If set to `false`, the PDF viewer will only be launched if explicitly requested using `C-l,v` or `C-l,j`.
  * `disable_focus_hack` (`false`): if `true`, the focus hack that LaTeXTools uses to return focus to Sublime in some circumstances will not be run. **Note**: This does not mean that the *viewer* won't steal the focus, only that LaTeXTools won't try to steal the focus back.

## Included File Settings

 * `"image_types"` (`["png", "jpg", "jpeg", "pdf" "eps"]`): image types that you use in LaTeX. These are used for autocompletions and to open included images where no extension is provided. Broadly speaking, this should correspond to any `\DeclareGraphicsExtensions{}` commands used in your document, but the default value corresponds to the types of images supported by `pdflatex` (they are also supported by `xelatex` and `lualatex`).

## Bibliographic References Settings

* `bibliography` (`"traditional"`): specifies the bibliography plugin to use to handle extracting entries from a bibliography. May be specified either as a single plugin or a list of plugins to be executed in order. Possible values:
	* `"traditional"`: the default bibliography which is quite fast and works for most situations.
	* `"new"`: a newer bibliography engine which uses a full Bib(La)TeX parser that supports more complex formatting (multiline entries, values enclosed in double quotes `""`, literals and `@string` macros) and allows you to access more fields, but can be slower and may not be necessary for most bibliographies.
* `cite_panel_format` (`["{author_short} {year} - {title_short} ({keyword})","{title}"]`): specifies the format for bibliography entries displayed in the quickpanel when typing `\cite{` or using one of the keybindings. It may either be a string or a list of two strings. In the latter case, the first string becomes the first line of the text displayed in the quick panel and the second the second.
* `cite_autocomplete_format`(`"{keyword}: {title}"`): specifies the format for bibliography displayed when using Sublime's autocomplete functionality (`ctrl+space` or `alt+/`). Must be only a simple string.

### Bibliography Format Strings

The two `cite_xxx_format` settings take simple format strings to tell LaTeXTools how to display the settings. Fields from the bibliography can be displayed using wildcards wrapped in `{}`. For example, using the value: `["{title} ({keyword})", "{author}"]` for `cite_panel_format` would produce and entry like this:

	Can quantum-mechanical description of physical reality be considered complete? (einstein1935quantum)
	Albert Einstein and B Podolsky and N Rosen

Using the `traditional` bibliography, the following fields are supported: `keyword`, `title`, `author`, `year`, and `journal`. In addition, LaTeXTools provides two useful pseudo-fields: `title_short` and `author_short`, which display shortened versions of the title or author respectively. Using the `new` bibliography, any field can be used. `title_short` and `author_short` are also provided, but `title_short` first tries to use the `shorttitle` BibLaTeX field, if it is available.

The default `cite_panel_format` produces output like the following:

	Einstein et al. 1934 - Can quantum-mechanical description of physical reality be co (einstein1935quantum)
	Can quantum-mechanical description of physical reality be considered complete?

Other example formats are provided in the settings file.

## Cache Settings

* `hide_local_cache` (`true`): Whether the local cache should be hidden in the sublime cache path (`true`) or in the same directory as the root file (`false`). See the section [LaTeXTools Cache](#latextools-cache).
* `local_cache_life_span` (`30 m`): The lifespan of the local cache, specified in the format `" d x h X m X s"` where `X` is a natural number `s` stands for seconds, `m` for minutes, `h` for hours, and `d` for days. Missing fields will be treated as 0 and white-spaces are optional. Hence you can write `"1 h 30 m"` to refresh the cached data every one and a half hours. If you use `"infinite"` the cache will not be invalidated automatically. A lower lifespan will produce results, which are more up to date. However it requires more recalculations and might decrease the performance.

## Project-Specific Settings

Any settings can be overridden on a project-specific basis if you are using SublimeText's [project system](https://www.sublimetext.com/docs/3/projects.html). In addition, you can use the `TEXroot` setting in the project file only to specify the master tex file instead of using `%!TEX root =` magic comments. If specified in the project file, the `TEXroot` will be resolved relative to the location of your `.sublime-project` file. Similarly, if you use `output_directory` or `aux_directory` in the project file, they will be resolved relative to the location of the project file.

To use project-specific settings, simply create a [`"settings"` section in your project file](http://docs.sublimetext.info/en/latest/file_management/file_management.html#the-sublime-project-format). The structure and format is the same as for the `LaTeXTools.sublime-settings` file. Here is an example:

```json
{
	... <folder-related options here> ...

	"settings" : {
		"TEXroot": "main.tex",
		"tex_file_exts": [".tex", ".tikz"],
		"builder_settings": {
			"program": "xelatex",
			"options": "--shell-escape"
		}
	}
}
```

This sets `main.tex` as the master tex file (assuming a multi-file project), and allows `.tikz` files to be recognized as tex files. Furthermore (using the default, i.e., traditional builder), it forces the use of `xelatex` instead of the default `pdflatex`, and also adds the `--shell-escape` option. All of these settings will only apply while in the current project.

**Note:** tweaking settings on a project-specific level can lead to subtle issues that can be difficult to track down. If you notice a bug, in addition to resetting your `LaTeXTools.sublime-settings` file, you should remove any LaTeXTools settings from your project file.

