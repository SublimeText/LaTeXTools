# oblivoir-xl class
# Matthew Bertucci 2023/03/09 for v3.2.1

#include:class-memoir
#include:ifluatex
#include:ifxetex
#include:luatexko
## uncomment following line for xetex
## #include:xetexko
#include:memhangul-x
#include:hyperref
#include:ob-toclof
#include:ob-koreanappendix

# oblivoir-xl not loaded on its own, options go to oblivoir
#keyvals:\documentclass/oblivoir#c
10.5pt
amsmath
arabicfront
bookmark
chapter
faht=##L
fawd=##L
figtabcapt
footnote
gremph
hangulpagestyle
hcr
itemph
kosection
latinquote
lwarp
lwarplanguage=%<language%>
lwarpoption={%<lwarp option%>}
lyxhyper
manualfontspec
mathdisp
microtype
moreverb
nanum
nobookmarks
nohyperref
nokorean
nonfrench
nounfonts
nowinname
obspace
oldhangul
openright
polyglossia
babelhangul
babelvacant
preload={%<package1,package2,...%>}
preloadoption={%<package options%>}
quotespacing
subfigure
tocentry
twoside
unfonts
usedotemph
uset1font
# options passed to memoir class
10pt
11pt
12pt
14pt
17pt
20pt
25pt
30pt
36pt
48pt
60pt
9pt
a3paper
a4paper
a5paper
a6paper
article
b3paper
b4paper
b5paper
b6paper
broadsheetpaper
crownvopaper
dbillpaper
demyvopaper
draft
ebook
executivepaper
extrafontsizes
final
fleqn
foolscapvopaper
fullptlayout
imperialvopaper
landscape
largecrownvopaper
largepostvopaper
ledgerpaper
legalpaper
leqno
letterpaper
mcrownvopaper
mdemyvopaper
mediumvopaper
mlargecrownvopaper
ms
msmallroyalvopaper
oldfontcommands
oldpaper
onecolumn
oneside
openany
openbib
openleft
postvopaper
pottvopaper
royalvopaper
showtrims
smalldemyvopaper
smallroyalvopaper
statementpaper
superroyalvopaper
twocolumn
#endkeyvals

\AppendixTitle
\AppendixTitleToToc
\appref{label}#r
\AttachAppendixTitleToSecnum
\oblivoirchapterstyle{style name}

\bookmarkpkgfalse#*
\bookmarkpkgtrue#*
\CallHyperref#*
\DEFAULTskips#*
\ensp#*
\hyperrefwithlyxfalse#*
\hyperrefwithlyxtrue#*
\ifbookmarkpkg#*
\ifhyperrefwithlyx#*
\ifkosection#*
\ifLwarp#*
\ifnobookmarks#*
\ifnokorean#*
\ifopenrightdoc#*
\ifPRELOAD#*
\iftwosidedoc#*
\kosectionfalse#*
\kosectiontrue#*
\LWARPlan#*
\MarkDocTitle#*
\memucshangulskips#*
\memucsinterwordchapterskip#*
\memucsinterwordskip#*
\nobookmarksfalse#*
\nobookmarkstrue#*
\nokoreanfalse#*
\nokoreantrue#*
\openrightdocfalse#*
\openrightdoctrue#*
\PRELOADfalse#*
\PRELOADstr#*
\PRELOADtrue#*
\twosidedocfalse#*
\twosidedoctrue#*
