# Completions

## Command completion, snippets, etc.

By default, ST provides a number of snippets for LaTeX editing; the LaTeXTools plugin adds a few more. You can see what they are, and experiment, by selecting **Tools | Snippets | LaTeX** and **Tools | Snippets | LaTeXTools** from the menu.

In addition, the LaTeXTools plugin provides useful completions for both regular and math text; check out files [`LaTeX.sublime-completions`](https://github.com/SublimeText/LaTeXTools/blob/master/LaTeX.sublime-completions) and [`LaTeX math.sublime-completions`](https://github.com/SublimeText/LaTeXTools/blob/master/LaTeX%20math.sublime-completions) in the LaTeXTools directory for details. Some of these are semi-intelligent: i.e. `bf` expands to `\textbf{}` if you are typing text, and to `\mathbf{}` if you are in math mode. Others allow you to cycle among different completions: e.g. `f` in math mode expands to `\phi` first, but if you hit Tab again you get `\varphi`; if you hit Tab a third time, you get back `\phi`.

## CWL support

LaTeXTools ships [TeXStudio Completion Word Lists][] to support command completions.

Additional user defined CWL files can be placed in  `Packages/User/cwl` directory.

By default, as soon as one starts typing a command, e.g., `\te`, a popup is shown displaying possible completions, e.g. including `\textit` and the like.

The following settings are provided to control LaTeXTools cwl behavior.

* `cwl_list`: a list of `cwl` files to load
* `cwl_autoload`: controls loading completions based on packages in the current document *in addition* to those specified in the `cwl_list`. Defaults to `true`, so you only need to set this if you want to *disable* this behavior.
* `command_completion`: when to show that cwl completion popup. The possible values are:
	* `prefixed` (default): show completions only if the current word is prefixed with a `\`
	* `always`: always show cwl completions
	* `never`: never display the popup
* `env_auto_trigger`: if `true`, autocomplete environment names upon typing `\begin{` or `\end{` (default: `false`)

## User defined completions

LaTeXTools provides support for custom user-defined completions through modification of the `LaTeX.sublime-completions` file. The user modified version should be placed in your `User` directory, otherwise it will be overwritten by future updates.

[TeXStudio Completion Word Lists]: https://htmlpreview.github.io/?https://github.com/texstudio-org/texstudio/master/utilities/manual/usermanual_en.html#description-of-the-cwl-format