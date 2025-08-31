# Available Builders

## Traditional Builder

By default, LaTeXTools uses the `traditional` builder, which is designed to work in most circumstances and for most setups. This builder provides all of the builder features discussed elsewhere in the documentation, such as the various [builder features](features.md#default-builder), including multi-document support, the ability to set LaTeX flags via the `TeX Options` settings, etc.

When you are using MiKTeX, the `traditional` builder defaults to using the MiKTeX compiler driver [`texify`](https://docs.miktex.org/manual/texifying.html), which automatically runs PDFLaTeX / XeLaTeX / LuaLaTeX as many times as necessary to generate a document. Note that because of certain limitations of `texify`, some features, such as support for output directory, auxiliary directory, jobname, etc. are unavailable when using the traditional builder. You can change this by installing `latexmk` and changing the `command` setting in the `builder_settings` block to `"latexmk -cd -f -%E -interaction=nonstopmode -synctex=1"`, in which case the `traditional` builder will run `latexmk` instead of `texify`

When you are using any other setup (MacTeX or TeXLive on Linux or Windows), the `traditional` builder uses [`latexmk`](https://www.ctan.org/pkg/latexmk/), which supports all the documented features for the builder.

## Basic Builder

The basic builder is a simple, straight-forward build system. that simply runs the configured build engine (pdflatex, xelatex, or lualatex) and bibtex or biber if necessary. It can also be configured to support bibtex8 through the `bibtex` builder setting. In addition, it supports the [TeX Options](features.md#tex-options) feature, the [output and auxiliary directory](features.md#output-directory-and-auxiliary-directory) features and the [Jobname](features.md#jobname) feature. It has been included because the default builder on MiKTeX, `texify` cannot be easily coerced to support biber or any of the other features supported by the basic builder. Note, however, that unlike `texify`, the basic builder does **not** support `makeindex` and friends (patches are welcome!).

You can use the basic builder by changing the `builder` setting to `"basic"`. It will read the same settings as the traditional builder.

## Script Builder

The `script` builder is an advanced feature to design custom compile workflows via settings.

Its primary goals are:

1. support customization of simple build workflows
2. enable LaTeXTools to integrate with external build systems in some fashion.

Unlike the "traditional" builder it is not designed to "just work," and is not recommend for those new to using TeX and friends. Please read this section carefully before using `script` builder.

Instead of invoking `texify` or `latexmk`, a user-defined series of commands is executed. Note that although **multi-file documents** are supported, engine selection or passing other options via the `%!TEX` macros is not possible.

**Note:** To use `script` builder set `"builder": "script"` in sublime-build file or any of the supported settings.

### Settings

The `script` builder is controlled through settings in *platform-specific* part of `builder_settings` of `LaTeXTools.sublime-settings`, or of the current project file (if any):

- `script_commands` — the command or list of commands to run. This setting **must** have a value or you will get an error message.
- `env` — a dictionary defining environment variables to be set for the environment the command is run in.

If `script_commands` is a string, it represents a single command to be executed:

```json
{
	"builder_settings": {
		"osx": {
			"script_commands": "pdflatex -synctex=1 -interaction=nonstopmode"
		}
	}
}
```

If `script_commands` is a list, it can be a list of strings representing single commands:

```json
{
	"builder_settings": {
		"osx": {
			"script_commands": [
				"pdflatex -synctex=1 -interaction=nonstopmode",
				"bibtex",
				"pdflatex -synctex=1 -interaction=nonstopmode",
				"pdflatex -synctex=1 -interaction=nonstopmode"
			]
		}
	}
}
```

or a list of lists, representing arguments of each command:

```json
{
	"builder_settings": {
		"osx": {
			"script_commands": [
				["pdflatex", "-synctex=1", "-interaction=nonstopmode"],
				["bibtex"],
				["pdflatex", "-synctex=1", "-interaction=nonstopmode"],
				["pdflatex", "-synctex=1", "-interaction=nonstopmode"]
			]
		}
	}
}
```

All specified commands are unconditionally executed subsequently using login shell (e.g.: bash on Linux or cmd.exe on Windows). This means, in the above example, it will run `bibtex` regardless of whether there are any citations.

The batch is aborted as soon as a commend returns with non-zero exit status.

It is especially important to ensure TeX and friends do not stop for user input. For example, if you use `pdflatex`, pass the `-interaction=nonstopmode` option.

### Variables

Each command can use the following variables which will be expanded before it is executed:

| Variable            | Description
|---------------------|------------------------------------------------------------------------------------
| `$file`             | The full path to the main file, e.g., _C:\\Files\\document.tex_
| `$file_name`        | The name of the main file, e.g., _document.tex_
| `$file_ext`         | The extension portion of the main file, e.g., _tex_
| `$file_base_name`   | The name portion of the main file without the extension, e.g., _document_
| `$file_path`        | The directory of the main file, e.g., _C:\\Files_
| `$aux_directory`    | The auxiliary directory set via a `%!TEX` directive or the settings
| `$output_directory` | The output directory set via a `%!TEX` directive or the settings
| `$jobname`          | The jobname set via a `%!TEX` directive or the settings
| `$eol`              | Will be replaced by empty string, preventing automatic `$file_base_name` appending

**Note:** If none of these variables occur in a command string, the `$file_base_name` will be appended. This may mean that a wrapper script is needed if, for example, using `make`

Commands are executed in the same path as `$file_path`, i.e. the folder containing the main document. Note, however, on Windows, since commands are launched using `cmd.exe`, you need to be careful if your root document is opened via a UNC path (this doesn't apply if you are simply using a mapped drive). `cmd.exe` doesn't support having the current working directory set to a UNC path and will change the path to `%SYSTEMROOT%`. In such a case, just ensure all the paths you specify are absolute paths and use `pushd` in place of `cd`, as this will create a (temporary) drive mapping.

### Output and Auxiliary Directories

If [auxiliary or output directory settings](settings.md#output-directory-settings) are specified, script builder creates them before batch execution. They are provided by [variables](#variables) and need to be passed to relevant commands in `script_commands`.

`pdflatex` and friends do not create (sub-)directories as needed. If `\include` is used (or anything attempts to `\@openout` a file in a subfolder), they must be created manually by script commands like  `"mkdir $output_directory\chapters"` (Windows) or `"mkdir -p $output_directory/chapters"` (Linux/MacOS).

**BibTeX**

Unlike biber, bibtex (and bibtex8) does not support an output directory parameter.
The following workaround can be used to run BibTeX _inside_ the output / auxiliary directory while making the directory containing your main file available to the `BIBINPUTS` environment variable.

```json
{
	"builder_settings": {
		"linux": {
			"script_commands": [
				"cd $output_directory; BIBINPUTS=\"$file_path;$BIBINPUTS\" bibtex \"$file_base_name\"",
			]
		},
		"windows": {
			"script_commands": [
				"cd $output_directory & set BIBINPUTS=\"$file_path:%BIBINPUTS%\" & bibtex \"$file_base_name\""
			]
		}
	}
}
```

**Note:** If a custom style file is used in the same directory, a similar work-around for `BSTINPUTS` environment variable needs to be applied.

### Job Name

If jobname behaviour is used, `$jobname` is to be passed to relevant commands. In particular, a standard build cycle might look something like this:

```json
{
	"builder_settings": {
		"osx": {
			"script_commands": [
				"pdflatex -synctex=1 -interaction=nonstopmode -jobname=$jobname \"$file_base_name\"",
				"bibtex $jobname",
				"pdflatex -synctex=1 -interaction=nonstopmode -jobname=$jobname \"$file_base_name\"",
				"pdflatex -synctex=1 -interaction=nonstopmode -jobname=$jobname \"$file_base_name\""
			]
		}
	}
}
```

### Caveats

LaTeXTools makes some assumptions that should be adhered to or else things won't work as expected:
- the final product is a PDF which will be written to the output directory or the same directory as the main file and named `$file_base_name.pdf`
- the LaTeX log will be written to the output directory or the same directory as the main file and named `$file_base_name.log`
- if you change the `PATH` in the environment (by using the `env` setting), you need to ensure that the `PATH` is still sane, e.g., that it contains the path for the TeX executables and other command line resources that may be necessary.

In addition, to ensure that forward and backward sync work, you need to ensure that the `-synctex=1` flag is set for your latex command. Again, don't forget the `-interaction=nonstopmode` flag (or whatever is needed for your tex programs not to expect user input in case of error).

Finally, please remember that script commands on Windows are run using `cmd.exe` which means that if your script uses any UNC paths will have to use `pushd` and `popd` to properly map and unmap a network drive.

## Sublime Build Files

LaTeXTools supports custom `.sublime-build` files or builders specified in project settings. For an overview of `.sublime-build` files in general, please refer to [Sublime Text build system documentation](https://www.sublimetext.com/docs/build_systems.html). For more on adding builders to project files, refer to [Sublime Text project file documentation](https://www.sublimetext.com/docs/projects.html). This section covers the basics of creating a `.sublime-build` file that works with LaTeXTools.

At a minimum, your `.sublime-build` file must have the following elements:

```json
{
	"target": "latextools_make_pdf",
	"selector": "text.tex.latex",

	"osx":
		{
			"file_regex": "^(...*?):([0-9]+): ([0-9]*)([^\\.]+)"
		},

	"windows":
		{
			"file_regex": "^((?:.:)?[^:\n\r]*):([0-9]+):?([0-9]+)?:? (.*)$"
		},

	"linux":
		{
			"file_regex": "^(...*?):([0-9]+): ([0-9]*)([^\\.]+)"
		}
}
```

Otherwise, other features may not work as expected. In addition, you can specify the following other parameters:

|Parameter|Description|
|-----------------|------------------------------------------------------------|
|`builder`|Overrides the `builder` setting. May refer to any valid LaTeXTools builder.|
|`program`|Overrides the `program` setting or `%!TEX program` macro. May be one of `pdflatex`, `xelatex`, or `lualatex`|
|`command`|Overrides the `command` setting, providing the command run by the builder. This is only useful if you use the `traditional` builder. For the format, see the relevant [Builder Setting](settings.md#builder-settings).|
|`env`|Overrides the `env` setting. Should be a dictionary similar to `env`, but note that when specified in a `.sublime-build` file, it is not, by default, platform-specific.|
|`path`|Overrides the `texpath` settings. Note that if you set this, you are responsible for ensuring that the appropriate LaTeX install can still be found.|
|`script_commands`|Overrides the `script_commands` setting used by the `script` builder. This is only useful if the `builder` is also changed to `script`.|


## Customizing the Build System

Since the release on March 13, 2014 ([v3.1.0](https://github.com/SublimeText/LaTeXTools/tree/v3.1.0)), LaTeXTools has had support for custom build systems, in addition to the default build system, called the "traditional" builder. Details on how to customize the traditional builder are documented above. If neither the traditional builder nor the script builder meet your needs you can also create a completely custom builder which should be able to support just about anything you can imagine. Let me know if you are interested in writing a custom builder!

Custom builders are small Python scripts that interact with the LaTeXTools build system. In order to write a basic builder it is a good idea to have some basic familiarity with the [Python language](https://www.python.org/). Python aims to be easy to understand, but to get started, you could refer either to the [Python tutorial](https://docs.python.org/3/tutorial/index.html) or any of the resources Python suggests for [non-programmers](https://wiki.python.org/moin/BeginnersGuide/NonProgrammers) or [those familiar with other programming languages](https://wiki.python.org/moin/BeginnersGuide/Programmers).

LaTeXTools comes packaged with a small sample builder to demonstrate the basics of the builder system, called [`SimpleBuilder`](https://github.com/SublimeText/LaTeXTools/blob/master/builders/simpleBuilder.py) which can be used as a reference for what builders can do.

If you are interested in developing your own builder, please see [our page on the wiki](https://github.com/SublimeText/LaTeXTools/wiki/Custom-Builders) with documentation and code samples!