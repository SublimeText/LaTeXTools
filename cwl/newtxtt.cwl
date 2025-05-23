# newtxtt package
# Matthew Bertucci 1/13/2022 for v1.051

#include:fontenc
#include:xkeyval

#keyvals:\usepackage/newtxtt#c
scale=%<factor%>
scaled=%<factor%>
nomono
straightquotes
ttdefault
ttzdefault
#endkeyvals

\ttzdefault#*
\ttzfamily
\textttz{text}

# deprecated
\ttz#S

# from T1 option of fontenc
\DH#n
\NG#n
\dj#n
\ng#n
\k{arg}#n
\guillemotleft#*n
\guillemotright#*n
\guilsinglleft#n
\guilsinglright#n
\quotedblbase#n
\quotesinglbase#n
\textquotedbl#n
\DJ#n
\th#n
\TH#n
\dh#n
\Hwithstroke#*n
\hwithstroke#*n
\textogonekcentered{arg}#*n
\guillemetleft#n
\guillemetright#n
