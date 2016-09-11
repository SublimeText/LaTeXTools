# Keybindings

Keybindings have been chosen to make them easier to remember, and also to minimize clashes with existing (and standard) ST bindings. We take advantage of the fact that ST supports key combinations, i.e. sequences of two (or more) keys. The basic principle is simple:

* **Most LaTeXTools facilities are triggered using `Ctrl+l` (Windows, Linux) or `Cmd+l` (OS X), followed by some other key or key combination**

* Compilation uses the standard ST "build" keybinding, i.e. `Ctrl-b` on Windows and Linux and `Cmd-b` on OS X. So does the **GoTo Anything** facility (though this may change).

For example, to jump to the point in the PDF file corresponding to the current cursor position, use `Ctrl-l, j`: that is, hit `Ctrl-l`, then release both the `Ctrl` and the `l` keys, and quickly type the `j` key (OS X users: replace `Ctrl` with `Cmd`). To wrap the selected text in an `\emph{}` command, use `Ctrl-l, Ctrl-e`: that is, hit `Ctrl-l`, release both keys, then hit `Ctrl-e` (again, OS X users hit `Cmd-l` and then `Cmd-e`). 

`Ctrl-l` (`Cmd-l` on OS X) is the standard ST keybinding for "expand selection to line"; this is **remapped** to `Ctrl-l,Ctrl-l` (`Cmd-l,Cmd-l` on OS X). This is the *only* standard ST keybinding that is affected by the plugin---an advantage of new-style keybindings.

Most plugin facilities are invoked using sequences of 2 keys or key combinations, as in the examples just given. A few use sequences of 3 keys or key combinations.

Henceforth, I will write `C-` to mean `Ctrl-` for Linux or Windows, and `Cmd-` for OS X. You know your platform, so you know what you should use. In a few places, to avoid ambiguities, I will spell out which key I mean.


## Compiling LaTeX files

**Keybinding:** `C-b` (standard ST keybinding)

LaTeXTools offers a fully customizable build process. This section describes the default process, also called "traditional" because it is the same (with minor tweaks) as the one used in previous releases. However, see the section on [builder features](features.md#builder-features) for how to customize the build process.

The default ST Build command takes care of the following:

* It saves the current file
* It invokes the tex build command (`texify` for MikTeX; `latexmk` for TeXlive and MacTeX).
* It parses the tex log file and lists all errors, warnings and, if enabled, bad boxes in an output panel at the bottom of the ST window: click on any error/warning/bad boxes to jump to the corresponding line in the text, or use the ST-standard Next Error/Previous Error commands.
* It invokes the PDF viewer for your platform and performs a forward search; that is, it displays the PDF page where the text corresponding to the current cursor position is located.


## Toggling window focus following a build

**Keybinding:** `C-l,t,f` (yes, this means `C-l`, then `t`, then `f`)

By default, after compilation, the focus stays on the ST window. This is convenient if you like to work with the editor and PDF viewer window open side by side, and just glance at the PDF output to make sure that all is OK. If however the editor and viewer windows overlap (e.g. if you have a small screen), you may prefer the viewer window to get the focus (i.e. become the foremost window) after compiling. To this end, you can use the `toggle_focus` command to change this behavior. The first time you invoke this command, the focus will shift to the viewer window after compiling the current file; if you invoke the command again, the post-compilation focus reverts to the editor window. Every time you invoke `toggle_focus`, a message will appear in the status bar.

You can change the default focus behavior via the `keep_focus` option: see the "Settings" section below.

## Toggling PDF syncing (forward search) following a build

**Keybinding:** `C-l,t,s`

By default, after compilation, LaTeXTools performs a 'forward search' so that the PDF viewer shows the point in the PDF file corresponding to the current cursor position in ST (by the way, you can trigger a forward search at any other time, not just when you are compiling: see below). If for whatever reason you don't like this behavior, you can turn it off using the `toggle_fwdsync` command. As for `toggle_focus`, a message will appear in the status bar to reflect this.

You can also change the default sync behavior via the `forward_sync` option: see the "Settings" section below.

## Checking the status of toggles and defaults

**Keybinding:** `C-l,t,?`

This opens a quick panel displaying the current toggle values and their corresponding default settings. Selecting an entry in the quick panel will toggle the value (turning the feature on or off).

## Removing temporary files from build

**Keybinding:** `C-l,backspace`

This deletes all temporary files from a previous build (the PDF file is kept). Subfolders are traversed recursively. This command also clears the [LaTeXTools cache](#latextools-cache).

Two settings allow you to fine-tune the behavior of this command. `temp_files_exts` allows you to specify which file extensions should be considered temporary, and hence deleted. `temp_files_ignored_folders` allows you to specify folders that should not be traversed. A good example are `.git` folders, for people who use git for version control.

**Note**: If you use any of the special values with the output directory or auxiliary directory feature, the above is ignored, and the entire directory is simply deleted. If you are using the auxiliary directory feature *without* using an output directory, the auxiliary directory will be cleared and the normal process will be run.

## Clearing the cache

**Keybinding:** `C-l,C-d,C-c`

This clears the [LaTeXTools cache](#latextools-cache). It is useful if the LaTeXTools cache information gets too out of date, but you want to maintain the LaTeX build files, such as `.aux`.

## Forward and Inverse Search

**Keybinding:** `C-l,j` (for forward search; inverse search depends on the previewer)

When working in an ST view on a TeX document, `C-l,j` will display the PDF page where the text corresponding to the current cursor position is located; this is called a "forward search". The focus is controlled by the `C-l,t,f` toggle setting and the `keep_focus` option.

If you are viewing a PDF file, then hitting `CMD+Shift+Click` in Skim (OSX), double-clicking in Sumatra (Windows), or hitting `Ctrl+click` in Evince (Linux) will bring you to the location in the source tex file corresponding to the PDF text you clicked on. This is called "inverse search".

To open a PDF file without performing a forward search, use `C-l,v`.

For support of forward and inverse search in other viewers, see the viewer section below.

## References and Citations

**Keybinding:** *autotriggered* by default (see below). Otherwise, `C-l,x` for 'cross-reference,' `C-l,C-f`, or `C-l,C-alt-f` (via the Fill Helper facility: see below). These are fully equivalent ways of invoking ref/cite completions.

The basic idea is to help you insert labels in `\ref{}` commands and bibtex keys in `\cite{}` commands. The appropriate key combination shows a list of available labels or keys, and you can easily select the appropriate one. Full filtering facilities are provided. 

**Notes**: 

1. In order to find all applicable labels and bibtex keys, the plugin looks at the **saved** file. So, if you invoke this command and do not see the label or key you just entered, perhaps you haven't saved the file.

2. Only bibliographies in external `.bib` files are supported: no `\bibitem...`. Sorry. It's hard as it is. 

3. Multi-file documents are fully supported.

Now for the details. (Many of these features were contributed by Wes Campaigne and jlewegie, whom I thank profusely.)

By default, as soon as you type, for example, `\ref{` or `\cite{`, a quick panel is shown (this is the fancy drop-down list ST displays at the top of the screen), listing, respectively, all the labels in your files, or all the entries in the bibliographies you reference your file(s) using the `\bibliography{}` command. This is the default *auto-trigger* behavior, and it can be a big time saver. You can, however, turn it off, either temporarily using a toggle, or permanently by way of preference settings: see below. Once the quick panel is shown, you can narrow down the entries shown by typing a few characters. As with any ST quick panel, what you type will be fuzzy-matched against the label names or, for citations, the content of the first displayed line in each entry (by default, the author names, year of publication, short title and citation key: see below). This is *wildly* convenient, and one of the best ST features: try it!

If auto-triggering is off, when you type e.g. `\ref{`, ST helpfully provides the closing brace, leaving your cursor between the two braces. Now, you need to type `C-l,x` to get the quick panel  showing all labels in the current file. You can also type e.g. `\ref{aa` [again, the closing brace is provided by ST], then `C-l, x`, and LaTeXTools will show a list of labels that fuzzy-match the string `aa`. 

In either case, you then select the label you want, hit Return, and LaTeXTools inserts the **full ref command**, as in `\ref{my-label}`. The LaTeX command `\eqref` works the same way.  Citations from bibtex files are also supported in a similar way. Use `\cite{}`,  `\citet{}`,  `\citeyear{}` etc.

One often needs to enter **multiple citations**, as e.g. in `\cite{paper1,paper2}`. This is easy to do: either cite the first paper, e.g. `\cite{paper1}` and then, *with your cursor immediately before the right brace*, type a comma (`,`). Again, the default auto-trigger behavior is that the quick panel with appear, and you can select the second paper. If auto-trigger is off, then you enter the comma, then use the shortcut `C-l,x` to bring up the quick panel (note: you *must* add the comma before invoking the shortcut, or you won't get the intended result). Of course, you can enter as many citations as you want.

The display of bibliographic entries is *customizable*. There is a setting, `cite-panel-format`, that controls exactly what to display in each of the two lines each entry gets in the citation quick panel. Options include author, title, short title, year, bibtex key, and journal. This is useful because people may prefer to use different strategies to refer to papers---author-year, short title-year, bibtex key (!), etc. Since only the first line in each quick panel entry is searchable, how you present the information matters. The default should be useful for most people; if you wish to change the format, check the `LaTeXTools.sublime-settings` file for detailed information. (As usual, copy that file to the `User` directory and edit your copy, not the original).

Thanks to recent contributed code, **multi-file documents** are *fully supported*. LaTeXTools looks for references, as well as `\bibliography{}` commands, in the root file and in all recursively included files. Please see the information on [**Multi-file documents**](#multi-file-documents) in the section on [**General Features**](#general-features) for details on how to setup multi-file documents.

LaTeXTools now also looks `\addbibresource{}` commands, which provides basic compatibility with biblatex.

### Old-style, deprecated functionality

**For now**, completions are also injected into the standard ST autocompletion system. Thus, if you hit `Ctrl-space` immediately after typing, e.g., `\ref{}`, you get a drop-down menu at the current cursor position (not a quick-panel) showing all labels in your document. However, the width of this menu is OK for (most) labels, but not really for paper titles. In other words, it is workable for references, but not really for citations. Furthermore, there are other limitations dictated by the ST autocompletion system. So, this is **deprecated**, and I encourage you to use auto-trigger mode or the `C-l,x` or `C-l,C-f` keybindings instead.

## Forcing Citations and References

**Keybinding**: `C-l,alt-x,c` (citations) or `C-l,alt-x,r` (refs)

In some cases, it may be desirable to forcibly insert a citation key or label, i.e., if LaTeXTools does not automatically understand the command you are using. In such circumstances, you can use these keybindings to forcibly insert either a citation or reference at the cursor position. Note that the current word won't be overridden and any open brackets will not be completed if either of these options are used.

## Toggle auto trigger mode on/off

**Keybinding:** `C-l,t,a,r` for references; `C-l,t,a,c` for citations; `C-l,t,a,f` for input files; `C-l,t,a,e` for environments; `C-l,t,a,b` for smart brackets

These toggles work just like the sync and focus toggles above. Indeed, `C-l,t,?` will now also display the status of the auto trigger toggles. Check the status bar for feedback (i.e. to see what the current state of the toggle is), but remember the message stays on for only a few seconds. `C-l,t,?` is your friend.

## Fill Helper: filling in package and file names automatically

**Keybinding:** *autotriggered* by default (see below). Otherwise, `C-l,C-f` or `C-l,C-alt-f` (see below).

Thanks to the amazing work by users btstream and Ian Bacher, LaTeXTools now offers a list of available files and packages when using commands such as `\usepackage`, `\include`, `\includegraphics`, `\includesvg` and `\input`. Assuming autocompletion is toggled on (the default):

 * when you type `\usepackage{`, a list of available package is displayed in the ST drop-down menu. Pick the one you need, and it will be inserted in your file, with a closing brace.

 * when you type any of the file-related input commands, a list of files in the current directory is displayed (suitably filtered, so graphics files are displayed for `\includegraphics`).

To toggle autocompletion on or off, use the `fill_auto_trigger` setting, or the `C-l,t,a,f` toggle.

In order for package autocomplete to work, you need to create a cache first. You can do it using the Command Palette: select `LaTeXTools: Build cache for LaTeX packages`.

The `C-l,C-f` keyboard shortcut also works for `\ref` and `\cite` completion. Basically, wherever you can use `C-l,x`, you can also use `C-l,C-f`. 

The `C-l,C-alt-f` keyboard shortcut is identical to the `C-l,C-f` shortcut, except that it ensures that the current word that the cursor is within is replaced. This is useful for, e.g., switching one citation for another or one label for another.

## Jumping to sections and labels

**Keybinding:** `C-r` (standard ST keybinding)

The LaTeXtools plugin integrates with the awesome ST "Goto Anything" facility. Hit `C-r`to get a list of all section headings, and all labels. You can filter by typing a few initial letters. Note that section headings are preceded by the letter "S", and labels by "L"; so, if you only want section headings, type "S" when the drop-down list appears.

Selecting any entry in the list will take you to the corresponding place in the text.

## Jump to Anywhere

**Keybinding:** `C-l, C-j` or `C-l, C-o` (see [below](#jumping-to-included-files))

**Mousebinding:** `ctrl-alt-leftclick` (Windows) / `super-leftclick` Linux) / `ctrl-super-leftclick` (OSX)

**Mousebinding (With SublimeCodeIntel):** `alt-leftclick` (Windows) / `super-leftclick` Linux) / `ctrl-leftclick` (OSX)

This is an IDE-like mouse navigation, which executes a jump depending on the context around the cursor. It is easy to use and intuitive. Just click with the mouse on a command while pressing the modifier key. The corresponding jump will be executed. Supported jump types are:

- Jump to referenced labels (e.g. `\ref`)
- Jump to citation entries in bibliography files (e.g. `\cite`)
- Open included files (e.g. `\input` or `\include`)
- Open root file from `%!TEX root =...` magic comment
- Open bibliographies (e.g. `\bibliography` or `\addbibresource`)
- Open included graphics with a specified program (e.g. `\includegraphics`)
- Open the documentation of used packages (e.g. `\usepackage`)
- Jump to self-defined command definition, i.e. jump to the `\newcommand` in which the command was defined

### SublimeCodeIntel Integration
If you use [SublimeCodeIntel](https://github.com/SublimeCodeIntel/SublimeCodeIntel) you recognize the alternative mouse-bindings and it does not work out of the box. Just open the command palette and run the command `LaTeXTools: Create Mousemap in User folder`. This will create a mouse-map in the user folder or modify the existing one to add the mouse-binding with the same modifiers as SublimeCodeIntel. This mouse-binding has a `fallback_command` command as argument. This command will be executed if the command in called outside a LaTeX document.

### Jumping to included files
To open a file included using, e.g., `\input` or `\include` or a bibliography, simply click while holding down the modifier key or press `C-l, C-j`. Sublime will open the included file.

There is an additional keybinding `C-l, C-o` to jump to included files. If the file already exists, this behaves just like `C-l, C-j`. However, if the file does not exist, it will also create the missing file and, if a `tex` file, will add the magic root entry (`%!TEX root=`) to the new file. This can be used to easily create files or to open already existing files.

### Image files
To open an image, which is included with `\includegraphics` just click on the command while pressing the modifier key or press `C-l, C-j`.

The program to open the image can be configured in the LaTeXTools settings in the `open_image_command` setting.

The following sub-settings are provided:

- `image_types`: a list of the image file types used in the `\includegraphics` command. This list is also used in the Fill Helper and to determine missing extensions to open images. When opening an image the `image_types`-list will be matched from left to right.
- `open_image_command`: the command/program to open an image used in the `\includegraphics` command. This commands can be configured OS-specific. For each OS you can create a list, which will be searched top-down for the matching extension. Each entry in the list has a `command` and `extension` field. The command is a string and will be executed with the file path appended, if the extension matches the extension of the file. You can optionally use `$file` inside the string to insert the file path at an arbitrary position. The `extension` can either be a string or a list of string. If it is missing, the command will be executed for every file type.

### Packages
If you use the command while the cursor is inside a `\usepackage` command, the documentation for the corresponding package will be opened in your default PDF viewer.

## LaTeX commands and environments

**Keybindings:** `C-l,c` for commands and `C-l,e` for environments

To insert a LaTeX command such as `\color{}` or similar, type the command without backslash (i.e. `color`), then hit `C-l,c`. This will replace e.g. `color` with `\color{}` and place the cursor between the braces. Type the argument of the command, then hit Tab to exit the braces.

Similarly, typing `C-l,e` gives you an environment: e.g. `test` becomes

	\begin{test}

	\end{test}

and the cursor is placed inside the environment thus created. Again, Tab exits the environment. 

Note that all these commands are undoable: thus, if e.g. you accidentally hit `C-l,c` but you really meant `C-l,e`, a quick `C-z`, followed by `C-l,e`, will fix things.

## Wrapping existing text in commands and environments

**Keybindings:** `C-l,C-c`, `C-l, C-n`, etc.

The tab-triggered functionality just described is mostly useful if you are creating a command or environment from scratch. However, you sometimes have existing text, and just want to apply some formatting to it via a LaTeX command or environment, such as `\emph` or `\begin{theorem}...\end{theorem}`.

LaTeXTools' wrapping facility helps you in just these circumstances. All commands below are activated via a key binding, and *require some text to be selected first*. Also, as a mnemonic aid, *all wrapping commands involve typing `C-l,C-something` (which you can achieve by just holding the `C-` key down after typing `l`).

- `C-l,C-c` wraps the selected text in a LaTeX command structure. If the currently selected text is `blah`, you get `\cmd{blah}`, and the letters `cmd` are highlighted. Replace them with whatever you want, then hit Tab: the cursor will move to the end of the command.
- `C-l,C-e` gives you `\emph{blah}`, and the cursor moves to the end of the command.
- `C-l,C-b` gives you `\textbf{blah}`
- `C-l,C-u` gives you `\underline{blah}`
- `C-l,C-t` gives you `\texttt{blah}`
- `C-l,C-n` wraps the selected text in a LaTeX environment structure. You get `\begin{env}`,`blah`, `\end{env}` on three separate lines, with `env` selected. Change `env` to whatever environment you want, then hit Tab to move to the end of the environment.


These commands also work if there is no selection. In this case, they try to do the right thing; for example, `C-l,C-e` gives `\emph{}` with the cursor between the curly braces.

You can also *change the current environment* using the `C-l,C-Shift-n` shortcut. Note well how this works. First, the cursor must be inside the environment you are interested in. Second, the command selects the environment name in the `\begin{env}` command and also in the `\end{env}` command (using ST's multiple-selection support). This way you can rename the environment as needed. *Remember to exit multiple-selection mode* when you are done by pressing the `ESC` key.

## Word Count

**Keybinding:** `C-l,w`

This uses [TeXcount](http://ctan.org/pkg/texcount) to generate a word count for the current document which is displayed in a quick panel. If you don't have the `TeXcount`, you will simply get an error message. Word counts in LaTeX documents can be quite finicky, and its worth reviewing the TeXcount documentation to ensure your document is setup to generate as accurate a word-count as possible. The counts returned are those reported by: `texcount -total -merge <main_file.tex>`.

The `word_count_sub_level` setting can be tweaked to display subcounts by chapter, section, etc. See the [Settings](#settings).
