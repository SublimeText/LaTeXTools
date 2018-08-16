# Recommended Packages

This sections is an overview of other Sublime Text packages, which have LaTeX or general text writing support and work together with LaTeXTools.
It is recommended to install the packages using [Package Control].
This is neither a full list of all packages you may possible want to install nor a list of "must have" packages. However they are a collection of packages useful for tex writing you may consider to install.

*You think this section is missing a valuable package? Just create a PR to add the package.*


## Packages used by LaTeXTools

You should install these packages. They provide data, which is used by LaTeXTools or Sublime Text.

### LaTeX-cwl

The [LaTeX-cwl] package contains cwl files. These files are used by LaTeXTools to provide completions for commands and environments. *It is highly recommended to install that package.*

### Dictionaries

You are a non-native English speaker and write your LaTeX documents in an other language? You still want Sublime Text to spellcheck your documents? You need [Dictionaries] package, because it contains spellcheck files for many languages. With LaTeXTools you can add a TeX directive a the top of the root document. E.g. `% !TEX spellcheck=de_DE` to spellcheck your document in German.


## Packages designed for LaTeX

These packages are created especially for LaTeX.

### LaTeXSmartQuotes

The only purpose of [LaTeXSmartQuotes] is to improve and handle quotations inside tex files. It is very handy if you switch between English, German, and French, because it auto-detect the used language. However if you only use English it will still be helpful, because it inserts the quotes you most likely want to use at that position.

### LaTeXYZ

The [LaTeXYZ] package adds and changes features to Sublime Text you may want to use, but are missing in LaTeXTools. It is especially designed to work with LaTeXTools and enrich it with features. **Be aware that after the installation some hotkeys behave different.**


## Packages with LaTeX support

These are general purpose packages, but their features support LaTeX.

### BracketHighlighter

[BracketHighlighter] highlights your bracket similar to the built-in highlighter, but supports more bracket types and you can customize the highlighting style.

### ExpandRegion

With [ExpandRegion] you can expand your selection step-by-step.

## Packages for text writing

The packages in this section are useful in general. They are helpful to manage your files, use multiple selections, or write text.

### MultiEditUtils

With [MultiEditUtils] you improve the control of your multiple selections. It has several features for it.

### AlignTab

[AlignTab] adds a command to align tables. This can be useful for `tabular` and `align` environments.

``` js
// aligntab in tabular environment (context only available ST build 3127+)
{
    "keys": ["ctrl+l", "ctrl+alt+f"],
    "command": "align_tab",
    "args": {
        "user_input": "\\&"
    },
    "context":
    [
        { "key": "selector", "operator": "equal", "operand": "text.tex.latex meta.environment.tabular" }
    ]
},
// aligntab in math environments (for align)
{
    "keys": ["ctrl+l", "ctrl+alt+f"],
    "command": "align_tab",
    "args": {
        "user_input": "\\&"
    },
    "context":
    [
        { "key": "selector", "operator": "equal", "operand": "text.tex.latex meta.environment.math.block.be" }
    ]
},
```


### Inc-Dec-Value

With [Inc-Dec-Value] you can not just increase and decrease number, but also cycle through a self defined list of words.
Just select the word (eg. with ExpandRegion) and press the increase or decrease hotkey.

Example settings (Open *Preferences > Package Settings > Inc-Dec-Value > Settings - User*):

``` js
{
    "action_inc_all":  1,
    "action_dec_all": -1,
    "action_ins_all":  1,
    "user_enums": [
        // toggle begin and end of commands
        ["begin", "end"],
        // change section types
        ["subparagraph", "paragraph", "subsubsection", "subsection", "section", "chapter", "part"],
        // increase/decrese the font-size
        ["tiny", "scriptsize", "footnotesize", "small", "normalsize", "large", "Large", "LARGE", "huge", "Huge"],
    ]
}
```

### FileManager / SideBarTools / SideBarEnhancement

The packages [FileManager], [SideBarTools], and [SideBarEnhancement] all add features to manipulate files and the corresponding entries to the side bar and the quickpanel. Since there was a discussion about SideBarEnhancement violating the users privacy by collection anonymized statistics, there there has been published a fork with a subset of the features called SideBarTools. In addition to these FileManager is an additonal package with a similar feature set. If you are unsure which package you want to use you may start with FileManager.

[Package Control]:https://packagecontrol.io/
[LaTeX-cwl]:https://github.com/LaTeXing/LaTeX-cwl
[Dictionaries]:https://github.com/titoBouzout/Dictionaries
[LaTeXSmartQuotes]:https://github.com/r-stein/sublime-text-latex-smart-quotes
[LaTeXYZ]:https://github.com/randy3k/LaTeXYZ
[BracketHighlighter]:https://github.com/facelessuser/BracketHighlighter
[ExpandRegion]:https://github.com/aronwoost/sublime-expand-region
[MultiEditUtils]:https://github.com/philippotto/Sublime-MultiEditUtils
[AlignTab]:https://github.com/randy3k/AlignTab
[Inc-Dec-Value]:https://github.com/rmaksim/Sublime-Text-2-Inc-Dec-Value
[FileManager]:https://github.com/math2001/FileManager
[SideBarTools]:https://github.com/braver/SideBarTools
[SideBarEnhancement]:https://github.com/SideBarEnhancements-org/SideBarEnhancements
