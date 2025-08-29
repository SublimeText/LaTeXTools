from __future__ import annotations
import re

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pdf_builder import CommandGenerator

from .pdf_builder import PdfBuilder

__all__ = ["SimpleBuilder"]


class SimpleBuilder(PdfBuilder):
    """
    SimpleBuilder class

    Just call a bunch of commands in sequence
    Demonstrate basics
    """
    name = "Simple Builder"

    def commands(self) -> CommandGenerator:
        pdflatex = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-shell-escape",
            "-synctex=1",
        ]
        bibtex = ["bibtex"]

        # Regex to look for missing citations
        # This works for plain latex; apparently natbib requires special handling
        # TODO: does it work with biblatex?
        citations_rx = re.compile(r"Warning: Citation `.+' on page \d+ undefined")

        # We have commands in our PATH, and are in the same dir as the master file
        run = 1
        brun = 0
        yield (pdflatex + [self.base_name], f"pdflatex run {run}...")

        # Check for citations
        # Use search, not match: match looks at the beginning of the string
        # We need to run pdflatex twice after bibtex
        if citations_rx.search(self.out):
            brun += 1
            yield (bibtex + [self.base_name], f"bibtex run {brun}...")
            run += 1
            yield (pdflatex + [self.base_name], f"pdflatex run {run}...")
            run += 1
            yield (pdflatex + [self.base_name], f"pdflatex run {run}...")

        # Apparently natbib needs separate processing
        if "Package natbib Warning: There were undefined citations." in self.out:
            brun += 1
            yield (bibtex + [self.base_name], f"bibtex run {brun}...")
            run += 1
            yield (pdflatex + [self.base_name], f"pdflatex run {run}...")
            run += 1
            yield (pdflatex + [self.base_name], f"pdflatex run {run}...")

        # Check for changed labels
        # Do this at the end, so if there are also citations to resolve,
        # we may save one pdflatex run
        if "Rerun to get cross-references right." in self.out:
            run += 1
            yield (pdflatex + [self.base_name], f"pdflatex run {run}...")
