# attachfile2 package
# Matthew Bertucci 2024/01/20 for v2.12

#include:iftex
#include:keyval
#include:color
#include:infwaerr
#include:ltxcmds
#include:kvoptions
#include:pdftexcmds
#include:pdfescape
#include:hyperref
#include:hycolor

#keyvals:\usepackage/attachfile2#c
draft
final
nofiles
pdftex
luatex
dvips
dvipdfmx
xetex
driverfallback=%<driver%>
#endkeyvals

\attachfile{file}
\attachfile[options%keyvals]{file}
\noattachfile
\noattachfile[options%keyvals]
\notextattachfile{text}
\notextattachfile[options%keyvals]{text}
\textattachfile{file}{text}
\textattachfile[options%keyvals]{file}{text}
\attachfilesetup{options%keyvals}

#keyvals:\usepackage/attachfile2#c,\attachfile,\attachfilesetup,\noattachfile,\notextattachfile,\textattachfile
appearance#true,false
author=%<text%>
color=%<color%>
created=%<PDF date%>
date=%<PDF date%>
description=%<text%>
icon=#Graph,Paperclip,PushPin,Tag
mimetype=%<type/subtype%>
modified=%<PDF date%>
print#true,false
size=%<integer%>
subject=%<text%>
timezone=%<offset%>
zoom#true,false
locked#true,false
scale=%<factor%>
ucfilespec=
annotname=%<name%>
#endkeyvals
