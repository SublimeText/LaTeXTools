# ltjreport class
# Matthew Bertucci 4/11/2022 for v1.8f

#include:luatexja
#include:stfloats

#keyvals:\documentclass/ltjreport#c
a4paper
a5paper
b4paper
b5paper
a4j
a5j
b4j
b5j
a4p
a5p
b4p
b5p
10pt
11pt
12pt
landscape
tombow
tombo
mentuke
tate
oneside
twoside
onecolumn
twocolumn
titlepage
notitlepage
openright
openleft
openany
leqno
fleqn
openbib
mathrmmc
draft
final
ptexmin
disablejfam
#endkeyvals

#ifOption:tombow
\stockheight#*
\stockwidth#*
#endif
#ifOption:tombo
\stockheight#*
\stockwidth#*
#endif
#ifOption:mentuke
\stockheight#*
\stockwidth#*
#endif

\bibname#n
\chapter*{title}#L1
\chapter[short title]{title}#L1
\chapter{title}#L1
\chaptermark{code}#*
\Cjascale
\ifptexmin#*
\if西暦#*
\heisei#*
\postchaptername#*
\postpartname#*
\prechaptername#*
\prepartname#*
\ptexminfalse#*
\ptexmintrue#*
\thechapter#*
\theHchapter#*
\和暦
\西暦
\西暦false#*
\西暦true#*
