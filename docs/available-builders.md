# Available Builders

## Traditional Builder

By default, LaTeXTools uses the `traditional` builder, which is designed to work in most circumstances and for most setups. This builder provides all of the builder features discussed elsewhere in the documentation, such as the various [builder features](features.md#default-builder), including multi-document support, the ability to set LaTeX flags via the `TeX Options` settings, etc.

When you are using MiKTeX, the `traditional` builder defaults to using the MiKTeX compiler driver [`texify`](http://docs.miktex.org/manual/texifying.html), which automatically runs PDFLaTeX / XeLaTeX / LuaLaTeX as many times as necessary to generate a document. Note that because of certain limitations of `texify`, some features, such as support for output directory, auxiliary directory, jobname, etc. are unavailable when using the traditional builder. You can change this by installing `latexmk` and changing the `command` setting in the `builder_settings` block to `"latexmk -cd -f -%E -interaction=nonstopmode -synctex=1"`, in which case the `traditional` builder will run `latexmk` instead of `texify`

When you are using any other setup (MacTeX or TeXLive on Linux or Windows), the `traditional` builder uses [`latexmk`](http://www.ctan.org/pkg/latexmk/), which supports all the documentated features for the builder.

## Basic Builder

The basic builder is a simple, straight-forward build system. that simply runs the configured build engine (pdflatex, xelatex, or lualatex) and bibtex or biber if necessary. It can also be configured to support bibtex8 through the `bibtex` builder setting. In addition, it supports the [TeX Options](features.md#tex-options) feature, the [output and auxiliary directory](features.md#output-directory-and-auxiliary-directory) features and the [Jobname](features.md#jobname) feature. It has been included because the default builder on MiKTeX, `texify` cannot be easily coerced to support biber or any of the other features supported by the basic builder. Note, however, that unlike `texify`, the basic builder does **not** support `makeindex` and friends (patches are welcome!).

You can use the basic builder by changing the `builder` setting to `"basic"`. It will read the same settings as the traditional builder.

## Script Builder

LaTeXTools now supports the long-awaited script builder. It has two primary goals: first, to support customization of simple build workflows and second, to enable LaTeXTools to integrate with external build systems in some fashion.

Note that the script builder should be considered an advanced feature. Unlike the "traditional" builder it is not designed to "just work," and is not recommend for those new to using TeX and friends. You are responsible for making sure your setup works. Please read this section carefully before using the script builder.

For the most part, the script builder works as described in the [Compiling LaTeX files](#compiling-latex-files) section *except that* instead of invoking either `texify` or `latexmk`, it invokes a user-defined series of commands. Note that although the Script Builder supports **Multi-file documents**, it does not support either the engine selection or passing other options via the `%!TEX` macros.

The script builder is controlled through two settings in the *platform-specific* part of the `builder_settings` section of `LaTeXTools.sublime-settings`, or of the current project file (if any):

- `script_commands` — the command or list of commands to run. This setting **must** have a value or you will get an error message.
- `env` — a dictionary defining any environment variables to be set for the environment the command is run in.

The `script_commands` setting should be either a string or a list. If it is a string, it represents a single command to be executed. If it is a list, it should be either a list of strings representing single commands or a list of lists, though the two may be mixed. For example:

```json
{
	"builder_settings": {
		"osx": {
			"script_commands":
				"pdflatex -synctex=1 -interaction=nonstopmode"
		}
	}
}
```

Will simply run `pdflatex` against the master document, as will:

```json
{
	"builder_settings": {
		"osx": {
			"script_commands":
				["pdflatex -synctex=1 -interaction=nonstopmode"]
		}
	}
}
```

Or:

```json
{
	"builder_settings": {
		"osx": {
			"script_commands": 
				[["pdflatex", "-synctex=1 -interaction=nonstopmode"]]
		}
	}
}
```

More interestingly, the main list can be used to supply a series of commands. For example, to use the simple pdflatex -> bibtex -> pdflatex -> pdflatex series, you can use the following settings:

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

Note, however, that the script builder is quite unintelligent in handling such cases. It will not note any failures nor only execute the rest of the sequence if required. It will simply continue to execute commands until it hits the end of the chain of commands. This means, in the above example, it will run `bibtex` regardless of whether there are any citations.

It is especially important to ensure that, in case of errors, TeX and friends do not stop for user input. For example, if you use `pdflatex` on either TeXLive or MikTeX, pass the `-interaction=nonstopmode` option. 

Each command can use the following variables which will be expanded before it is executed:

|Variable|Description|
|-----------------|------------------------------------------------------------|
|`$file`   | The full path to the main file, e.g., _C:\\Files\\document.tex_|
|`$file_name`| The name of the main file, e.g., _document.tex_|
|`$file_ext`| The extension portion of the main file, e.g., _tex_|
|`$file_base_name`| The name portion of the main file without the extension, e.g., _document_|
|`$file_path`| The directory of the main file, e.g., _C:\\Files_|
|`$aux_directory`| The auxiliary directory set via a `%!TEX` directive or the settings|
|`$output_directory`| The output directory set via a `%!TEX` directive or the settings|
|`$jobname`| The jobname set via a `%!TEX` directive or the settings|

For example:

```json
{
	"builder_settings": {
		"osx": {
			"script_commands": [[
				"pdflatex", 
				"-synctex=1"
				"-interaction=nonstopmode",
				"$file_base_name"
			]]
		}
	}
}
```

Note that if none of these variables occur in the command string, the `$file_base_name` will be appended to the end of the command. This may mean that a wrapper script is needed if, for example, using `make`.

Commands are executed in the same path as `$file_path`, i.e. the folder containing the main document. Note, however, on Windows, since commands are launched using `cmd.exe`, you need to be careful if your root document is opened via a UNC path (this doesn't apply if you are simply using a mapped drive). `cmd.exe` doesn't support having the current working directory set to a UNC path and will change the path to `%SYSTEMROOT%`. In such a case, just ensure all the paths you specify are absolute paths and use `pushd` in place of `cd`, as this will create a (temporary) drive mapping.

### Supporting output and auxiliary directories

If you are using LaTeXTools output and auxiliary directory behavior there are some caveats to be aware of. First, it is, of course, your responsibility to ensure that the approrpiate variables are passed to the appropriate commands in your script. Second, `pdflatex` and friends do not create output directories as needed. Therefore, at the very least, your script must start with either `"mkdir $output_directory"` (Windows) or `"mkdir -p $output_directory"` and a corresponding command if using a separate `$aux_directory`. Note that if you `\include` (or otherwise attempt anything that will `\@openout` a file in a subfolder), you will need to ensure the subfolder exists. Otherwise, your run of `pdflatex` will fail.

Finally, unlike Biber, bibtex (and bibtex8) does not support an output directory parameter, which can make it difficult to use if you are using the LaTeXTools output directory behavior. The following work-arounds can be used to get BibTeX to do the right thing.

On Windows, run BibTeX like so:

```
cd $aux_directory & set BIBINPUTS=\"$file_path:%BIBINPUTS%\" & bibtex $file_base_name
```

And on OS X or Linux, use this:

```
"cd $output_directory; BIBINPUTS=\"$file_path;$BIBINPUTS\" bibtex $file_base_name"
```

In either case, these run bibtex *inside* the output / auxiliary directory while making the directory containing your main file available to the `BIBINPUTS` environment variable. Note if you use a custom style file in the same directory, you will need to apply a similar work-around for the `BSTINPUTS` environment variable.

### Supporting jobname

If you are using LaTeXTools jobname behaviour, you should be aware that you are responsible for ensure jobname is set in the appropriate context. In particular, a standard build cycle might look something like this:

```json
"builder_settings": {
	"osx": {
		"script_commands": [
			"pdflatex -synctex=1 -interaction=nonstopmode -jobname=$jobname $file_base_name",
			"bibtex $jobname",
			"pdflatex -synctex=1 -interaction=nonstopmode -jobname=$jobname $file_base_name",
			"pdflatex -synctex=1 -interaction=nonstopmode -jobname=$jobname $file_base_name"
		]
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

LaTeXTools now has some support for custom `.sublime-build` files or builders specified in your project settings. For an overview of `.sublime-build` files in general, please see [the Unofficial Documentation](http://sublime-text-unofficial-documentation.readthedocs.io/en/latest/reference/build_systems.html) (which is generally a great resource about Sublime Text). For more on adding builders to project files, see [the relevant section of the Sublime documentation](https://www.sublimetext.com/docs/3/projects.html). This section will cover the basics of creating a `.sublime-build` file that works with LaTeXTools.

At a minimum, your `.sublime-build` file must have the following elements:

```json
{
	"target": "make_pdf",
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