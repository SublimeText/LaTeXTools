import sys

# clear modules cache if package is reloaded (after update?)
prefix = __spec__.parent + "."  # don't clear the base package
for module_name in [
    module_name
    for module_name in sys.modules
    if module_name.startswith(prefix) and module_name != __spec__.name
]:
    del sys.modules[module_name]
globals().pop("module_name", None)
del globals()["prefix"]

from .latextools.auto_label import (
    LatextoolsAutoInsertLabelCommand,
    LatextoolsAutoInserLabelListener,
)
from .latextools.biblatex_crossref_completions import (
    BiblatexCrossrefCompletions
)
from .latextools.biblatex_field_name_completions import (
    FieldNameCompletions
)
from .latextools.biblatex_name_completions import (
    BiblatexNameCompletions
)
from .latextools.biblatex_syntax_listener import (
    BibLaTeXSyntaxListener
)
from .latextools.change_environment import (
    LatextoolsChangeEnvironmentCommand,
    LatextoolsToggleEnvironmentStarCommand,
)
from .latextools.context_provider import (
    LatextoolsContextListener
)
from .latextools.delete_temp_files import (
    LatextoolsClearCacheCommand,
    LatextoolsClearLocalCacheCommand,
    LatextoolsDeleteTempFilesCommand,
)
from .latextools.detect_spellcheck import (
    LatextoolsAutoDetectSpellcheckListener,
    LatextoolsDetectSpellcheckCommand
)
from .latextools.jumpto_anywhere import (
    LatextoolsJumptoAnywhereCommand,
    LatextoolsJumptoAnywhereByMouseCommand
)
from .latextools.jumpto_pdf import (
    LatextoolsJumptoPdfCommand,
    LatextoolsViewPdfCommand,
)
from .latextools.jumpto_tex_file import (
    LatextoolsJumptoFileCommand
)
from .latextools.latex_command import (
    LatextoolsLatexCmdCommand
)
from .latextools.latex_command_completions import (
    LatexCmdCompletion
)
from .latextools.latex_directive_completions import (
    LatexDirectiveCompletion
)
from .latextools.latex_doc_viewer import (
    LatextoolsPkgDocCommand,
    LatextoolsViewDocCommand
)
from .latextools.latex_env import (
    LatextoolsLatexEnvCommand
)
from .latextools.latex_env_closer import (
    LatextoolsLatexEnvCloserCommand
)
from .latextools.latex_fill_all import (
    LatexFillAllEventListener,
    LatextoolsFillAllCommand,
    LatexToolsFillAllCompleteBracket,
    LatexToolsReplaceWord
)
from .latextools.latex_installed_packages import (
    LatextoolsGenPkgCacheCommand
)
from .latextools.latextools_cache_listener import (
    LatextoolsCacheUpdateListener,
    LatextoolsAnalysisUpdateCommand,
    LatextoolsBibcacheUpdateCommand,
)
from .latextools.make_pdf import (
    LatextoolsMakePdfCommand,
    LatextoolsExecEventListener,
)
from .latextools.reset_settings import (
    LatextoolsResetSettingsCommand
)
from .latextools.preview import (
    ImagePreviewHoverListener,
    PreviewPhantomListener
)
from .latextools.reveal_folders import (
    LatextoolsRevealAuxDirectoryCommand,
    LatextoolsRevealOutputDirectoryCommand,
    LatextoolsRevealTexRootDirectoryCommand
)
from .latextools.search_commands import (
    LatextoolsSearchCommandCommand,
    LatextoolsSearchCommandInputCommand
)
from .latextools.smart_paste import (
    LatextoolsDownloadInsertImageHelperCommand,
    LatextoolsSmartPasteCommand
)
from .latextools.system_check import (
    LatextoolsSystemCheckCommand
)
from .latextools.tex_count import (
    LatextoolsTexcountCommand
)
from .latextools.tex_syntax_listener import (
    TeXSyntaxListener
)
from .latextools.toc_quickpanel import (
    LatextoolsTocQuickpanelCommand,
    LatextoolsTocQuickpanelContext
)
from .latextools.toggle_settings import (
    LatextoolsToggleKeysCommand
)

from .plugins.viewer.dbus_viewer import LatextoolsDbusViewerListener


def plugin_loaded():
    from .latextools.utils.logging import init_logger
    init_logger()

    prefix = __spec__.parent + "."
    for name, module in sys.modules.items():
        if (
            name.startswith(prefix) 
            and hasattr(module, "latextools_plugin_loaded")
        ):
            module.latextools_plugin_loaded()


def plugin_unloaded():
    prefix = __spec__.parent + "."
    for name, module in sys.modules.items():
        if (
            name.startswith(prefix) 
            and hasattr(module, "latextools_plugin_unloaded")
        ):
            module.latextools_plugin_unloaded()

    from .latextools.utils.logging import shutdown_logger
    shutdown_logger()
