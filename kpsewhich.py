from __future__ import print_function

import sublime
import traceback

if sublime.version() < '3000':
    _ST3 = False
    from latextools_utils.external_command import (
        check_output, CalledProcessError
    )
else:
    _ST3 = True
    from .latextools_utils.external_command import (
        check_output, CalledProcessError
    )

__all__ = ['kpsewhich']


def kpsewhich(filename, file_format=None, notify_user_on_error=False):
    # build command
    command = ['kpsewhich']
    if file_format is not None:
        command.append('-format=%s' % (file_format))
    command.append(filename)

    try:
        return check_output(command)
    except CalledProcessError as e:
        if notify_user_on_error:
            sublime.error_message(
                'An error occurred while trying to run kpsewhich. '
                'Files in your TEXINPUTS could not be accessed.'
            )
            if e.output:
                print(e.output)
            traceback.print_exc()
    except OSError:
        if notify_user_on_error:
            sublime.error_message(
                'Could not run kpsewhich. Please ensure that your texpath '
                'setting is correct.'
            )
            traceback.print_exc()

    return None
