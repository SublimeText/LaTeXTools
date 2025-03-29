# ltjspf class
# Matthew Bertucci 2022/06/01 for v20220530.0

#include:luatexja
#include:jslogo
#include:stfloats

#keyvals:\documentclass/ltjspf#c
a3paper
a4paper
a5paper
a6paper
b4paper
b5paper
b6paper
a4j
a5j
b4j
b5j
a4var
b5var
letterpaper
legalpaper
executivepaper
landscape
8pt
9pt
10pt
11pt
12pt
14pt
17pt
20pt
21pt
25pt
30pt
36pt
43pt
12Q
14Q
10ptj
10.5ptj
11ptj
12ptj
nomag
nomag
tombow
tombo
mentuke
oneside
twoside
vartwoside
onecolumn
twocolumn
titlepage
notitlepage
leqno
fleqn
draft
final
mingoth
ptexjis
jis
english
jslogo
nojslogo
#endkeyvals

#ifOption:tombow
\stockheight#L
\stockwidth#L
#endif
#ifOption:tombo
\stockheight#L
\stockwidth#L
#endif
#ifOption:mentuke
\stockheight#L
\stockwidth#L
#endif

\alsoname#*
\AuthorsEmail{email%URL}#U
\bibname
\chaptermark{code}#*
\Cjascale
\eauthor{names}
\email{email%URL}#U
\etitle{text}
\fullwidth#L
\headfont#*
\heisei#*
\HUGE
\ifjisfont#*
\ifmingoth#*
\ifnarrowbaselines#*
\ifptexjis#*
\ifptexmin#*
\if西暦#*
\jisfontfalse#*
\jisfonttrue#*
\jsTocLine#*
\keywords{keywords%text}
\mingothfalse#*
\mingothtrue#*
\narrowbaselines
\narrowbaselinesfalse#*
\narrowbaselinestrue#*
\plainifnotempty#*
\postpartname#*
\postsectionname#*
\prepartname#*
\presectionname#*
\ptexjisfalse#*
\ptexjistrue#*
\ptexminfalse#*
\ptexmintrue#*
\seename#*
\widebaselines
\上小{text}
\和暦
\小{text}
\西暦
\西暦false#*
\西暦true#*