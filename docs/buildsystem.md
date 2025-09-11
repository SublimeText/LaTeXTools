# Build System

LaTeXTools integrates into [Sublime Text build system](https://www.sublimetext.com/docs/build_systems.html).

The following build variants are provided to compile open TeX document to PDF and optionally partly override configuration:

| Variant                                       | Description
| --------------------------------------------- | -------------------------------------------------------------------------
| Compile to PDF                                | Use configured builder and compiler.
| Compile to PDF - Traditional Builder          | Use `traditional` builder with configured compiler.
| Compile to PDF - Traditional Builder with...  | Use `traditional` builder with displayed compiler.
| Compile to PDF - Basic Builder                | Use `basic` builder with configured compiler.
| Compile to PDF - Basic Builder with...        | Use `basic` builder with displayed compiler.
| Compile to PDF - Script Builder               | Use `script` builder with `script_commands` from [builder settings](settings.md#builder-settings).

## Configuration

Build system is configured by...

1. [builder settings](settings.md#builder-settings) in _LaTeXTools.sublime-settings_
2. [Project Specific Settings](settings.md#project-specific-settings) in _\*.sublime-project_
3. `%!TEX` directives in main TeX document
4. [Sublime Build Files](#sublime-build-files)

with given order of priority, later items overriding values from earlier ones.

At its core, `latextools_make_pdf` command implements a custom build `target` for [_\*.sublime-build_](#sublime-build-files) files, which provides infrastructure to run processes and display messages in build output panel. Actual workflows are implemented by [builder plugins](#builder-plugins). 

## Sublime Build Files

**Build Menu** items are defined by  _\*.sublime-build_ or [build_system](https://www.sublimetext.com/docs/projects.html#build-systems-key) key in _\*.sublime-project_ files.

For general information about Sublime Text's build system, please refer to:

- [Sublime Text build system documentation](https://www.sublimetext.com/docs/build_systems.html)
- [Sublime Text project file documentation](https://www.sublimetext.com/docs/projects.html)

At a minimum, a _\*.sublime-build_ for LaTeXTools must have the following elements for all features to work as expected:

```json
{
	"target": "latextools_make_pdf",
	"cancel": {"kill": true},
	"selector": "text.tex.latex",
	
	"linux": {
		"file_regex": "^(...*?):([0-9]+): ([0-9]*)([^\\.]+)"
	},

	"osx": {
		"file_regex": "^(...*?):([0-9]+): ([0-9]*)([^\\.]+)"
	},

	"windows": {
		"file_regex": "^((?:.:)?[^:\n\r]*):([0-9]+):?([0-9]+)?:? (.*)$"
	}
}
```

Parameter explanation:

| Parameter         | Description
| ------------------|------------------------------------------------------------
| `target`          | specifies the command to execute for building. LaTeXTools' build engine is provided by `latextools_make_pdf` command.  
| `cancel`          | required to be able to cancel a running build process at any point
| `selector`        | specifies for which scope (file type) the [build configuration](#configuration) is enabled for.
| `file_regex`      | used for navigation between build errors via <kbd>F4</kbd> and <kbd>shift+F4</kbd> keys.

LaTeXTools specific parameters:

| Parameter         | Description
| ------------------|------------------------------------------------------------
| `builder`         | Overrides the `builder` setting. May refer to any valid LaTeXTools builder.
| `program`         | Overrides the `program` setting or `%!TEX program` macro. May be one of `pdflatex`, `xelatex`, or `lualatex`
| `command`         | Overrides the `command` setting, providing the command line to run by the `traditional` builder. For the format, see the relevant [builder settings](settings.md#builder-settings).
| `options`         | Overrides the `options` setting, appending additional arguments to specified `command` of traditional builder. Especially useful to extend default command.
| `shell`           | specifies whether to run `command` (or any other command invoked by selected builder) in login shell. If `false`, the command is invoked directly.
| `env`             | Overrides the `env` setting. Must be a dictionary similar to `env`, but note that when specified in a `.sublime-build` file, it must be located in `osx` etc. to be platform-specific.
| `path`            | Overrides the `texpath` settings. Note that if you set this, you are responsible to ensure appropriate LaTeX install can still be found. This key overrides any `$PATH` setting in `env`.
| `script_commands` | Overrides the `script_commands` setting used by the `script` builder.

## Build Output Highlighting

If `"highlight_build_panel"` setting is set `True` build output is assigned a syntax definition. Color schemes can use assigned scopes to hihlight content of build output.

Primary scope being used is `message.[error|info|warning]` to align with default build outputs of ST.

| scope                                        | description
| -------------------------------------------- | ----------------------------
| `meta.messages message.info`                 | command `done` status
| `meta.messages message.warning`              | command `cancelled` status
| `meta.messages message.error`                | command `error` or `aborted` status
| `meta.logfile message.info`                  | logfile info messages
| `meta.logfile message.warning`               | logfile warnings
| `meta.logfile message.error`                 | logfile errors
| `meta.summary.sucess message.info.build`     | build `done` or `skipped` status
| `meta.summary.failure message.warning.build` | build `cancelled` status
| `meta.summary.failure message.error.build`   | build `failed` status

## Builder Plugins

A builder is a classic coroutine, yielding commands performing all required steps to build a PDF document from given TeX file.

Available default builders are:

- [Traditional Builder](#traditional-builder)
- [Basic Builder](#basic-builder)
- [Script Builder](#script-builder)

To learn, how to create custom builder plugins, refer to [Custom Builder](#custom-builder) section.

Breaking Changes of LaTeXTools v4.5.2:

1. All commands are executed with working directory set to `aux_directory`, which enables support for custom auxiliary directories in all builders and compilers, without the need to explicitly specify `--aux-directory` or `--output-directory` command line arguments.

2. Main TeX document's location is automatically prepended to `$TEXINPUTS`, `$BIBINPUTS` and `$BSTINPUTS`. Hence no special action is required for commands like `bibtex` or `bibtex8`, which don't support `--output-directory` arguments.

## Traditional Builder

The `traditional` builder is designed to work in most circumstances and for most setups. It supports all [builder features](features.md#default-builder) discussed elsewhere in the documentation, including multi-document support, the ability to set LaTeX flags via the [TeX Options](features.md#tex-options) settings, etc.

If available, [latexmk][] is used to generate the document. Otherwise [texify][] is used as fallback.

Default commands:

```
latexmk -f -%E -interaction=nonstopmode -synctex=1
```

**Note:** `-cd` argument is no longer required as of LaTeXTools v4.5.2

```
texify -b -p --engine=%E --tex-option="--synctex=1"
```

Supported settings:

- `command` - a string or list of strings, specifying the build command line to use.
- `program`	- the latex engine to use. Valid values are `pdflatex`, `xelatex`, or `lualatex`.
- `env` - a dictionary defining environment variables to be set for the environment the command is run in.
- `options` - a list of options to pass to pdf compiler.

**Example**

```json
{
	"builder_settings": {
		"command": "latexmk -cd -f -%E -interaction=nonstopmode -synctex=1",
		"program": "xelatex",
		"options": ["--shell-escape"],

		"osx": {
			"env": {
				"BIBINPUTS": "~/.local/tex:$BIBINPUTS"
			}
		}
	}
}
```

**Note:** The example displays the default latexmk build command for illustration purposes. If the default command is used, it doesn't need to be specified, explicitly.

**Note:** The placeholder `%E` is replaced by `-pdf`, `-xelatex`, etc. according to specified latex engine (e.g. via: `program`).

## Basic Builder

The `basic` builder is a simple, straight-forward build system, which simply runs the configured latex and bibliography compiler as needed. It supports [TeX Options](features.md#tex-options), [output and auxiliary directory](features.md#output-directory-and-auxiliary-directory) and [Jobname](features.md#jobname) feature, but not `makeindex` and friends. Its primary goal is to work around some shortcomings of [texify][] on platforms [latexmk][] is not available on.

**Note:** To use `basic` builder set `"builder": "basic"` in sublime-build file or any of the supported settings.

**Note:** Initial pdflatex call(s) may return with `error`, if required directories are to be created. Don't worry about it, that's normal behavior.

Supported settings:

- `bibtex` - the bibliography engine to use, if not explicitly requested by build process. Valid values are `biber`, `bibtex` or `bibtex8`.
- `env` - a dictionary defining environment variables to be set for the environment the command is run in.
- `program`	- the latex engine to use. Valid values are `pdflatex`, `xelatex`, or `lualatex`.
- `options` - a list of options to pass to pdf compiler.

## Script Builder

The `script` builder is an advanced feature to design custom compile workflows via settings.

Its primary goals are:

1. support customization of simple build workflows
2. enable LaTeXTools to integrate with external build systems in some fashion.

Unlike the "traditional" builder it is not designed to "just work," and is not recommend for those new to using TeX and friends. Please read this section carefully before using `script` builder.

Instead of invoking [texify][] or [latexmk][], a user-defined series of commands is executed. Note that although **multi-file documents** are supported, engine selection or passing other options via the `%!TEX` macros is not possible.

**Note:** To use `script` builder set `"builder": "script"` in sublime-build file or any of the supported settings.

Supported settings:

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

Each command can use [variables](#expandable-variables) which will be expanded before it is executed.

**Note:** If none of these variables occur in a command string, the `$file_base_name` will be appended. This may mean that a wrapper script is needed if, for example, using `make`

Commands are executed in the same path as `$file_path`, i.e. the folder containing the main document. Note, however, on Windows, since commands are launched using `cmd.exe`, you need to be careful if your root document is opened via a UNC path (this doesn't apply if you are simply using a mapped drive). `cmd.exe` doesn't support having the current working directory set to a UNC path and will change the path to `%SYSTEMROOT%`. In such a case, just ensure all the paths you specify are absolute paths and use `pushd` in place of `cd`, as this will create a (temporary) drive mapping.

### Output and Auxiliary Directories

If [auxiliary or output directory settings](settings.md#output-directory-settings) are specified, script builder creates them before batch execution. They are provided by [variables](#variables) for use in `script_commands`.

`pdflatex` and friends do not create (sub-)directories as needed. If `\include` is used (or anything attempts to `\@openout` a file in a subfolder), they must be created manually by script commands like  `"mkdir $output_directory\chapters"` (Windows) or `"mkdir -p $output_directory/chapters"` (Linux/MacOS).

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

## Custom Builder

A builder is a python class, extending `PdfBuilder`, to interact with LaTeXTools' build system. It implements a workflow by generating command line calls, required to compile a PDF document.

**Note:**: Any `PdfBuilder` subclass is automatically registered as soon as its owning module is loaded, or imported by a module, which is loaded, by Sublime Text.

**Note**: The builder name - to be used in settings - is the class name converted from PascalCase to snake_case with `Builder` suffix removed.

**Note**: Workflow is aborted if any executed command returns with non-zero exit status (by default).

### Tutorial

#### My First Builder

To create a custom builder:

1. Create a Sublime Text plugin in _Packages/User_ or any other _Packages/MyLaTeXPdfBuilder_ package.
2. Implement a builder class _(e.g.: `class MyFirstBuilder(PdfBuilder)`)_.
3. Activate the builder by setting _(e.g.: `"builder": "my_first"`)_.

**Note:** If plugin is created in any but _User_ package, ensure to also add a _.python-version_ file with `3.8` in it, to ensure it is loaded by plugin_host, which LaTeXTools runs on.

**Source**

```py
from LaTeXTools.plugins.builder.pdf_builder import PdfBuilder


class MyFirstBuilder(PdfBuilder):
    """
    A really simple builder implementation
    """
    
    name = "My First Builder"
    """
    Display name to use to refer to this builder in build output panel.
    """

    def commands(self):
        """
        A classic coroutine, generating commands to execute,
        receiving their exit status in return.
        """

        # yield is how commands are passed to build back-end.
        #
        # Each command is a tuple of 2 items:
        #
        #   1. command line to execute
        #
        #      can be a string, list of strings or `Popen` object
        #
        #   2. message to display when command is executed
        #
        #      It should describe the executed program and end with "..."
        #      to indicate progress. 
        #
        #      The back-end will append "done", "error", "cancelled" status, 
        #      after command execution finished.
        yield ("pdflatex", "running pdflatex...")
```

**LaTeXTools.sublime-settings**

```json
{
    "builder": "my_first"
}
```

**Build output**

```
[Compiling 'C:\path\to\tex\document.tex' using 'My First Builder']
running pdflatex...done

[Done!]
```

#### My Second Builder

The following code snippets illustrates basic possibilities to yield commands and customize workflow.

```py
from LaTeXTools.plugins.builder.pdf_builder import PdfBuilder


class MySecondBuilder(PdfBuilder):

    name = "My Second Builder"
    """
    Display name to use to refer to this builder in build output panel.
    """

    def __init__(self, *args):
        """
        Optionally initiate custom builder attributes.
        
        Note: It's recommended to do so at beginning of `commands()`, instead.
        """
        super().__init__(*args)
        self.sync_id = 1

    def commands(self):
        """
        A classic coroutine, generating commands to execute,
        receiving their exit status in return.
        """

        # display a message in the build output console
        self.display("Building something simple\n")

        # yield is how commands are passed to build back-end.
        #
        # Each command is a tuple of 2 items:
        #   1. command line to execute
        #   2. message to display when command is executed
        yield ("pdflatex", "running pdflatex...")
        
        # Commands with arguments are passed as list of strings.
        yield (["pdflatex", f"-synctex={self.sync_id}"], "running pdflatex...")

        # By default commands are executed with current working directory (`cwd`)
        # set to specified aux_directory if it differs from tex document's location.
        # To call commands with custom working directory or parameters,
        # use `PdfBuilder.command()` method.
        yield (self.command(["bibtex"], cwd="/my/custom/working/dir"), "running bibtex"...)

        # Prevent aborting workflow if command(s) return with non-zero exit status
        self.abort_on_error = False

        # Each `yield` statement returns the exit status of the executed command.
        status = yield ("pdflatex", "running pdflatex...")
        if status != 0:
            self.display("something went wrong, trying something else, instead")
            ...

        # To safely expand known variables in strings, use `self.expandvars()` method.
        my_template = "--path=$file_path"
        my_arg = self.expandvars(my_template)
        yield (["any-command", my_arg], "running any-command...")

```

#### Simple Builder

The [simple builder](https://github.com/SublimeText/LaTeXTools/blob/master/plugins/builder/simple_builder.py) demonstrates the most basic real world workflow to create a pdf document.

```py
from __future__ import annotations
import re

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pdf_builder import CommandGenerator

from .pdf_builder import PdfBuilder

__all__ = ["SimpleBuilder"]


class SimpleBuilder(PdfBuilder):
    """
    SimpleBuilder class

    Just call a bunch of commands in sequence to demonstrate basics
    """
    name = "Simple Builder"

    def commands(self) -> CommandGenerator:
        pdflatex = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-shell-escape",
            "-synctex=1",
        ]
        bibtex = ["bibtex"]

        # Regex to look for missing citations
        # This works for plain latex; apparently natbib requires special handling
        # TODO: does it work with biblatex?
        citations_rx = re.compile(r"Warning: Citation `.+' on page \d+ undefined")

        # We have commands in our PATH, and are in the same dir as the master file
        run = 1
        brun = 0
        yield (pdflatex + [self.base_name], f"pdflatex run {run}...")

        # Check for citations
        # Use search, not match: match looks at the beginning of the string
        # We need to run pdflatex twice after bibtex
        if citations_rx.search(self.out):
            brun += 1
            yield (bibtex + [self.base_name], f"bibtex run {brun}...")
            run += 1
            yield (pdflatex + [self.base_name], f"pdflatex run {run}...")
            run += 1
            yield (pdflatex + [self.base_name], f"pdflatex run {run}...")

        # Apparently natbib needs separate processing
        if "Package natbib Warning: There were undefined citations." in self.out:
            brun += 1
            yield (bibtex + [self.base_name], f"bibtex run {brun}...")
            run += 1
            yield (pdflatex + [self.base_name], f"pdflatex run {run}...")
            run += 1
            yield (pdflatex + [self.base_name], f"pdflatex run {run}...")

        # Check for changed labels
        # Do this at the end, so if there are also citations to resolve,
        # we may save one pdflatex run
        if "Rerun to get cross-references right." in self.out:
            run += 1
            yield (pdflatex + [self.base_name], f"pdflatex run {run}...")
```

### Reference

#### Expandable Variables

The `PdfBuilder` defines an `expandvars(template: str)` method, which can be called to expand following variables in strings.

| Variable            | Description
|---------------------|------------------------------------------------------------------------------------
| `$file`             | The full path to the main file, e.g., _C:\\Files\\document.tex_
| `$file_name`        | The name of the main file, e.g., _document.tex_
| `$file_ext`         | The extension portion of the main file, e.g., _tex_
| `$file_base_name`   | The name portion of the main file without the extension, e.g., _document_
| `$file_path`        | The directory of the main file, e.g., _C:\\Files_
| `$aux_directory`    | The auxiliary directory set via [build configuration](#configuration)
| `$output_directory` | The output directory set via [build configuration](#configuration)
| `$jobname`          | The jobname set via [build configuration](#configuration)
| `$eol`              | Will be replaced by empty string. Relevant to prevent automatic `$file_base_name` appending in [script builder](#script-builder).

#### PdfBuilder Variables

The `PdfBuilder` defines following attributes for direct use in builders' workflow code.

| Variable                   | Description
| -------------------------- | -----------------------------------------------------------
| self.tex_root              | the full path of the main tex document (e.g. C:\path\to\tex_root.tex)
| self.tex_dir               | the full path to the directory containing the main tex document (e.g. C:\path\to)
| self.tex_name              | the name of the main tex document (e.g. tex_root.tex)
| self.base_name             | the name of the main tex document without the extension (e.g. tex_root)
| self.tex_ext               | the extension of the main tex document (e.g. tex)
| self.engine                | the compiler engine from [build configuration](#configuration) (e.g. `pdflatex`, `xelatex`, ...)
| self.options               | additional compiler options from [build configuration](#configuration) (e.g.: `-shell-escape`)
| self.job_name              | the job name from [build configuration](#configuration)
| self.aux_directory         | path to auxiliary directory from [build configuration](#configuration), relative to `self.tex_dir`
| self.aux_directory_full    | absolute path to auxiliary directory
| self.output_directory      | path to output directory from [build configuration](#configuration), relative to `self.tex_dir`
| self.output_directory_full | absolute path to output directory
| self.tex_directives        | dictionary of `%!TEX` directives from root document
| self.builder_settings      | dictionary representing [builder settings](settings.md#builder-settings)
| self.platform_settings     | dictionary representing [platform specific settings](settings.md#platform-specific-settings)
| self.abort_on_error        | specifies whether to abort build on non-zero exit status of executed command. (default: `True`)
| self.run_in_shell          | specifies whether to run commands in login shell. Value depends on build system configuration. (default: `False`)
| self.out                   | the output from most recently run command.

---

[latexmk]: https://www.ctan.org/pkg/latexmk/
[texify]: https://docs.miktex.org/manual/texifying.html
