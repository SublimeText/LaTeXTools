from .latex_fill_all import FillAllHelper
from .latextools_utils.settings import get_setting
from .latex_cwl_completions import BEGIN_END_BEFORE_REGEX
from .latex_cwl_completions import get_cwl_completions
from .latex_cwl_completions import is_cwl_available
from .latex_own_command_completions import get_own_env_completion


class EnvFillAllHelper(FillAllHelper):

    def get_completions(self, view, prefix, line):
        if not is_cwl_available():
            return

        completions = (
            get_cwl_completions().get_completions(env=True) +
            get_own_env_completion(view))

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
