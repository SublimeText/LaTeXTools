import sublime
import sublime_plugin

## return latex completions after \
# The completions are sorted by categories sich as cite, ref, section,
# unnumbered section, list, text style, text size, paragraph, math,
# insert, formatting, tocs and some other functions
class LatexCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):

        # only trigger within text.tex scope
        if not view.match_selector(locations[0], "text.tex"):
            return []

        # only continue if curser after '\''
        pt = locations[0] - len(prefix) - 1
        ch = view.substr(sublime.Region(pt, pt + 1))
        if ch != '\\':
            return []

        ## return list for 'string.other.math' (not implemented)
        if view.match_selector(locations[0], "string.other.math"):
            # return nothing for now
            return []
            return ([
                # greek
                ("greek\talpha", "alpha"),
                ("greek\tbeta", "beta")
            ], sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        ## return list for 'text.tex'
        return ([
            # cite
            ("cite\t(author year)", "citep{$1}"),
            ("cite\tauthor (year)", "citet{$1}"),
            ("cite\tauthor year", "citealp{$1}"),
            ("cite\t(year)", "citeyearpar{$1}"),
            ("cite\tyear", "citeyear{$1}"),
            ("cite\tauthor", "citeauthor{$1}"),
            ("cite\tnumeric", "cite{$1}"),
            ("cite\tnot cited", "nocite{$1}"),
            # label & cross-references
            ("label\tadd label", "label{$1}"),
            ("ref\tcross-reference: x", "ref{$1}"),
            ("ref\tcross-reference: page", "pageref{$1}"),
            ("ref\tcross-reference: x on page y", "ref{$1} on page \pageref{$1}"),
            # sectioning
            ("section\tPART I", "part{$1}\n$0"),
            ("section\tCHAPTER 1", "chapter{$1}\n$0"),
            ("section\t1 Section", "section{$1}\n$0"),
            ("section\t1.1 Subsection", "subsection{$1}\n$0"),
            ("section\t1.1.1 Subsubsection", "subsubsection{$1}\n$0"),
            ("section\tparagraph", "paragraph{$1}\n$0"),
            ("section\tsubparagraph", "subparagraph{$1}\n$0"),
            ("unnumbered section\tPART*", "part*{$1}\n$0"),
            ("unnumbered section\tCHAPTER*", "chapter*{$1}\n$0"),
            ("unnumbered section\tSection*", "section*{$1}\n$0"),
            ("unnumbered section\tSubsection*", "subsection*{$1}\n$0"),
            ("unnumbered section\tSubsubsection*", "subsubsection*{$1}\n$0"),
            ("unnumbered section\tparagraph*", "paragraph*{$1}\n$0"),
            ("unnumbered section\tsubparagraph*", "subparagraph*{$1}\n$0"),
            # lists
            ("list\tnumbered list", "begin{enumerate}\n\item $1\n\end{enumerate}\n$0"),
            ("list\tbulleted list", "begin{itemize}\n\item $1\n\end{itemize}\n$0"),
            ("list\tdescription list", "begin{description}\n\item [{${1:name}}] $2\n\end{description}\n$0"),
            # text style
            ("text style\temphasize", "emph{$1}$0"),
            ("text style\tbold", "textbf{$1}$0"),
            ("text style\titalic", "textit{$1}$0"),
            ("text style\tunderline", "underline{$1}$0"),
            ("text style\tfamily: sans serif", "textsf{$1}$0"),
            ("text style\tfamily: typewriter", "texttt{$1}$0"),
            ("text style\tcolor", "textcolor{${1:black}}{$2}$0"),
            # text size
            ("text size\ttiny", "tiny{$1}$0"),
            ("text size\tsmall", "small{$1}$0"),
            ("text size\tnormal", "normal{$1}$0"),
            ("text size\tlarge", "large{$1}$0"),
            ("text size\thuge", "huge{$1}$0"),
            # paragraph setting
            ("paragraph\tline spacing: 1", "begin{singlespace}\n$1\n\\end{singlespace}\n$0"),
            ("paragraph\tline spacing: 1.5", "begin{onehalfspace}\n$1\n\\end{onehalfspace}\n$0"),
            ("paragraph\tline spacing: 2", "begin{doublespace}\n$1\n\\end{doublespace}\n$0"),
            ("paragraph\tline spacing: custom", "begin{spacing}{${1:1.25}}\n$2\n\\end{spacing}\n$0"),
            ("paragraph\tno indent", "noindent "),
            ("paragraph\talignment: left", "begin{flushleft}\n$1\n\par\end{flushleft}\n$0"),
            ("paragraph\talignment: center", "begin{center}\n$1\n\par\end{center}\n$0"),
            ("paragraph\talignment: right", "begin{flushright}\n$1\n\par\end{flushright}\n$0"),
            # math
            ("math\tdisplay formula", "[\n$1\n\\]\n$0"),
            ("math\tnumbered formula", "begin{equation}\n$1\n\end{equation}\n$0"),
            # insert floats
            ("float\tfigure", "begin{figure}\n\caption{$1}\n$2\n\end{figure}\n$0"),
            ("float\ttable", "begin{table}\n\caption{$1}\n$2\n\end{table}\n$0"),
            ("float\talgorithm", "begin{algorithm}\n\caption{$1}\n$2\n\end{algorithm}\n$0"),
            # formatting
            ("formatting\tnew page", "newpage{}"),
            ("formatting\tpage break", "pagebreak{}"),
            ("formatting\tvertical space", "vspace{${1:0.5in}}$0"),
            ("formatting\tbig skip", "bigskip"),
            ("formatting\tmed skip", "medskip"),
            ("formatting\tsmall skip", "smallskip"),
            ("formatting\tpackage", "usepackage"),
            # tocs
            ("toc\ttable of contents", "tableofcontents{}\n"),
            ("toc\tlist of figures", "listoffigures\n"),
            ("toc\tlist of tables", "listoftables\n"),
            # other stuff
            ("footnote\tinsert footnote", "footnote{$1}$0"),
            ("comment\tinsert comment", "begin{comment}\n$1\n\end{comment}\n$0"),
            ("graphics\tinsert figure", "includegraphics[width=${1:1}]{$2}\n$0"),
            ("url\tinsert url", "url{$1}$0"),
            ("bibliograph\tinsert bibliograph", "bibliographystyle{${1:plainnat}}\n\\bibliography{${2:filepath}}\n$0")
        ], sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
