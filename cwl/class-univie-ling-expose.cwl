# univie-ling-expose class
# Matthew Bertucci 2024/06/28 for v.2.6

#include:class-scrartcl
#include:array
#include:translator
#include:fontenc
# loads T1 option of fontenc
#include:mathptmx
#include:uarial
#include:sourcecodepro
#include:url
#include:geometry
#include:setspace
#include:scrlayer-scrpage
#include:microtype
#include:csquotes
#include:graphicx
#include:datetime2
#include:covington
#include:caption
#include:ragged2e
#include:biblatex
# loads style=univie-ling option of biblatex
#include:varioref
#include:prettyref
#include:isodate

#keyvals:\documentclass/univie-ling-expose#c
all#true,false
biblatex#true,false
apa#true,false
caption#true,false
ref#true,false
covington#true,false
draftmark=#true,false,firstpage
microtype#true,false
polyglossia#true,false
fonts=#ps,otf,none
fontenc={%<enc1,enc2,...%>}
#endkeyvals

#ifOption:apa
## loads style=apa and natbib=true options of biblatex
# from style=apa option of biblatex
#keyvals:\usepackage/biblatex#c,\ExecuteBibliographyOptions#c
apamaxprtauth=%<number%>
#endkeyvals
# from apa.bbx
\foreverunspace#*
\printtexte{text}#*
\printtexte[format]{text}#*
\maxprtauth#*
\apanum{num}#*
\mkdaterangeapalong{datetype}#*
\mkdaterangeapalongextra{datetype}#*
\begrelateddelimcommenton#*
\begrelateddelimreviewof#*
\begrelateddelimreprintfrom#*
\urldatecomma#*
# from apa.cbx
\apashortdash#*
\citeresetapa#*
\fullcitebib[prenote][postnote]{bibid}#*C
\fullcitebib[postnote]{bibid}#*C
\fullcitebib{bibid}#*C
\nptextcite[prenote][postnote]{bibid}#C
\nptextcite[postnote]{bibid}#C
\nptextcite{bibid}#C
\nptextcites{bibid}{bibid}#*C
\nptextcites(pre){bibid}{bibid}#*C
\nptextcites(pre)(post){bibid}{bibid}#*C
\nptextcites(pre)(post)[pre]{bibid}[pre]{bibid}#*C
\nptextcites[pre]{bibid}[pre]{bibid}#*C
\nptextcites[pre][post]{bibid}[pre][post]{bibid}#*C
\nptextcites(pre)(post)[pre][post]{bibid}[pre][post]{bibid}#*C

# from natbib=true option of biblatex
# from blx-natbib.def
\citet[prenote][postnote]{bibid}#C
\citet[postnote]{bibid}#C
\citet{bibid}#C
\citet*[prenote][postnote]{bibid}#C
\citet*[postnote]{bibid}#C
\citet*{bibid}#C
\citep[prenote][postnote]{bibid}#C
\citep[postnote]{bibid}#C
\citep{bibid}#C
\citep*[prenote][postnote]{bibid}#C
\citep*[postnote]{bibid}#C
\citep*{bibid}#C
\citealt[prenote][postnote]{bibid}#C
\citealt[postnote]{bibid}#C
\citealt{bibid}#C
\citealt*[prenote][postnote]{bibid}#C
\citealt*[postnote]{bibid}#C
\citealt*{bibid}#C
\citealp[prenote][postnote]{bibid}#C
\citealp[postnote]{bibid}#C
\citealp{bibid}#C
\citealp*[prenote][postnote]{bibid}#C
\citealp*[postnote]{bibid}#C
\citealp*{bibid}#C
\citeauthor[prenote][postnote]{bibid}#C
\citeauthor[postnote]{bibid}#C
\citeauthor{bibid}#C
\citeauthor*[prenote][postnote]{bibid}#C
\citeauthor*[postnote]{bibid}#C
\citeauthor*{bibid}#C
\citeyearpar[prenote][postnote]{bibid}#C
\citeyearpar[postnote]{bibid}#C
\citeyearpar{bibid}#C
\Citet[prenote][postnote]{bibid}#C
\Citet[postnote]{bibid}#C
\Citet{bibid}#C
\Citet*[prenote][postnote]{bibid}#C
\Citet*[postnote]{bibid}#C
\Citet*{bibid}#C
\Citep[prenote][postnote]{bibid}#C
\Citep[postnote]{bibid}#C
\Citep{bibid}#C
\Citep*[prenote][postnote]{bibid}#C
\Citep*[postnote]{bibid}#C
\Citep*{bibid}#C
\Citealt[prenote][postnote]{bibid}#C
\Citealt[postnote]{bibid}#C
\Citealt{bibid}#C
\Citealt*[prenote][postnote]{bibid}#C
\Citealt*[postnote]{bibid}#C
\Citealt*{bibid}#C
\Citealp[prenote][postnote]{bibid}#C
\Citealp[postnote]{bibid}#C
\Citealp{bibid}#C
\Citealp*[prenote][postnote]{bibid}#C
\Citealp*[postnote]{bibid}#C
\Citealp*{bibid}#C
\citefullauthor[prenote][postnote]{bibid}#C
\citefullauthor[postnote]{bibid}#C
\citefullauthor{bibid}#C
\Citefullauthor[prenote][postnote]{bibid}#C
\Citefullauthor[postnote]{bibid}#C
\Citefullauthor{bibid}#C
\citetext{text}
\defcitealias{bibid}{alias}
\citetalias{bibid}
\citepalias{bibid}
#endif
#ifOption:apa=true
## loads style=apa and natbib=true options of biblatex
# from style=apa option of biblatex
#keyvals:\usepackage/biblatex#c,\ExecuteBibliographyOptions#c
apamaxprtauth=%<number%>
#endkeyvals
# from apa.bbx
\foreverunspace#*
\printtexte{text}#*
\printtexte[format]{text}#*
\maxprtauth#*
\apanum{num}#*
\mkdaterangeapalong{datetype}#*
\mkdaterangeapalongextra{datetype}#*
\begrelateddelimcommenton#*
\begrelateddelimreviewof#*
\begrelateddelimreprintfrom#*
\urldatecomma#*
# from apa.cbx
\apashortdash#*
\citeresetapa#*
\fullcitebib[prenote][postnote]{bibid}#*C
\fullcitebib[postnote]{bibid}#*C
\fullcitebib{bibid}#*C
\nptextcite[prenote][postnote]{bibid}#C
\nptextcite[postnote]{bibid}#C
\nptextcite{bibid}#C
\nptextcites{bibid}{bibid}#*C
\nptextcites(pre){bibid}{bibid}#*C
\nptextcites(pre)(post){bibid}{bibid}#*C
\nptextcites(pre)(post)[pre]{bibid}[pre]{bibid}#*C
\nptextcites[pre]{bibid}[pre]{bibid}#*C
\nptextcites[pre][post]{bibid}[pre][post]{bibid}#*C
\nptextcites(pre)(post)[pre][post]{bibid}[pre][post]{bibid}#*C

# from natbib=true option of biblatex
# from blx-natbib.def
\citet[prenote][postnote]{bibid}#C
\citet[postnote]{bibid}#C
\citet{bibid}#C
\citet*[prenote][postnote]{bibid}#C
\citet*[postnote]{bibid}#C
\citet*{bibid}#C
\citep[prenote][postnote]{bibid}#C
\citep[postnote]{bibid}#C
\citep{bibid}#C
\citep*[prenote][postnote]{bibid}#C
\citep*[postnote]{bibid}#C
\citep*{bibid}#C
\citealt[prenote][postnote]{bibid}#C
\citealt[postnote]{bibid}#C
\citealt{bibid}#C
\citealt*[prenote][postnote]{bibid}#C
\citealt*[postnote]{bibid}#C
\citealt*{bibid}#C
\citealp[prenote][postnote]{bibid}#C
\citealp[postnote]{bibid}#C
\citealp{bibid}#C
\citealp*[prenote][postnote]{bibid}#C
\citealp*[postnote]{bibid}#C
\citealp*{bibid}#C
\citeauthor[prenote][postnote]{bibid}#C
\citeauthor[postnote]{bibid}#C
\citeauthor{bibid}#C
\citeauthor*[prenote][postnote]{bibid}#C
\citeauthor*[postnote]{bibid}#C
\citeauthor*{bibid}#C
\citeyearpar[prenote][postnote]{bibid}#C
\citeyearpar[postnote]{bibid}#C
\citeyearpar{bibid}#C
\Citet[prenote][postnote]{bibid}#C
\Citet[postnote]{bibid}#C
\Citet{bibid}#C
\Citet*[prenote][postnote]{bibid}#C
\Citet*[postnote]{bibid}#C
\Citet*{bibid}#C
\Citep[prenote][postnote]{bibid}#C
\Citep[postnote]{bibid}#C
\Citep{bibid}#C
\Citep*[prenote][postnote]{bibid}#C
\Citep*[postnote]{bibid}#C
\Citep*{bibid}#C
\Citealt[prenote][postnote]{bibid}#C
\Citealt[postnote]{bibid}#C
\Citealt{bibid}#C
\Citealt*[prenote][postnote]{bibid}#C
\Citealt*[postnote]{bibid}#C
\Citealt*{bibid}#C
\Citealp[prenote][postnote]{bibid}#C
\Citealp[postnote]{bibid}#C
\Citealp{bibid}#C
\Citealp*[prenote][postnote]{bibid}#C
\Citealp*[postnote]{bibid}#C
\Citealp*{bibid}#C
\citefullauthor[prenote][postnote]{bibid}#C
\citefullauthor[postnote]{bibid}#C
\citefullauthor{bibid}#C
\Citefullauthor[prenote][postnote]{bibid}#C
\Citefullauthor[postnote]{bibid}#C
\Citefullauthor{bibid}#C
\citetext{text}
\defcitealias{bibid}{alias}
\citetalias{bibid}
\citepalias{bibid}
#endif

#ifOption:draftmark
#include:draftwatermark
#endif
#ifOption:draftmark=true
#include:draftwatermark
#endif
#ifOption:draftmark=firstpage
#include:draftwatermark
#endif

#ifOption:polyglossia
#include:polyglossia
#include:fontspec
#endif
#ifOption:polyglossia=true
#include:polyglossia
#include:fontspec
#endif

#ifOption:fonts=otf
#include:fontspec
#endif

\studienkennzahl{degree program code}
\studienrichtung{field of study%text}
\supervisor{name}
\cosupervisor{name}
\advisor{name}
\Expression{text}
\Meaning{text}
\Concept{text}
\weblink{URL}#U
\weblink{URL}[date]#U
\SetURLDate{date}
\urldate{date}

\footnumwidth#*
\lecsemshort#S
\lecsemverb#S
\origtableofcontents#S
\maxfn#*
\urlprefix#*

# from T1 option of fontenc
\DH#n
\dh#n
\dj#n
\DJ#n
\guillemetleft#n
\guillemetright#n
\guillemotleft#*n
\guillemotright#*n
\guilsinglleft#n
\guilsinglright#n
\Hwithstroke#n
\hwithstroke#n
\k{arg}#n
\NG#n
\ng#n
\quotedblbase#n
\quotesinglbase#n
\textogonekcentered{arg}#n
\textquotedbl#n
\th#n
\TH#n

# from style=univie-ling option of biblatex
#keyvals:\usepackage/biblatex#c,\ExecuteBibliographyOptions#c
issueeditor#true,false
#endkeyvals
\mkbibdateunified{arg1}{arg2}{arg3}#*
