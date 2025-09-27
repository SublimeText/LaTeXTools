from __future__ import annotations
import os
import re
import sublime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pdf_builder import Command, CommandGenerator, CommandLine

from ...latextools.utils.logging import logger

from .pdf_builder import PdfBuilder

__all__ = ["BasicBuilder"]

# Standard LaTeX warning
CITATIONS_REGEX = re.compile(
    r"""
    Warning:\s+
    (?: Citation\s+[`'].+'\s+(?:on\s+page\s+\d+\s+)?undefined
    | Empty\s+bibliography\s )
    """,
    re.M | re.X,
)
# Capture which program to run for BibLaTeX
BIBLATEX_REGEX = re.compile(r"Package biblatex Warning: Please \(re\)run (\S*)")
# Used to indicate a subdirectory that needs to be made for a file input using
# \include
FILE_WRITE_ERROR_REGEX = re.compile(r"! I can't write on file `(.*)/([^/']*)'", re.M)


class BasicBuilder(PdfBuilder):
    """
    BasicBuilder class

    This is a more fully functional verion of the Simple Builder
    concept. It implements the same building features as the
    Traditional builder.
    """

    name = "Basic Builder"

    def commands(self) -> CommandGenerator:
        self.run_in_shell = False
        engine = self.engine
        if "la" not in engine:
            # we need the command rather than the engine
            engine = {
                "pdftex": "pdflatex",
                "xetex": "xelatex",
                "luatex": "lualatex",
            }.get(engine, "pdflatex")

        if engine not in ["pdflatex", "xelatex", "lualatex"]:
            engine = "pdflatex"

        latex = [engine, "-interaction=nonstopmode", "-shell-escape", "-synctex=1"]
        biber = ["biber"]

        if self.aux_directory:
            # No supported engine supports --aux-directory, use --output-directory
            # and move final documents later.
            biber.append(f"--output-directory={self.aux_directory}")
            latex.append(f"--output-directory={self.aux_directory}")

        if self.job_name and self.job_name != self.base_name:
            latex.append(f"--jobname={self.job_name}")

        for option in self.options:
            latex.append(option)

        latex.append(self.tex_name)

        # Initial pdflatex run may fail, if required diretories are not yet present
        self.abort_on_error = False
        yield (latex, f"running {engine}...")

        # Create required directories and retry
        while matches := FILE_WRITE_ERROR_REGEX.findall(self.out):
            for path, _ in matches:
                abspath = os.path.join(self.aux_directory_full, path)
                os.makedirs(abspath, exist_ok=True)
                logger.debug(f"Created directory {abspath}")

            yield (latex, f"running {engine}...")

        self.abort_on_error = True

        # Check for citations
        # We need to run pdflatex twice after bibtex
        run_bibtex = False
        use_bibtex = True
        bibtex = None
        if CITATIONS_REGEX.search(self.out):
            run_bibtex = True
            # are we using biblatex?
            m = BIBLATEX_REGEX.search(self.out)
            if m:
                bibtex = m.group(1).lower()
                if bibtex == "biber":
                    use_bibtex = False
        # check for natbib as well
        elif "Package natbib Warning: There were undefined citations" in self.out:
            run_bibtex = True

        if run_bibtex:
            if use_bibtex:
                # set-up bibtex cmd line
                if bibtex is None:
                    bibtex = [self.builder_settings.get("bibtex", "bibtex")]
                elif isinstance(bibtex, str):
                    bibtex = [bibtex]
                bibtex.append(self.job_name)
                yield (self.command(bibtex, cwd=self.aux_directory_full), f"running {bibtex[0]}...")
            else:
                yield (biber + [self.job_name], "running biber...")

            for i in range(2):
                yield (latex, f"running {engine}...")

        # Check for changed labels
        # Do this at the end, so if there are also citations to resolve,
        # we may save one pdflatex run
        if "Rerun to get cross-references right." in self.out:
            yield (latex, f"running {engine}...")
