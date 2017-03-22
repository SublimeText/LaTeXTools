# Keybindings

Keybindings have been chosen to make them easier to remember, and also to minimize clashes with existing (and standard) ST bindings. We take advantage of the fact that ST supports key combinations, i.e. sequences of two (or more) keys. The basic principle is simple:

* **Most** LaTeXTools facilities are triggered using <kbd>Ctrl+l</kbd> (Windows, Linux) or <kbd>⌘+l</kbd> (OS X), followed by some other key or key combination

* **Compilation** uses the standard ST "build" keybinding, i.e. <kbd>Ctrl+b</kbd> on Windows and Linux and <kbd>⌘</kbd>+<kbd>b</kbd> on OS X. So does the **GoTo Anything** facility.

For example, to jump to the point in the PDF file corresponding to the current cursor position, use <kbd>Ctrl+l</kbd>, <kbd>j</kbd>: that is, hit <kbd>Ctrl+l</kbd>, then release both the <kbd>Ctrl</kbd> and the <kbd>l</kbd> keys, and quickly type the <kbd>j</kbd> key (OS X users: replace <kbd>Ctrl</kbd> with <kbd>⌘</kbd>). To wrap the selected text in an `\emph{}` command, use <kbd>Ctrl+l</kbd>, <kbd>Ctrl+e</kbd>: that is, hit <kbd>Ctrl+l</kbd>, release both keys, then hit <kbd>Ctrl+e</kbd> (OS X users hit <kbd>⌘+l</kbd> and then <kbd>⌘+e</kbd>). 

<kbd>Ctrl+l</kbd> (<kbd>⌘+l</kbd> on OS X) is the standard ST keybinding for **Expand selection to line**; for LaTeX documents when LaTeXTools is active, this is **remapped** to <kbd>Ctrl+l</kbd>,<kbd>Ctrl+l</kbd> (<kbd>⌘+l</kbd>,<kbd>⌘+l</kbd> on OS X). This is the *only* standard ST keybinding that is affected by the plugin---an advantage of new-style keybindings.

Most plugin facilities are invoked using sequences of 2 keys or key combinations, as in the examples just given. A few use sequences of 3 keys or key combinations.

Henceforth, I will write <kbd>C+</kbd> to mean <kbd>Ctrl+</kbd> for Linux or Windows, and <kbd>⌘+</kbd> for OS X. You know your platform, so you know what you should use. In a few places, to avoid ambiguities, I will spell out which key I mean.

## Compiling LaTeX files

**Keybinding:** <kbd>C+b</kbd> (standard ST keybinding)

LaTeXTools offers a fully customizable build process. This section describes the default process, also called "traditional" because it is the same (with minor tweaks) as the one used in previous releases. However, see the section on [builder features](features.md#builder-features) for how to customize the build process.

The default ST Build command takes care of the following:

* It saves the current file
* It invokes the tex build command (`texify` for MikTeX; `latexmk` for TeXlive and MacTeX).
* It parses the tex log file and lists all errors, warnings and, if enabled, bad boxes in an output panel at the bottom of the ST window: click on any error/warning/bad boxes to jump to the corresponding line in the text, or use the ST-standard Next Error/Previous Error commands.
* It invokes the PDF viewer for your platform and performs a forward search; that is, it displays the PDF page where the text corresponding to the current cursor position is located.

## Selecting Build Variant

**Keybinding:** <kbd>C+shift+b</kbd> (standard ST3 keybinding)

LaTeXTools offers a range of build variants to select standard build options. These variants can be used to customize the options passed to the LaTeXTools builder, so that you don't need a project file or to use any of the `%!TEX` directives to change, e.g., the build system used. Variants are provided for the supported builders and for the supported programs.

In addition, custom Sublime build files can be created to add your own variants to standard LaTeXTools commands. For more on this, see the section on [Sublime Build Files](available-builders.md#sublime-build-files).

**Note**: The settings provided by build variants *override* settings specified using TeX directives or in your settings. This means, for example, if you select a build variant that changes the program, `%!TEX program` directives or `program` settings will be ignored. If you want to return LaTeXTools back to its default behavior, please select the **LaTeX** build variant.

## Toggling window focus following a build

**Keybinding:** <kbd>C+l</kbd>,<kbd>t</kbd>,<kbd>f</kbd>

By default, after compilation, the focus stays on the ST window. This is convenient if you like to work with the editor and PDF viewer window open side by side, and just glance at the PDF output to make sure that all is OK. If however the editor and viewer windows overlap (e.g. if you have a small screen), you may prefer the viewer window to get the focus (i.e. become the foremost window) after compiling. To this end, you can use the `toggle_focus` command to change this behavior. The first time you invoke this command, the focus will shift to the viewer window after compiling the current file; if you invoke the command again, the post-compilation focus reverts to the editor window. Every time you invoke `toggle_focus`, a message will appear in the status bar.

You can change the default focus behavior via the `keep_focus` option: see the "Settings" section below.

## Toggling PDF syncing (forward search) following a build

**Keybinding:** <kbd>C+l</kbd>,<kbd>t</kbd>,<kbd>s</kbd>

By default, after compilation, LaTeXTools performs a 'forward search' so that the PDF viewer shows the point in the PDF file corresponding to the current cursor position in ST (by the way, you can trigger a forward search at any other time, not just when you are compiling: see below). If for whatever reason you don't like this behavior, you can turn it off using the `toggle_fwdsync` command. As for `toggle_focus`, a message will appear in the status bar to reflect this.

You can also change the default sync behavior via the `forward_sync` option: see the "Settings" section below.

## Checking the status of toggles and defaults

**Keybinding:** <kbd>C+l</kbd>,<kbd>t</kbd>,<kbd>?</kbd>

This opens a quick panel displaying the current toggle values and their corresponding default settings. Selecting an entry in the quick panel will toggle the value (turning the feature on or off).

## Show the build panel

**Keybinding:** <kbd>shift+escape</kbd>

This will show the LaTeXTools build panel, including any messages from the previous build. This is useful if you have hidden the build panel, either using the `hide_build_panel` setting or by pressing <kbd>escape</kbd> when the panel is visible.

## Removing temporary files from build

**Keybinding:** <kbd>C+l</kbd>,<kbd>backspace</kbd>

This deletes all temporary files from a previous build (the PDF file is kept). Subfolders are traversed recursively. This command also clears the [LaTeXTools cache](features.md#latextools-cache).

Two settings allow you to fine-tune the behavior of this command. `temp_files_exts` allows you to specify which file extensions should be considered temporary, and hence deleted. `temp_files_ignored_folders` allows you to specify folders that should not be traversed. A good example are `.git` folders, for people who use git for version control.

**Note**: If you use any of the special values with the output directory or auxiliary directory feature, the above is ignored, and the entire directory is simply deleted. If you are using the auxiliary directory feature *without* using an output directory, the auxiliary directory will be cleared and the normal process will be run.

## Clearing the cache

**Keybinding:** <kbd>C+l</kbd>,<kbd>C+d</kbd>,<kbd>C+c</kbd>

This clears the [LaTeXTools cache](features.md#latextools-cache). It is useful if the LaTeXTools cache information gets too out of date, but you want to maintain the LaTeX build files, such as `.aux`.

## Forward Search and Inverse Search

**Keybinding:** <kbd>C+l</kbd>,<kbd>j</kbd> (forward search)

When working in an ST view on a TeX document, <kbd>C+l</kbd>,<kbd>j</kbd> will display the PDF page where the text corresponding to the current cursor position is located; this is called a "forward search". The focus is controlled by the <kbd>C+l</kbd>,<kbd>t</kbd>,<kbd>f</kbd> toggle setting and the `keep_focus` option.

### Inverse Search

Inverse search (i.e., going from the PDF file back to the TeX document in ST) depends on the viewer you are using. Assuming you have properly configured your viewer, the default inverse search shortcuts are:

 * <kbd>⌘+shift+click</kbd> on a location in **Skim.app** (OS X)
 * Double-click in **Sumatra PDF** (Windows)
 * <kbd>Ctrl+left-click</kbd> in **Evince** (Linux)
 * <kbd>Shift+left-click</kbd> in **Okular** (Linux)
 * <kbd>Ctrl+left-click</kbd> in **Zathura** (Linux)


This will bring you to the corresponding location in the source text document.

### Other PDF Viewers

Not all PDF viewers have support for forward or inverse search. In those cases, using the forward search command <kbd>C+l</kbd>,<kbd>j</kbd> is equivalent to running the [View PDF](#view-pdf) command.

## View PDF

** Keybinding:** <kbd>C+l</kbd>,<kbd>v</kbd>

This will open the PDF document corresponding to the current TeX file in your configured viewer. Note that opening the PDF using this does *not* do a forward search.

## References and Citations

**Keybinding:** *autotriggered* by default (see below). Otherwise, <kbd>C+l</kbd>,<kbd>x</kbd> for 'cross-reference,' <kbd>C+l</kbd>,<kbd>C+f</kbd>, or <kbd>C+l</kbd>,<kbd>C+Alt+f</kbd> (via the [Fill Helper facility](#fill-helper); see below). These are fully equivalent ways of invoking ref/cite completions.

The basic idea is to help you insert labels in `\ref{}` commands and bibtex keys in `\cite{}` commands. The appropriate key combination shows a list of available labels or keys, and you can easily select the appropriate one. Full filtering facilities are provided. 

**Notes**: 

1. In order to find all applicable labels and bibtex keys, the plugin looks at the **saved** file. So, if you invoke this command and do not see the label or key you just entered, perhaps you haven't saved the file.

2. Only bibliographies in external `.bib` files are supported: no `\bibitem...`. Sorry. It's hard as it is. 

3. Multi-file documents are fully supported.

Now for the details. (Many of these features were contributed by Wes Campaigne and jlewegie, whom I thank profusely.)

By default, as soon as you type, for example, `\ref{` or `\cite{`, a quick panel is shown (this is the fancy drop-down list ST displays at the top of the screen), listing, respectively, all the labels in your files, or all the entries in the bibliographies you reference in your file(s) using either the `\bibliography{}` command or one of biblatex equivalents such as `\addbibresource{}`. This is the default *auto-trigger* behavior, and it can be a big time saver. You can, however, turn it off, either temporarily using a toggle, or permanently by way of preference settings; see below. Once the quick panel is shown, you can narrow down the entries shown by typing a few characters. As with any ST quick panel, what you type will be fuzzy-matched against the label names or, for citations, the content of the first displayed line in each entry (by default, the author names, year of publication, short title and citation key; see below). This is *wildly* convenient, and one of the best ST features: try it!

If auto-triggering is off, when you type e.g. `\ref{`, ST helpfully provides the closing brace, leaving your cursor between the two braces. Now, you need to type `C-l,x` to get the quick panel  showing all labels in the current file. You can also type e.g. `\ref{aa` [again, the closing brace is provided by ST], then `C-l, x`, and LaTeXTools will show a list of labels that fuzzy-match the string `aa`. In either case, you then select the label you want, hit `return`, and LaTeXTools inserts the **full ref command**, as in `\ref{my-label}`. Citations for `bib` files are supported in a similar way.

One often needs to enter **multiple citations**, as e.g. in `\cite{paper1,paper2}`. This is easy to do: either cite the first paper, e.g. `\cite{paper1}` and then, *with your cursor immediately before the right brace*, type a comma (`,`). Again, the default auto-trigger behavior is that the quick panel with appear, and you can select the second paper. If auto-trigger is off, then you enter the comma, then use the shortcut <kbd>C+l</kbd>,<kbd>x</kbd> to bring up the quick panel (note: you *must* add the comma before invoking the shortcut, or you won't get the intended result). Of course, you can enter as many citations as you want.

LaTeXTools currently provides support for a range of referencing facilities, including those provided by the **cleveref**, **fancyref**, and **varioref** packages in addition to the standard, built-in reference commands. However, if you are using a reference command that LaTeXTools doesn't recognize, you can use the key combination <kbd>C+l</kbd>,<kbd>Alt+x</kbd>,<kbd>r</kbd> to display the quick-panel and insert a label anywhere.

Similarly, LaTeXTools provides support for a range of bibliography referencing programs, including **biblatex** and **natbib** in addition to the default `\cite{}` command. Similarly to references, if you come across a command that requires a citation and LaTeXTools doesn't currently support it, you can use the key combination <kbd>C+l</kbd>,<kbd>Alt+x</kbd>,<kbd>c</kbd> to display the quick-panel of all ciations and insert the bibkey.

The display of bibliographic entries is *customizable*. There is a setting, `cite-panel-format`, that controls exactly what to display in each of the two lines each entry gets in the citation quick panel. Options include author, title, short title, year, bibtex key, and journal. This is useful because people may prefer to use different strategies to refer to papers---author-year, short title-year, bibtex key (!), etc. Since only the first line in each quick panel entry is searchable, how you present the information matters. The default should be useful for most people; if you wish to change the format, check the `LaTeXTools.sublime-settings` file for detailed information. (As usual, copy that file to the `User` directory and edit your copy, not the original).

Thanks to recent contributed code, **multi-file documents** are *fully supported*. LaTeXTools looks for labels, as well as `\bibliography{}` commands, in the root file and in all recursively included files. Please see the information on [**Multi-file documents**](features.md#multi-file-documents) in the section on [**General Features**](features.md#general-features) for details on how to setup multi-file documents.

### Old-style, deprecated functionality

**For now**, completions are also injected into the standard ST autocompletion system. Thus, if you hit <kbd>Ctrl+space</kbd> (Windows or OS X) or <kbd>Alt+/</kbd> (Linux) immediately after typing, e.g., `\ref{`, you get a drop-down menu at the current cursor position (not a quick-panel) showing all labels in your document. However, the width of this menu is OK for (most) labels, but not really for paper titles. In other words, it is workable for references, but not really for citations. Furthermore, there are other limitations dictated by the ST autocompletion system. So, this is **deprecated**, and I encourage you to use auto-trigger mode or the <kbd>C+l</kbd>,<kbd>x</kbd> or <kbd>C+l</kbd>,<kbd>C+f</kbd> keybindings instead.

## Forcing Citations and References

**Keybinding**: <kbd>C+l</kbd>,<kbd>Alt+x</kbd>,<kbd>c</kbd> (citations) or <kbd>C+l</kbd>,<kbd>Alt+x</kbd>,<kbd>r</kbd> (refs)

In some cases, it may be desirable to forcibly insert a citation key or label, i.e., if LaTeXTools does not automatically understand the command you are using. In such circumstances, you can use these keybindings to forcibly insert either a citation or reference at the cursor position. Note that the current word won't be overridden and any open brackets will not be completed if either of these options are used.

## Fill Helper

**Keybinding:** *autotriggered* by default (see below). Otherwise, <kbd>C+l</kbd>,<kbd>C+f</kbd> or <kbd>C+l</kbd>,<kbd>C+Alt+f</kbd> (see below).

Thanks to the amazing work by users btstream and Ian Bacher, LaTeXTools now offers a list of available files and packages when using commands such as `\usepackage`, `\include`, `\includegraphics`, `\includesvg` and `\input`. Assuming autocompletion is toggled on (the default):

 * when you type `\usepackage{`, a list of available package is displayed in the ST drop-down menu. Pick the one you need, and it will be inserted in your file, with a closing brace.

 * when you type any of the file-related input commands, a list of files in the current directory is displayed (suitably filtered, so graphics files are displayed for `\includegraphics`).

To toggle autocompletion on or off, use the `fill_auto_trigger` setting, or the `C-l,t,a,f` toggle.

In order for package autocomplete to work, you need to create a cache first. You can do it using the Command Palette: select `LaTeXTools: Build cache for LaTeX packages`.

The `C-l,C-f` keyboard shortcut also works for `\ref` and `\cite` completion. Basically, wherever you can use `C-l,x`, you can also use `C-l,C-f`. 

The `C-l,C-alt-f` keyboard shortcut is identical to the `C-l,C-f` shortcut, except that it ensures that the current word that the cursor is within is replaced. This is useful for, e.g., switching one citation for another or one label for another.

## Toggle auto trigger mode on/off

**Keybinding:** <kbd>C+l</kbd>,<kbd>t</kbd>,<kbd>a</kbd>,<kbd>r</kbd> (references); <kbd>C+l</kbd>,<kbd>t</kbd>,<kbd>a</kbd>,<kbd>c</kbd> (citations); <kbd>C+l</kbd>,<kbd>t</kbd>,<kbd>a</kbd>,<kbd>f</kbd> (input files); <kbd>C+l</kbd>,<kbd>t</kbd>,<kbd>a</kbd>,<kbd>e</kbd> (environments); <kbd>C+l</kbd>,<kbd>t</kbd>,<kbd>a</kbd>,<kbd>b</kbd> (smart brackets)

These toggles work just like the sync and focus toggles, but control whether or not the auto-trigger behavior is enabled for different types of auto-triggers. <kbd>C+l</kbd>,<kbd>t</kbd>,<kbd>?</kbd> will also displays the status of the auto trigger toggles.

## Jumping to sections and labels

**Keybinding:** <kbd>C+r</kbd> or <kbd>C+shift+r</kbd> (standard ST keybinding) or <kbd>C+l</kbd>,<kbd>C+r</kbd> or <kbd>C+l</kbd>,<kbd>C+shift+r</kbd> (LaTeXTools only)

This will display a list of all section headings and (if you so desire) labels in the current LaTeX document. You can filter the list of sections / labels by typing some of the characters in the heading name.

Selecting any entry in the list will take you to the corresponding place in the text. On ST3 only, highlighting a specific item (using the arrow keys) will temporarily open the corresponding location.

You can disable this and use the default overlay by settings `overwrite_goto_overlay` to `false` in your LaTeXTools settings.

## Jump to Anywhere

**Keybinding:** <kbd>C+l</kbd>,<kbd>C+j</kbd> or <kbd>C+l</kbd>,<kbd>C+o</kbd> (see [below](#jumping-to-included-files))

**Mousebinding:** <kbd>Ctrl+Alt+left-click</kbd> (Windows) / <kbd>Super+left-click</kbd> (Linux) / <kbd>⌘+Ctrl+click</kbd> (OSX)

**Mousebinding (With SublimeCodeIntel):** <kbd>Alt+left-click</kbd> (Windows) / <kbd>Super+left-click</kbd> (Linux) / <kbd>Ctrl+click</kbd> (OSX)

This is an IDE-like mouse navigation, which executes a jump depending on the context around the cursor. It is easy to use and intuitive. Just click with the mouse on a command while pressing the modifier key. The corresponding jump will be executed. Supported jump types are:

- Jump to referenced labels (e.g. `\ref`)
- Show and jump to label usages (e.g. `\label`)
- Jump to citation entries in bibliography files (e.g. `\cite`)
- Jump to glossary entries (e.g. `\gls`)
- Open included files (e.g. `\input` or `\include`)
- Open root file from `%!TEX root =...` magic comment
- Open bibliographies (e.g. `\bibliography` or `\addbibresource`)
- Open included graphics with a specified program (e.g. `\includegraphics`)
- Open the documentation of used packages (e.g. `\usepackage`)
- Jump to self-defined command definition, i.e. jump to the `\newcommand` in which the command was defined

### SublimeCodeIntel Integration
If you use [SublimeCodeIntel](https://github.com/SublimeCodeIntel/SublimeCodeIntel) you will recognize the alternative mouse-bindings; however, these are not activated out of the box. To use them, open the command palette and run the command `LaTeXTools: Create Mousemap in User folder`. This will create a mouse-map in the user folder or modify the existing one to add the mouse-binding with the same modifiers as SublimeCodeIntel. These mouse-bindings have a `fallback_command` command argument, which is the command that will be executed if the command in called outside a LaTeX document.

### Jumping to included files
To open a file included using, e.g., `\input` or `\include` or a bibliography, simply click while holding down the modifier key or press `C-l, C-j`. Sublime will open the included file.

Additionally, the keybinding <kbd>C+l</kbd><kbd>C+o</kbd> is provided, that, if the file already exists, behaves just like <kbd>C+l</kbd>,<kbd>C+j</kbd>. However, if the file does *not* exist, it will also create the missing file and, if a `tex` file, will add the magic root comment (`%!TEX root=`) to the new file. This can be used to easily create files or to open already existing files.

### Image files
To open an image, which is included with `\includegraphics` just click on the command while pressing the modifier key or press  <kbd>C+l</kbd>,<kbd>C+j</kbd>.

The program to open the image can be configured in the LaTeXTools settings in the `open_image_command` setting.

The following sub-settings are provided:

- `image_types`: a list of the image file types used in the `\includegraphics` command. This list is also used in the Fill Helper and to determine missing extensions to open images. When opening an image the `image_types`-list will be matched from left to right.
- `open_image_command`: the command/program to open an image used in the `\includegraphics` command. This commands can be configured OS-specific. For each OS you can create a list, which will be searched top-down for the matching extension. Each entry in the list has a `command` and `extension` field. The command is a string and will be executed with the file path appended, if the extension matches the extension of the file. You can optionally use `$file` inside the string to insert the file path at an arbitrary position. The `extension` can either be a string or a list of string. If it is missing, the command will be executed for every file type.

### Packages
If you use the command while the cursor is inside a `\usepackage` command, the documentation for the corresponding package will be opened in your default PDF viewer using the `texdoc` command.

## LaTeX commands and environments

**Keybindings:**  <kbd>C+l</kbd>,<kbd>c</kbd> (commands) and <kbd>C+l</kbd>,<kbd>e</kbd> (environments)

To insert a LaTeX command such as `\color{}` or similar, type the command without backslash (i.e. `color`), then hit <kbd>C+l</kbd>,<kbd>c</kbd>. This will replace e.g. `color` with `\color{}` and place the cursor between the braces. Type the argument of the command, then hit Tab to exit the braces.

Similarly, typing <kbd>C+l</kbd>,<kbd>e</kbd> gives you an environment: e.g. `test` becomes

	\begin{test}

	\end{test}

and the cursor is placed inside the environment thus created. Again, Tab exits the environment. 

Note that all these commands are undoable: thus, if e.g. you accidentally hit <kbd>C+l</kbd>,<kbd>c</kbd> but you really meant <kbd>C+l</kbd>,<kbd>e</kbd>, a quick <kbd>C+z</kbd> (undo), followed by <kbd>C+l</kbd>,<kbd>e</kbd>, will fix things.

## Wrapping existing text in commands and environments

**Keybindings:** <kbd>C+l</kbd>,<kbd>C+c</kbd>; <kbd>C+l</kbd>,<kbd>C+e</kbd>; <kbd>C+l</kbd>,<kbd>C+b</kbd>; <kbd>C+l</kbd>,<kbd>C+u</kbd>; <kbd>C+l</kbd>,<kbd>C+t</kbd>; <kbd>C+l</kbd>,<kbd>C+n</kbd>; <kbd>C+l</kbd>,<kbd>C+Shift+n</kbd> (see description)

Sometimes have existing text that you want to apply some formatting to, via a LaTeX command or environment, such as `\emph` or `\begin{theorem}...\end{theorem}`.

LaTeXTools' wrapping facility helps you in just these circumstances. All commands below are activated via a key binding, and *require some text to be selected first*. Also, as a mnemonic aid, *all wrapping commands involve typing <kbd>C+l</kbd>,<kbd>C+(something)</kbd> (which you can achieve by just holding the <kbd>C</kbd> key down after typing <kbd>l</kbd>).

- <kbd>C+l</kbd>,<kbd>C+c</kbd> wraps the selected text in a LaTeX command structure. If the currently selected text is `blah`, you get `\cmd{blah}`, and the letters `cmd` are highlighted. Replace them with whatever you want, then hit Tab: the cursor will move to the end of the command.
- <kbd>C+l</kbd>,<kbd>C+e</kbd> gives you `\emph{blah}`, and the cursor moves to the end of the command.
- <kbd>C+l</kbd>,<kbd>C+b</kbd> gives you `\textbf{blah}`
- <kbd>C+l</kbd>,<kbd>C+u</kbd> gives you `\underline{blah}`
- <kbd>C+l</kbd>,<kbd>C+t</kbd> gives you `\texttt{blah}`
- <kbd>C+l</kbd>,<kbd>C+n</kbd> wraps the selected text in a LaTeX environment structure. You get `\begin{env}`,`blah`, `\end{env}` on three separate lines, with `env` selected. Change `env` to whatever environment you want, then hit Tab to move to the end of the environment.


These commands also work if there is no selection. In this case, they try to do the right thing; for example, <kbd>C+l</kbd>,<kbd>C+e</kbd> gives `\emph{}` with the cursor between the curly braces.

You can also *change the current environment* using the <kbd>C+l</kbd>,<kbd>C+Shift+n</kbd> shortcut. Note how this works. First, the cursor must be inside the environment you are interested in. Second, the command selects the environment name in the `\begin{env}` command and also in the `\end{env}` command (using ST's multiple-selection support). This way you can rename the environment as needed. *Remember to exit multiple-selection mode* when you are done by pressing the <kbd>Esc<kbd key.

## Word Count

**Keybinding:** <kbd>C+l</kbd>,<kbd>w</kbd>

This uses [TeXcount](http://ctan.org/pkg/texcount) to generate a word count for the current document which is displayed in a quick panel. If you don't have the `TeXcount`, you will simply get an error message. Word counts in LaTeX documents can be quite finicky, and its worth reviewing the TeXcount documentation to ensure your document is setup to generate as accurate a word-count as possible. The counts returned are those reported by: `texcount -total -merge <main_file.tex>`.

The `word_count_sub_level` setting can be tweaked to display subcounts by chapter, section, etc. See the [Settings](settings.md).
