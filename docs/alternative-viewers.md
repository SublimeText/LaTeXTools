# Alternate Viewers

## Preview.app

The Preview.app viewer is very straight-forward. It simply launches Preview.app with the relevant PDF file. Please note that Preview.app *does not* support forward or inverse sync, so you will not have that functionality available. Nevertheless, if you want to avoid installing another PDF viewer, this may be an acceptable option.

## Okular

The Okular viewer is quite similar to the Evince viewer. Forward sync (i.e., from Sublime to Okular) should work out of the box, but a caveat needs to be observed. For forward sync to work properly, the PDF document *must* be opened in Okular's unique session. If it is not, each forward sync command will open a new copy of the PDF. This also means that you can only have a *single* PDF document opened by LaTeXTools at a time.

If, when you run a forward sync, you get a message which reads **There's already a unique Okular instance running. This instance won't be the unique one.**, you will need to adjust the `sync_wait` settings, increasing the value until the error stops. See the [Linux](#linux2) platform settings.

To setup inverse sync (i.e., going from Okular to Sublime), in Okular open **Settings > Configure Okular > Editor**. From the dropdown menu, choose **Custom Text Editor** and in the **Command** box, fill in `subl "%f:%l"` (note that this assumes that you have `subl` in `/usr/bin` or another folder on your PATH).

## Zathura

Zathura mostly works out of the box without any configuration. However, because, unlike other viewers, it does not steal the focus under some circumstances, Zathura may not properly gain focus if you have set `keep_focus` to `false`. To ensure that the focus ends up on Zathura, you will have to install either [`wmctrl`](https://sites.google.com/site/tstyblo/wmctrl) or [`xodotool`](http://www.semicomplete.com/projects/xdotool/), which should be available through your package manager. You can, of course, install both.

## Command Viewer

Some support for other viewers is provided via the `command` viewer, which allows the execution of arbitrary commands to view a pdf or perform a forward search.

Using the command viewer requires that you configure the command(s) to be run in the platform-specific part of the `viewer_settings` block in your LaTeXTools preferences. There are three commands available:

 * `forward_sync_command`: the command to executing a forward search (`ctrl + l, j` or `cmd + l, j`).
 * `view_command`: the command to simply view the PDF document.

Of these, on `view_command` needs to be specified, though you will not have forward search capabilities unless you specify a `forward_sync_command` as well.

The following variables will be substitued with appropriate values inside your commands:

|Variable|Description|
|---------------------|--------------------------------------------------------|
|`$pdf_file`          | full path of PDF file, e.g. _C:\\Files\\document.pdf_|
|`$pdf_file_name`     | name of the PDF file, e.g. _document.pdf_|
|`$pdf_file_ext`      | extension of the PDF file, e.g. _pdf_|
|`$pdf_file_base_name`| name of the PDF file without the extension, e.g. _document_|
|`$pdf_file_path`     | full path to directory containing PDF file, e.g. _C:\\Files_|
|`$sublime_binary`    | full path to the Sublime binary|

In addition, the following variables are available for the `forward_sync_command` only:

|Variable|Description|
|---------------------|--------------------------------------------------------|
|`$src_file`          | full path of the tex file, e.g. _C:\\Files\\document.tex_|
|`$src_file_name`     | name of the tex file, e.g., _document.tex_|
|`$src_file_ext`      | extension of the tex file, e.g. _tex_|
|`$src_file_base_name`| name of the tex file without the extension, e.g. _document_|
|`$src_file_path`     | full path to directory containing tex file, e.g. _C:\\Files_|
|`$line`              | line to sync to|
|`$col`               | column to sync to|

If none of these variables occur in the command string, the `$pdf_file` will be appended to the end of the command.

Commands are executed in the `$pdf_file_path`, i.e., the folder containing the `$pdf_file`.

For example, you can use the command viewer to support Okular with the following settings:

```json
{
	"viewer": "command",

	"viewer_settings": {
		"linux": {
			"forward_sync_command": "okular --unique $pdf_file#src:$line$src_file",
			"view_command": "okular --unique"
		}
	}
}
```