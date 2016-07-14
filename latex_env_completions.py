try:
    _ST3 = True
    from .latex_fill_all import FillAllHelper
    from .latextools_utils import get_setting
    from .latex_cwl_completions import (
        parse_cwl_file, parse_line_as_environment, is_cwl_available,
        BEGIN_END_BEFORE_REGEX
    )
except:
    _ST3 = False
    from latex_fill_all import FillAllHelper
    from latextools_utils import get_setting
    from latex_cwl_completions import (
        parse_cwl_file, parse_line_as_environment, is_cwl_available,
        BEGIN_END_BEFORE_REGEX
    )


class EnvFillAllHelper(FillAllHelper):

    def get_completions(self, view, prefix, line):
        if not is_cwl_available():
            return

        completions = parse_cwl_file(parse_line_as_environment)

        if prefix:
            completions = [c for c in completions if c[1].startswith(prefix)]

        show_entries = [c[0].split('\t') for c in completions]
        completions = [c[1] for c in completions]
        return show_entries, completions

    def matches_line(self, line):
        return bool(
            BEGIN_END_BEFORE_REGEX.match(line)
        )

    def is_enabled(self):
        return get_setting('env_auto_trigger', True)
