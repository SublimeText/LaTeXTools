# Requirements and Setup

You will need to be running either SublimeText 2 or 3. For ST3, the plugin has been tested against the latest beta versions, though it may work for dev builds as well.

You will also need to install a TeX distribution, but this can be done separately. The various options for TeX distributions are discussed in the OS-specific sections below.

## Installation

The recommended way to install the LaTeXTools plugin is via [Package Control](https://packagecontrol.io/). It's awesome and makes it easy to keep your installed packages up-to-date. If you don't already have Package Control, instructions to install it can be found [here](https://packagecontrol.io/installation) (it's very easy!).

Once, you have Package Control installed, launch the **Command Palette** by pressing <kbd>Ctrl+shift+p</kbd> (Windows / Linux) or <kbd>⌘+shift+p</kbd> (OS X) and select the **Package Control: Install Package** option. This will bring up a quick panel with a list of installable plugins. Start typing **LaTeXTools** and when you see it, select it. That's it!

If you prefer a more hands-on approach, you can always clone the [git repository](https://github.com/SublimeText/LaTeXTools.git) or else just [grab the plugin's .zip file from GitHub](https://github.com/SublimeText/LaTeXTools/archive/master.zip) and extract it to your Sublime **Packages** directory (you can open it easily from ST, by clicking on **Preferences | Browse Packages**). Please note that if you do a manual installation, the package **must** be named "LaTeXTools".

If you are running LaTeXTools for the first time, you may want to run the **LaTeXTools: Reset user settings to default** command from the **Command Palette** to get an editable copy of the settings file. To open this file, please select **Preferences | Package Settings | LaTeXTools | Settings – User**. Please pay careful attention to the settings in the [Platform-Specific Settings](#platform-specific-settings) for your platform, as these may need to be adjusted for your environment. See the OS-specific instructions below for details on what needs to be adjusted.

## OS X

### Distribution

On **OSX**, you need to be running the [MacTeX](https://www.tug.org/mactex/) distribution (which is pretty much the only one available on the Mac anyway). Just download and install it in the usual way. We have tested MacTeX versions 2010--2016, both 32 and 64 bits; these work fine. MacTeX 2008 does *not* seem to work out of the box, so please upgrade.

If you don't want to install the entire MacTeX distribution—which is pretty big—[BasicTeX](https://www.tug.org/mactex/morepackages.html) will also work, though you may need to spend more time ensuring all the packages you need are installed! One such package that is missing is `latexmk`, which is a script for building LaTeX documents, which LaTeXTools uses by default. You can either choose to install `latexmk` or [change the builder](#builder.md) to use a builder that does not require `latexmk`. To install `latexmk`, you can either use the **TeX Live Utility** (assuming you are using a recent version of BasicTeX) or from the **Terminal** type `sudo tlmgr install latexmk`, which will prompt you for your password and install the `latexmk` package.

### Setup Skim

We recommend that you install the [Skim PDF viewer](http://skim-app.sourceforge.net/), as this provides forward and inverse search capabilities, which are very useful! Skim is the default viewer that LaTeXTools uses on OS X. If you don't install Skim, please see the information on [available viewers](available-viewers.md#preview) for details on how to setup LaTeXTools to work with Preview.app

To configure inverse search, in Skim, open the **Preferences** dialog, select the **Sync** tab, then:

 * Uncheck the "Check for file changes" option
 * Choose the Sublime Text preset (for ST3) or Sublime Text 2 (for ST2)

If you are using an old version of Skim without built-in support for ST,  you can always choose the Custom preset and enter (for ST3): `/Applications/Sublime Text.app/Contents/SharedSupport/bin/subl` in the **Command** field, and `"%file":%line` in the **Arguments** field.

#### Setup ImageMagick and Ghostscript

If you are using Sublime Text 3 version 3118 or later and want to use the equation preview feature or use the image preview feature for PDFs, EPSs, or PSs, you will need to ensure that Ghostscript 8 or higher is installed and available on the `texpath` defined for your machine. If you installed the full MacTeX distribution, Ghostscript is already included. If you installed the BasicTeX distribution, you will need to install Ghostscript yourself.

If you do not want to use the equation preview feature, change the `preview_math_mode` setting to `"none"` when you are configuring your settings.

Similarly, if you would like to use the image preview feature to view file types not support by SublimeText or Ghostcript (so anything other than PNGs, JPEGs, GIFs, PDFs, EPSs, and PSs), you will need to ensure that ImageMagick is installed on your machine and available on your `texpath`.

If you do not want to use the image preview feature, change the `preview_image_mode` setting to `"none"` when you are configuring your settings.

The easiest way to install ImageMagick or Ghostscript is to use either [Homebrew](http://brew.sh/) or [MacPorts](https://www.macports.org/). Installing should be as simple as typing the relevant command in the Terminal:

|Product|Package Manager|Command|
|-------|---------------|-------|
|ImageMagick|Homebrew|`brew install imagemagick`|
|ImageMagick|Mac Ports|`sudo port install ImageMagick`|
|Ghostscript|Homebrew|`brew install ghostscript`|
|Ghostscript|Mac Ports|`sudo port install ghostscript`|

If you do not use Homebrew or MacPorts (and you should), you will need to compile and install binaries from source. The source for Ghostscript can be found [on this page](http://ghostscript.com/download/gsdnld.html) and the source and compilation instructions for ImageMagick can be found [on this page](http://www.imagemagick.org/script/binary-releases.php#macosx).

You can use the **LaTeXTools: Check System** command to verify that these are installed and setup in a place LaTeXTools can find.

### Configure LaTeXTools Settings

To edit the LaTeXTools user settings, select **Preferences | Package Settings | LaTeXTools | Settings – User** from the ST menu and scroll down to the  section titled **Platform settings** and find the **osx** block. 

Within that block, verify that the `"texpath"` setting is correct. This setting is use by LaTeXTools to determine the `PATH` used for running TeX and friends which, because of how LaunchControl works will differ from your path on the shell. The default value should work with MacTeX installed in the normal way, but you will want to verify that this setting is correct. Note that your `"texpath"` **must** include `$PATH`.

<!-- TODO: does this belong here? -->
### El Capitan

Prior to El Capitan, MacTeX defaulting to installing itself in the `/usr` directory. However, beginning with El Capitan, applications can no longer write to `/usr`. MacTeX 2015 and later remedies this by creating a link to TeX binaries in `/Library/TeX` you can read more about this [on the MacTeX site](https://www.tug.org/mactex/elcapitan.html). The default LaTeXTools settings file now adds `/Library/TeX/texbin` to the `texpath`. In practice, this means the following:

 * If you are running MacTeX 2015 and do *not* have the `texpath` option in your user settings file, you do not need to take further action.
 * If you are running MacTex 2015 and have the `texpath` setting open your user settings file (remember, you can do so from the **Preferences | Package Settings | LaTeXTools** submenu) and add `/Library/TeX/texbin` as the first entry in `texpath`.
 * If you are running earlier MacTeX versions, unfortunately you do *not* have the `/Library/TeX/texbin` link at all, so adding that path to `texpath` would not help. You have two options: create the link yourself, or edit the `texpath` option to point to the appropriate directory. Check Section 8 of [this document](https://tug.org/mactex/UpdatingForElCapitan.pdf) for details.

Sorry for the complications. It's not my fault.

## Windows

### Distribution

On **Windows**, both [MiKTeX](http://www.miktex.org/) and [TeXLive](https://www.tug.org/texlive/) are supported. Pick one and install it following the relevant documentation.

### Setup Sumatra

We recommend that you also install the [Sumatra PDF viewer](http://www.sumatrapdfreader.org/). Its very light-weight and supports both forward and inverse search. It is also the only viewer supported on Windows. Just download and install it in the normal way.

Once you've installed SumatraPDF, its a good idea to add it to your `PATH` so that LaTeXTools can easily find it. To do this, find the folder you installed SumatraPDF to (usually `C:\Program Files\SumatraPDF`). Once you have this, open the command line (`cmd.exe`) and run `setx PATH %PATH%;C:\Program Files\SumatraPDF`, changing the `C:\Program Files\SumatraPDF` depending on where you actually installed it.

You now need to set up inverse search in Sumatra PDF. However, the GUI for doing this is hidden in Sumatra until you open a PDF file that has actual synchronization information (that is, an associated `.synctex.gz` file). See [this forum post](http://forums.fofou.org/sumatrapdf/topic?id=2026321) for details. 

If you have a PDF file with a corresponding `.synctex.gz` file, then open it in Sumatra and go to **Settings | Options**, and enter:

 * (ST3) `"C:\Program Files\Sublime Text 3\sublime_text.exe" "%f:%l"`
 * (ST2) `"C:\Program Files\Sublime Text 2\sublime_text.exe" "%f:%l"` 

as the inverse-search command line (in the text-entry field at the bottom of the options dialog). You may need to modify these paths depending on where you installed ST.

If you do not already have such a file, you can easily create one by compiling any LaTeX file with `pdflatex -synctex=1 <file.tex>` and opening the resulting PDF in SumatraPDF. Alternatively, you can open the console (`cmd.exe`) and run the following command (assuming SumatraPDF.exe is on your `PATH`):

`sumatrapdf.exe -inverse-search "\"C:\Program Files\Sublime Text 3\sublime_text.exe\" \"%f:%l\""`

(Adapt as necessary for ST2 or depending on the path you installed ST to)

I'm sorry this is not straightforward---it's not my fault :-)

#### Setup ImageMagick and Ghostscript

If you are using Sublime Text 3 version 3118 or later and want to use the equation preview feature or use the image preview feature for PDFs, EPSs, or PSs, you will need to ensure that Ghostscript 8 or higher is installed and available on the `texpath` defined for your machine.

If you do not want to use the equation preview feature, change the `preview_math_mode` setting to `"none"` when you are configuring your settings.

To install and setup Ghostcript:

* If you are using MiKTeX, LaTeXTools should automatically find the MiKTeX Ghostscript install, provided MiKTeX is available on your `PATH` system variable or via the LaTeXTools `texpath` setting.
* If you are using TeXLive and you installed the default profile, you should already have Ghostscript installed in `<drive>:path\to\texlive\<year>\tlpkg\tlgs\bin`. Make sure this is added to your `PATH` system variable or to the `texpath` when setting up LaTeXTools.
* If you do not have Ghostscript installed, you can simple download and install the [latest release here](http://ghostscript.com/download/gsdnld.html).

Similarly, if you would like to use the image preview feature to view file types not support by SublimeText or Ghostcript (so anything other than PNGs, JPEGs, GIFs, PDFs, EPSs, and PSs), you will need to ensure that [ImageMagick](http://www.imagemagick.org/) is installed on your machine, which you should be able to do using one of the [binary releases](http://www.imagemagick.org/script/binary-releases.php#windows). Once ImageMagick is installed, ensure its location is either added to your `PATH` system variable or the `texpath` LaTeXTools setting.

If you do not want to use the image preview feature, change the `preview_image_mode` setting to `"none"` when you are configuring your settings.

You can use the **LaTeXTools: Check System** command to verify that these are installed and setup in a place LaTeXTools can find.

### Configure LaTeXTools Settings

To edit the LaTeXTools user settings, select **Preferences | Package Settings | LaTeXTools | Settings – User** from the ST menu and scroll down to the  section titled **Platform settings** and find the **windows** block.

Within that block, verify that the `"texpath"` setting is correct. This setting is use by LaTeXTools to determine the `PATH` used for running TeX and friends. Both MiKTeX and TeXLive by default add themselves to your `PATH`, but if you told them not to, you will need to ensure that they are added to the path here.

If you did not follow the instructions above to add SumatraPDF to your path, you will need to change the `sumatra` to point to you Sumatra install. Normally, it will end up being `C:\Program Files\SumatraPDF\SumatraPDF.exe`.

Finally, you need to ensure that the `distro` setting is correct. The possible values are `"miktex"` and `"texlive"`, depending on which distribution you installed.

## Linux

**Linux** support is coming along nicely. However, as a general rule, you will need to do some customization before things work. This is due to differences across distributions (a.k.a. "fragmentation"). Do not expect things to work out of the box.

### Distribution

You need to install TeXLive.

We highly recommend installing the version directly from TUG, which can be found [here](https://www.tug.org/texlive/acquire-netinstall.html) rather than the version included with your distribution, as TeXLive is generally updated more regularly and tends to include more features. In particular, if you are on Ubuntu, note that `apt-get install texlive` will get you a working but incomplete setup. For example, it will *not* install `latexmk`, which is essential to LaTeXTools. You need to install it via `apt-get install latexmk`. However, as long as the expected binaries are available on your system, LaTeXTools should generally work.

You can use the **LaTeXTools: Check System** command to ensure that the expected binaries are found.

#### Setup ImageMagick and Ghostscript

If you are using Sublime Text 3 version 3118 or later and want to use the equation preview feature or use the image preview feature for PDFs, EPSs, or PSs, you will need to ensure that Ghostscript 8 or higher is installed and available on the `texpath` defined for your machine.

If you do not want to use the equation preview feature, change the `preview_math_mode` setting to `"none"` when you are configuring your settings.

Similarly, if you would like to use the image preview feature to view file types not support by SublimeText or Ghostcript (so anything other than PNGs, JPEGs, GIFs, PDFs, EPSs, and PSs), you will need to ensure that ImageMagick is installed on your machine and available on your `texpath`. Note that for some image formats, ImageMagick also requires Ghostscript to be installed.

If you do not want to use the image preview feature, change the `preview_image_mode` setting to `"none"` when you are configuring your settings.

If you installed the full TeXLive profile from TUG, you should already have a version of Ghostscript installed. Otherwise, it can simply be installed using your distribution's package manager. ImageMagick should also be available the same way.

Once again, you can use the **LaTeXTools: Check System** command to verify that these are setup in a place LaTeXTools can find.

### Setup Viewer

By default, LaTeXTools assumes you are using Evince (Document Viewer) as your PDF viewer. Support is also available for Okular and Zathura and other viewers that can be run via the command line. See the section on [available-viewers](available-viewers.md) for details on how to setup other viewers.

Evince is already installed by default on any distro that provides the Gnome desktop environment, but if it hasn't been, it can be installed using your distribution's package manager. In addition to Evince, you will need to ensure you have the Python bindings for `dbus` and the Python bindings for Gnome, i.e. `gobject` or `python-gi`, depending on your distribution. If you use the Gnome desktop, you likely already have these, but if not, you will need to install them using your distribution's package manager. In particular, they are reportedly not installed on Arch Linux by default.

Unlike other viewers and platforms, Evince forward and backward search should work out of the box thanks to the magic of `dbus`, but if not, please let us know!


### Configure LaTeXTools Settings

To edit the LaTeXTools user settings, select **Preferences | Package Settings | LaTeXTools | Settings – User** from the ST menu and scroll down to the  section titled **Platform settings** and find the **linux** block.

Within that block, verify that the `"texpath"` setting is correct. This setting is use by LaTeXTools to determine the `PATH` used for running TeX and friends. Please note that if you use Unity (the default launcher on Ubuntu), ST can end up "seeing" a different `PATH` then you will in the terminal. This is because Unity inherits its environment from `/bin/sh` rather than `/bin/bash`, `/bin/zsh`, `/bin/fish`, etc. This means that you may need to add the path to TeX and friends to your `"texpath"` for LaTeXTools to work.

If your `PATH` contains a Python distribution that is not the default Python distribution, it may be necessary to configure the `"python"` setting to point to the system Python distribution. There have been reports of issues using `dbus` and `gobject` on **conda** and similar Python releases.
