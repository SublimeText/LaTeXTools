import sublime

if int(sublime.version()) < 3143:
    print(__package__ + " requires ST 3143+")
else:
    import sys

    # clear modules cache if package is reloaded (after update?)
    prefix = __package__ + "."  # don't clear the base package
    for module_name in [
        module_name
        for module_name in sys.modules
        if module_name.startswith(prefix) and module_name != __name__
    ]:
        del sys.modules[module_name]

    from .latextools.utils.logging import logger, init_logger, shutdown_logger

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
    from .latextools.biblatex_snippet_completions import (
        SnippetCompletions
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
        LatextoolsClearBibliographyCacheCommand,
        LatextoolsDeleteTempFilesCommand,
    )
    from .latextools.deprecated_command import (
        LatextoolsFindDeprecatedCommandsCommand
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
    from .latextools.latex_cwl_completions import (
        LatexCwlCompletion
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
        LatextoolsDoOutputEditCommand,
        LatextoolsDoFinishEditCommand,
        LatextoolsExecEventListener,
    )
    from .latextools.migrate import (
        LatextoolsMigrateCommand
    )
    from .latextools.preview.preview_image import (
        PreviewImageHoverListener,
        PreviewImagePhantomListener
    )
    from .latextools.preview.preview_math import (
        MathPreviewPhantomListener
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
        LatextoolsSystemCheckCommand,
        LatextoolsInsertTextCommand
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
    from .latextools.utils.input_quickpanel import (
        InputQuickpanelListener,
        LatextoolsConfirmQuickpanelCommand
    )


    def _filter_func(name):
        return name.startswith(prefix) and name not in (__name__, "latextools")


    def plugin_loaded():
        init_logger()
        for name in sorted(filter(_filter_func, sys.modules)):
            module = sys.modules[name]
            if hasattr(module, "plugin_loaded"):
                logger.debug("calling %s.plugin_loaded()", name)
                module.plugin_loaded()


    def plugin_unloaded():
        for name in sorted(filter(_filter_func, sys.modules)):
            module = sys.modules[name]
            if hasattr(module, "plugin_unloaded"):
                logger.debug("calling %s.plugin_unloaded()", name)
                module.plugin_unloaded()

        shutdown_logger()
