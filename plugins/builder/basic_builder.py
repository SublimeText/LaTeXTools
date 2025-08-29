import os
import re
import sublime
import subprocess
import sys

from ...latextools.utils.external_command import external_command
from ...latextools.utils.external_command import get_texpath
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

    def __init__(self, *args):
        super(BasicBuilder, self).__init__(*args)
        self.name = "Basic Builder"
        self.bibtex = self.builder_settings.get("bibtex", "bibtex")
        self.display_log = self.builder_settings.get("display_log", False)

    def commands(self):
        # Print greeting
        self.display("\n\nBasic Builder: ")

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

        yield (latex, f"running {engine}...")
        self.display("done.\n")
        self.log_output()

        # Create required directories
        while matches := FILE_WRITE_ERROR_REGEX.findall(self.out):
            for path, _ in matches:
                abspath = os.path.join(self.aux_directory_full or self.tex_dir, path)
                os.makedirs(abspath, exist_ok=True)
                logger.debug(f"Created directory {abspath}")

            yield (latex, f"running {engine}...")
            self.display("done.\n")
            self.log_output()

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
                yield (
                    self.run_bibtex(bibtex),
                    f"running {bibtex or 'bibtex'}...",
                )
            else:
                yield (biber + [self.job_name], "running biber...")

            self.display("done.\n")
            self.log_output()

            for i in range(2):
                yield (latex, f"running {engine}...")
                self.display("done.\n")
                self.log_output()

        # Check for changed labels
        # Do this at the end, so if there are also citations to resolve,
        # we may save one pdflatex run
        if "Rerun to get cross-references right." in self.out:
            yield (latex, f"running {engine}...")
            self.display("done.\n")
            self.log_output()

        self.move_assets_to_output()

    def log_output(self):
        if self.display_log:
            self.display("\nCommand results:\n")
            self.display(self.out)
            self.display("\n\n")

    def run_bibtex(self, command=None):
        if command is None:
            command = [self.bibtex]
        elif isinstance(command, str):
            command = [command]

        # to get bibtex to work with the output directory, we change the
        # cwd to the output directory and add the main directory to
        # BIBINPUTS and BSTINPUTS
        env = dict(os.environ)
        cwd = self.tex_dir

        if self.aux_directory:
            # cwd is, at the point, the path to the main tex file
            env["BIBINPUTS"] = cwd + os.pathsep + env.get("BIBINPUTS", "")
            env["BSTINPUTS"] = cwd + os.pathsep + env.get("BSTINPUTS", "")
            # now we modify cwd to be the output directory
            # NOTE this cwd is not reused by any of the other command
            cwd = self.aux_directory_full
        env["PATH"] = get_texpath()

        command.append(self.job_name)
        return external_command(
            command,
            env=env,
            cwd=cwd,
            preexec_fn=os.setsid if sublime.platform() != "windows" else None,
            use_texpath=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
