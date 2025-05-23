# testidx package
# Matthew Bertucci 2/22/2022 for v1.2

#include:color
#include:ifxetex
#include:ifluatex

## 2 Package Options ##
#keyvals:\usepackage/testidx#c
ascii
noascii
german
ngerman
nogerman
stripaccents
nostripaccents
sanitize
nosanitize
showmarks
hidemarks
noshowmarks
verbose
noverbose
notestencaps
testencaps
prefix
noprefix
diglyphs
nodiglyphs
#endkeyvals

\testidxGermanOn#*
\testidxGermanOff#*
\testidxStripAccents#*
\testidxNoStripAccents#*
\testidxSanitizeOn#*
\testidxSanitizeOff#*
\testidxshowmarkstrue#*
\testidxshowmarksfalse#*
\iftestidxverbose#*
\testidxverbosetrue#*
\testidxverbosefalse#*
\iftestidxdiglyphs#*
\testidxdiglyphstrue#*
\testidxdiglyphsfalse#*
\iftestidxprefix#*
\testidxprefixtrue#*
\testidxprefixfalse#*

## 3 Basic Commands ##
\testidx
\testidx[blocks]
\tstidxmaxblocks
\tstidxprefixblock{n}
\tstindex{text}

\tstidxmarker#*
\tstidxopenmarker#*
\tstidxclosemarker#*
\tstidxsubmarker#*
\tstidxopensubmarker#*
\tstidxclosesubmarker#*
\tstidxsubsubmarker#*
\tstidxopensubsubmarker#*
\tstidxclosesubsubmarker#*
\tstidxseemarker#*
\tstidxsubseemarker#*
\tstidxsubseesep#*

\tstidxencapi{location}#*
\tstidxencapii{location}#*
\tstidxencapiii{location}#*

\tstidxSetSeeEncap{encap name}
\tstidxSetSeeAlsoEncap{encap name}
\tstidxtext{text}

## 4 Indexing Special Characters ##
\tstidxquote#*
\tstidxactual#*
\tstidxlevel#*
\tstidxencap#*
\tstidxopenrange#*
\tstidxcloserange#*

# not in main documentation
\testidxverbosefmt{arg1}#S
\tstidxapp[opt]{arg1}#S
\tstidxappfmt{arg1}#S
\tstidxappopt[opt]{arg1}{arg2}#S
\tstidxappoptfmt{arg1}#S
\tstidxappopt{arg1}{arg2}#S
\tstidxappopt{arg1}{arg2}{arg3}#S
\tstidxapp{arg1}#S
\tstidxapp{arg1}{arg2}#S
\tstidxartbook[opt]{arg1}{arg2}#S
\tstidxartbook{arg1}{arg2}#S
\tstidxartbook{arg1}{arg2}{arg3}#S
\tstidxartfilm[opt]{arg1}{arg2}#S
\tstidxartfilm{arg1}{arg2}#S
\tstidxartfilm{arg1}{arg2}{arg3}#S
\tstidxartphrase{arg1}{arg2}{arg3}#S
\tstidxartplace{arg1}{arg2}{arg3}#S
\tstidxbook[opt]{arg1}#S
\tstidxbookfmt{arg1}#S
\tstidxbook{arg1}#S
\tstidxbook{arg1}{arg2}#S
\tstidxcloseapp[opt]{arg1}#S
\tstidxcloseappopt[opt]{arg1}{arg2}#S
\tstidxcloseappopt{arg1}{arg2}#S
\tstidxcloseappopt{arg1}{arg2}{arg3}#S
\tstidxcloseapp{arg1}#S
\tstidxcloseapp{arg1}{arg2}#S
\tstidxcloseartbook[opt]{arg1}{arg2}#S
\tstidxcloseartbook{arg1}{arg2}#S
\tstidxcloseartbook{arg1}{arg2}{arg3}#S
\tstidxcloseartphrase{arg1}{arg2}{arg3}#S
\tstidxclosebook[opt]{arg1}#S
\tstidxclosebook{arg1}#S
\tstidxclosebook{arg1}{arg2}#S
\tstidxclosecs[opt]{arg1}#S
\tstidxclosecsn[opt]{arg1}#S
\tstidxclosecsn{arg1}#S
\tstidxclosecsn{arg1}{arg2}#S
\tstidxclosecs{arg1}#S
\tstidxclosecs{arg1}{arg2}#S
\tstidxcloseenv[opt]{arg1}#S
\tstidxcloseenv{arg1}#S
\tstidxcloseenv{arg1}{arg2}#S
\tstidxclosefilm[opt]{arg1}#S
\tstidxclosefilm{arg1}#S
\tstidxclosefilm{arg1}{arg2}#S
\tstidxcloseperson{arg1}{arg2}{arg3}#S
\tstidxclosephrase{arg1}{arg2}#S
\tstidxclosesty[opt]{arg1}#S
\tstidxclosestyopt[opt]{arg1}{arg2}#S
\tstidxclosestyopt{arg1}{arg2}#S
\tstidxclosestyopt{arg1}{arg2}{arg3}#S
\tstidxclosesty{arg1}#S
\tstidxclosesty{arg1}{arg2}#S
\tstidxclosesym{arg1}{arg2}#S
\tstidxcloseutfphrase{arg1}{arg2}{arg3}#S
\tstidxcloseutf{arg1}{arg2}{arg3}{arg4}#S
\tstidxcloseword{arg1}{arg2}#S
\tstidxcs[opt]{arg1}#S
\tstidxcsfmt{arg1}#S
\tstidxcs{arg1}#S
\tstidxcs{arg1}{arg2}#S
\tstidxdash#S
\tstidxdefblocksep#S
\tstidxencapcsn[opt]{arg1}#S
\tstidxencapcsn{arg1}#S
\tstidxencapcsn{arg1}{arg2}#S
\tstidxencaptext{arg1}{arg2}#S
\tstidxensuretext{arg1}#S
\tstidxenv[opt]{arg1}#S
\tstidxenvfmt{arg1}#S
\tstidxenv{arg1}#S
\tstidxenv{arg1}{arg2}#S
\tstidxfilm[opt]{arg1}#S
\tstidxfilmfmt{arg1}#S
\tstidxfilm{arg1}#S
\tstidxfilm{arg1}{arg2}#S
\tstidxfmtclosepost{arg1}{arg2}{arg3}#S
\tstidxfmtclosepre{arg1}{arg2}{arg3}#S
\tstidxfmtopenpost{arg1}{arg2}{arg3}#S
\tstidxfmtopenpre{arg1}{arg2}{arg3}#S
\tstidxfmtpost{arg1}{arg2}{arg3}#S
\tstidxfmtpre{arg1}{arg2}{arg3}#S
\tstidxfootnote#S
\tstidxgphword{arg1}{arg2}#S
\tstidxindexmarkerprefix#S
\tstidxindexmarker{arg1}#S
\tstidxmath[opt]{arg1}#S
\tstidxmathsym[opt]{arg1}#S
\tstidxmathsymprefix#S
\tstidxmathsym{arg1}#S
\tstidxmathsym{arg1}{arg2}#S
\tstidxmath{arg1}#S
\tstidxmath{arg1}{arg2}#S
\tstidxnewblock#S
\tstidxnumber[opt]{arg1}#S
\tstidxnumber{arg1}#S
\tstidxnumber{arg1}{arg2}#S
\tstidxopenapp[opt]{arg1}#S
\tstidxopenappopt[opt]{arg1}{arg2}#S
\tstidxopenappopt{arg1}{arg2}#S
\tstidxopenappopt{arg1}{arg2}{arg3}#S
\tstidxopenapp{arg1}#S
\tstidxopenapp{arg1}{arg2}#S
\tstidxopenartbook[opt]{arg1}{arg2}#S
\tstidxopenartbook{arg1}{arg2}#S
\tstidxopenartbook{arg1}{arg2}{arg3}#S
\tstidxopenartphrase{arg1}{arg2}{arg3}#S
\tstidxopenbook[opt]{arg1}#S
\tstidxopenbook{arg1}#S
\tstidxopenbook{arg1}{arg2}#S
\tstidxopencs[opt]{arg1}#S
\tstidxopencsn[opt]{arg1}#S
\tstidxopencsn{arg1}#S
\tstidxopencsn{arg1}{arg2}#S
\tstidxopencs{arg1}#S
\tstidxopencs{arg1}{arg2}#S
\tstidxopenenv[opt]{arg1}#S
\tstidxopenenv{arg1}#S
\tstidxopenenv{arg1}{arg2}#S
\tstidxopenfilm[opt]{arg1}#S
\tstidxopenfilm{arg1}#S
\tstidxopenfilm{arg1}{arg2}#S
\tstidxopenperson{arg1}{arg2}{arg3}#S
\tstidxopenphrase{arg1}{arg2}#S
\tstidxopensty[opt]{arg1}#S
\tstidxopenstyopt[opt]{arg1}{arg2}#S
\tstidxopenstyopt{arg1}{arg2}#S
\tstidxopenstyopt{arg1}{arg2}{arg3}#S
\tstidxopensty{arg1}#S
\tstidxopensty{arg1}{arg2}#S
\tstidxopensym{arg1}{arg2}#S
\tstidxopenutfphrase{arg1}{arg2}{arg3}#S
\tstidxopenutf{arg1}{arg2}{arg3}{arg4}#S
\tstidxopenword{arg1}{arg2}#S
\tstidxperson{arg1}{arg2}{arg3}#S
\tstidxphrasepl{arg1}#S
\tstidxphrase{arg1}{arg2}#S
\tstidxplace{arg1}{arg2}#S
\tstidxprocessasciisort#S
\tstidxprocessasciisortnostrip{arg1}{arg2}#S
\tstidxprocessasciisortstrip{arg1}{arg2}#S
\tstidxprocessascii{arg1}{arg2}#S
\tstidxprocessutf#S
\tstidxprocessutfnosanitize{arg1}{arg2}#S
\tstidxprocessutfsanitize{arg1}{arg2}#S
\tstidxqt{arg1}#S
\tstidxseeref{arg1}{arg2}{arg3}#S
\tstidxsortumlaut#S
\tstidxsortumlautstrip#S
\tstidxsty[opt]{arg1}#S
\tstidxstyfmt{arg1}#S
\tstidxstyopt[opt]{arg1}{arg2}#S
\tstidxstyoptfmt{arg1}#S
\tstidxstyopt{arg1}{arg2}#S
\tstidxstyopt{arg1}{arg2}{arg3}#S
\tstidxsty{arg1}#S
\tstidxsty{arg1}{arg2}#S
\tstidxsubseeref{arg1}{arg2}{arg3}{arg4}#S
\tstidxsubutf{arg1}{arg2}{arg3}{arg4}#S
\tstidxsubword{arg1}{arg2}{arg3}#S
\tstidxsym{arg1}{arg2}#S
\tstidxumlaut#S
\tstidxutf#S
\tstidxutfcloseperson{arg1}{arg2}{arg3}#S
\tstidxutfclosepost{arg1}{arg2}{arg3}{arg4}#S
\tstidxutfclosepre{arg1}{arg2}{arg3}{arg4}#S
\tstidxutfopenperson{arg1}{arg2}{arg3}#S
\tstidxutfopenpost{arg1}{arg2}{arg3}{arg4}#S
\tstidxutfopenpre{arg1}{arg2}{arg3}{arg4}#S
\tstidxutfperson{arg1}{arg2}{arg3}#S
\tstidxutfphrase{arg1}{arg2}#S
\tstidxutfplace{arg1}{arg2}#S
\tstidxutfpost{arg1}{arg2}#S
\tstidxutfpre{arg1}{arg2}#S
\tstidxutfsubclosepost{arg1}{arg2}{arg3}{arg4}{arg5}{arg6}#S
\tstidxutfsubclosepre{arg1}{arg2}{arg3}{arg4}{arg5}{arg6}#S
\tstidxutfsubopenpost{arg1}{arg2}{arg3}{arg4}{arg5}{arg6}#S
\tstidxutfsubopenpre{arg1}{arg2}{arg3}{arg4}{arg5}{arg6}#S
\tstidxutfsubpost{arg1}{arg2}{arg3}{arg4}#S
\tstidxutfsubpre{arg1}{arg2}{arg3}{arg4}{arg5}{arg6}#S
\tstidxutfword{arg1}{arg2}#S
\tstidxwordpl{arg1}#S
\tstidxword{arg1}{arg2}#S
\tstindexclosepost{arg1}{arg2}#S
\tstindexclosepre{arg1}{arg2}#S
\tstindexopenpost{arg1}{arg2}#S
\tstindexopenpre{arg1}{arg2}#S
\tstindexpost{arg1}{arg2}#S
\tstindexpre{arg1}{arg2}#S
\tstindexsee{arg1}{arg2}#S
\tstindexstysee{arg1}{arg2}{arg3}#S
\tstindexsubsee{arg1}{arg2}#S
\tstindexutfsee{arg1}{arg2}#S
\tstsubindexclosepost{arg1}{arg2}#S
\tstsubindexclosepre{arg1}{arg2}#S
\tstsubindexopenpost{arg1}{arg2}#S
\tstsubindexopenpre{arg1}{arg2}#S
\tstsubindexpost{arg1}{arg2}#S
\tstsubindexpre{arg1}{arg2}#S
\tstsubsubindexclosepost{arg1}{arg2}#S
\tstsubsubindexclosepre{arg1}{arg2}#S
\tstsubsubindexopenpost{arg1}{arg2}#S
\tstsubsubindexopenpre{arg1}{arg2}#S
\tstsubsubindexpost{arg1}{arg2}#S
\tstsubsubindexpre{arg1}{arg2}#S