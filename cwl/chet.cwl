# chet package
# Matthew Bertucci 2022/07/02 for v2.2

#include:kvoptions
#include:xspace
#include:datetime
#include:amsmath
#include:caption
#include:tocloft
#include:cite
#include:collref
#include:color
#include:microtype
#include:manyfoot
#include:footmisc
#include:filecontents
#include:geometry
#include:hyperref

#keyvals:\usepackage/chet#c
macrosonly#true,false
#endkeyvals

\draftmode
\titlemath{math}#m
\email{email%URL}#U
\emailV{email%URL}#U
\emails{emails%URL}#U
\newsec{title}#L2
\newsec{title}[label]#L2
\subsec{title}#L3
\subsec{title}[label]#L3
\subsubsec{title}#L4
\subsubsec{title}[label]#L4
\eqn{math%formula}
\eqn{math%formula}[label]#l
\eqna{math%formula}
\eqna{math%formula}[label]#l
\twoseqn{math1%formula}{math2%formula}
\twoseqn{math1%formula}{math2%formula}[label2%labeldef]#l
\twoseqn{math1%formula}{math2%formula}[label2%labeldef][overall-label%labeldef]#l
\twoseqn{math1%formula}[label1%labeldef]{math2%formula}#l
\twoseqn{math1%formula}[label1%labeldef]{math2%formula}[label2%labeldef]#l
\twoseqn{math1%formula}[label1%labeldef]{math2%formula}[label2%labeldef][overall-label%labeldef]#l
\threeseqn{math1%formula}{math2%formula}{math3%formula}
\threeseqn{math1%formula}{math2%formula}{math3%formula}[label3%labeldef]#l
\threeseqn{math1%formula}{math2%formula}[label2%labeldef]{math3%formula}#l
\threeseqn{math1%formula}[label1%labeldef]{math2%formula}{math3%formula}#l
\threeseqn{math1%formula}[label1%labeldef]{math2%formula}[label2%labeldef]{math3%formula}[label3%labeldef]#l
\threeseqn{math1%formula}[label1%labeldef]{math2%formula}[label2%labeldef]{math3%formula}[label3%labeldef][overall-label%labeldef]#l
\fourseqn{math1%formula}{math2%formula}{math3%formula}{math4%formula}
\fourseqn{math1%formula}{math2%formula}{math3%formula}{math4%formula}[label4%labeldef]#l
\fourseqn{math1%formula}{math2%formula}{math3%formula}[label3%labeldef]{math4%formula}#l
\fourseqn{math1%formula}{math2%formula}[label2%labeldef]{math3%formula}{math4%formula}#l
\fourseqn{math1%formula}[label1%labeldef]{math2%formula}{math3%formula}{math4%formula}#l
\fourseqn{math1%formula}[label1%labeldef]{math2%formula}[label2%labeldef]{math3%formula}[label3%labeldef]{math4%formula}[label4%labeldef]#l
\fourseqn{math1%formula}[label1%labeldef]{math2%formula}[label2%labeldef]{math3%formula}[label3%labeldef]{math4%formula}[label4%labeldef][overall-label%labeldef]#l
\rcite{bibid}#C
\rcite[add. text]{bibid}#C
\toc
\foot{text}
\foot[number]{text}
\ack{acknowledgments%text}
\begin{acknowledgments}#*
\end{acknowledgments}#*
\begin{appendices}
\end{appendices}
\appendices#*
\preprint{preprint}
\affiliation{affiliation%text}
\abstract{text}
\mytitlefont#*
\rcitedraft{bibid}#*C
\showkeyslabelformat{text}#*

\footinsE#S
\thefootnoteE#S
\FootnoteE{marker}{text}#S
\FootnotemarkE{marker}#S
\FootnotetextE{marker}{text}#S
\footnoteE{text}#S
\footnoteE[number]{text}#S
\footnotemarkE#S
\footnotemarkE[number]#S
\footnotetextE{text}#S
\footnotetextE[number]{text}#S
\footinsEE#S
\thefootnoteEE#S
\FootnoteEE{marker}{text}#S
\FootnotemarkEE{marker}#S
\FootnotetextEE{marker}{text}#S
\footnoteEE{text}#S
\footnoteEE[number]{text}#S
\footnotemarkEE#S
\footnotemarkEE[number]#S
\footnotetextEE{text}#S
\footnotetextEE[number]{text}#S
\footinsEEE#S
\thefootnoteEEE#S
\FootnoteEEE{marker}{text}#S
\FootnotemarkEEE{marker}#S
\FootnotetextEEE{marker}{text}#S
\footnoteEEE{text}#S
\footnoteEEE[number]{text}#S
\footnotemarkEEE#S
\footnotemarkEEE[number]#S
\footnotetextEEE{text}#S
\footnotetextEEE[number]{text}#S