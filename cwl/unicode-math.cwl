# unicode-math package
# rend3r, 6 Sep 2020
# muzimuzhi, 7 Sep 2020
# Matthew Bertucci 13 Aug 2023 for v0.8r

# The 2946 math symbol commands listed in
#     https://github.com/wspr/unicode-math/blob/master/unicode-math-table.tex
# and documented in `texdoc unimath-symbols` are not recorded. Perhaps those
# commonly used and not yet recorded in latex-document.cwl and amssymb.cwl can 
# be added.

#include:l3keys2e
#include:fontspec
#include:fix-cm
#include:amsmath

\unimathsetup{options%keyvals}
\setmathfont{font}
\setmathfont[font features]{font}#*
\setmathfont{font}[font features%keyvals]
\setmathfont[font features]{font}[font features%keyvals]#*
\setmathfontface{cmd}{font}#d
\setmathfontface{cmd}[font features]{font}#*d
\setmathfontface{cmd}{font}[font features%keyvals]#d
\setmathfontface{cmd}[font features]{font}[font features%keyvals]#*d
\setoperatorfont{cmd}
\NewNegationCommand{symbol or cmd%cmd}{definition}#*d
\RenewNegationCommand{symbol or cmd%cmd}{definition}#*

#keyvals:\unimathsetup#c,\setmathfont#c,\setmathfontface#c,\usepackage/unicode-math#c
normal-style=#ISO,TeX,french,upright,literal
math-style=#ISO,TeX,french,upright,literal
bold-style=#ISO,TeX,upright,literal
sans-style=#italic,upright,literal
nabla=#italic,upright,literal
partial=#italic,upright,literal
colon=#TeX,literal
slash-delimiter=#ascii,frac,div
active-frac=#small,normalsize
mathrm=#text,sym
mathup=#text,sym
mathit=#text,sym
mathsf=#text,sym
mathbf=#text,sym
mathtt=#text,sym
#endkeyvals

#keyvals:\unimathsetup#c,\usepackage/unicode-math#c
trace=#on,debug,off
warnings-off={%<warning list%>}
#endkeyvals

#keyvals:\setmathfont#c,\setmathfontface#c
range=%<unicode range%>
script-font=%<font name%>
sscript-font=%<font name%>
script-features={%<features%>}
sscript-features={%<features%>}
version=%<version name%>
# and all the keys inherited from fontspec
#endkeyvals

\symnormal{text%plain}#*m
\symliteral{text%plain}#*m
\symup{text%plain}#*m
\symrm{text%plain}#*m
\symit{text%plain}#*m
\symbf{text%plain}#*m
\symsf{text%plain}#*m
\symtt{text%plain}#*m
\symbb{text%plain}#*m
\symbbit{text%plain}#*m
\symcal{text%plain}#*m
\symscr{text%plain}#*m
\symfrak{text%plain}#*m
\symsfup{text%plain}#*m
\symsfit{text%plain}#*m
\symbfsf{text%plain}#*m
\symbfup{text%plain}#*m
\symbfit{text%plain}#*m
\symbfcal{text%plain}#*m
\symbfscr{text%plain}#*m
\symbffrak{text%plain}#*m
\symbfsfup{text%plain}#*m
\symbfsfit{text%plain}#*m
\mathtextrm{text%plain}#*m
\mathtextbf{text%plain}#*m
\mathtextit{text%plain}#*m
\mathtextsf{text%plain}#*m
\mathtexttt{text%plain}#*m
\mathup{text%plain}#*m
\mathbb{text%plain}#m
\mathbbit{text%plain}#*m
\mathscr{text%plain}#m
\mathsfup{text%plain}#*m
\mathsfit{text%plain}#*m
\mathbfsf{text%plain}#*m
\mathbfup{text%plain}#*m
\mathbfit{text%plain}#*m
\mathbfcal{text%plain}#*m
\mathbfscr{text%plain}#*m
\mathbffrak{text%plain}#*m
\mathbfsfup{text%plain}#*m
\mathbfsfit{text%plain}#*m
\mathfrak{text%plain}#m

# Commands not in the main documentation
\addnolimits{math commands%formula}#*
\crampeddisplaystyle#*
\crampedscriptscriptstyle#*
\crampedscriptstyle#*
\crampedtextstyle#*
\mathaccentoverlay#S
\mathaccentwide#S
\mathbacktick#S
\mathbotaccent#S
\mathbotaccentwide#S
\mathfence#S
\mathover#S
\mathstraightquote#S
\mathunder#S
\removenolimits{math commands%formula}#*
\UnicodeMathSymbol{code point}{cmd}{math class}{unicode name}#*d

# commands defined by default font (computer modern) for both math and text
\Angstrom
\ast
\backdprime
\backprime
\backslash
\backtrprime
\blanksymbol
\bullet
\cdotp
\dagger
\ddagger
\diameter
\div
\divslash#*
\downarrow
\dprime
\eighthnote
\equal#*
\eth
\euro
\fracslash#*
\gets
\greater#*
\infty
\ldotp#*
\leftarrow
\less#*
\lnot
\mathampersand
\mathatsign
\mathcolon
\mathcomma
\mathdollar
\matheth
\mathhyphen
\mathoctothorpe
\mathparagraph
\mathpercent
\mathperiod
\mathplus
\mathquestion
\mathratio
\mathsection
\mathsemicolon
\mathslash
\mathsterling
\mathunderscore
\mathvisiblespace
\mathyen
\mho
\minus#*
\neg
\pm
\prime
\qprime
\rightarrow
\smblkcircle
\smwhtcircle
\sphericalangle#*
\surd#*
\tieconcat#*
\times
\to
\trprime
\unicodeellipsis#*
\uparrow
\vert
\Vert

# math letter commands defined by default font (computer modern)
\Alpha#*m
\BbbA#*m
\Bbba#*m
\BbbB#*m
\Bbbb#*m
\BbbC#*m
\Bbbc#*m
\BbbD#*m
\Bbbd#*m
\BbbE#*m
\Bbbe#*m
\Bbbeight#*m
\BbbF#*m
\Bbbf#*m
\Bbbfive#*m
\Bbbfour#*m
\BbbG#*m
\Bbbg#*m
\Bbbgamma#*m
\BbbGamma#*m
\BbbH#*m
\Bbbh#*m
\BbbI#*m
\Bbbi#*m
\BbbJ#*m
\Bbbj#*m
\BbbK#*m
\Bbbk#*m
\BbbL#*m
\Bbbl#*m
\BbbM#*m
\Bbbm#*m
\BbbN#*m
\Bbbn#*m
\Bbbnine#*m
\BbbO#*m
\Bbbo#*m
\Bbbone#*m
\BbbP#*m
\Bbbp#*m
\Bbbpi#*m
\BbbPi#*m
\BbbQ#*m
\Bbbq#*m
\BbbR#*m
\Bbbr#*m
\BbbS#*m
\Bbbs#*m
\Bbbseven#*m
\Bbbsix#*m
\Bbbsum#*m
\BbbT#*m
\Bbbt#*m
\Bbbthree#*m
\Bbbtwo#*m
\BbbU#*m
\Bbbu#*m
\BbbV#*m
\Bbbv#*m
\BbbW#*m
\Bbbw#*m
\BbbX#*m
\Bbbx#*m
\BbbY#*m
\Bbby#*m
\BbbZ#*m
\Bbbz#*m
\Bbbzero#*m
\Beta#*m
\Chi#*m
\Epsilon#*m
\Eta#*m
\Iota#*m
\itAlpha#*m
\italpha#*m
\itBeta#*m
\itbeta#*m
\itChi#*m
\itchi#*m
\itDelta#*m
\itdelta#*m
\itEpsilon#*m
\itepsilon#*m
\itEta#*m
\iteta#*m
\itGamma#*m
\itgamma#*m
\itIota#*m
\itiota#*m
\itKappa#*m
\itkappa#*m
\itLambda#*m
\itlambda#*m
\itMu#*m
\itmu#*m
\itNu#*m
\itnu#*m
\itOmega#*m
\itomega#*m
\itOmicron#*m
\itomicron#*m
\itPhi#*m
\itphi#*m
\itPi#*m
\itpi#*m
\itPsi#*m
\itpsi#*m
\itRho#*m
\itrho#*m
\itSigma#*m
\itsigma#*m
\itTau#*m
\ittau#*m
\itTheta#*m
\ittheta#*m
\itUpsilon#*m
\itupsilon#*m
\itvarepsilon#*m
\itvarkappa#*m
\itvarphi#*m
\itvarpi#*m
\itvarrho#*m
\itvarsigma#*m
\itvarTheta#*m
\itvartheta#*m
\itXi#*m
\itxi#*m
\itZeta#*m
\itzeta#*m
\Kappa#*m
\mbfA#*m
\mbfa#*m
\mbfAlpha#*m
\mbfalpha#*m
\mbfB#*m
\mbfb#*m
\mbfBeta#*m
\mbfbeta#*m
\mbfC#*m
\mbfc#*m
\mbfChi#*m
\mbfchi#*m
\mbfD#*m
\mbfd#*m
\mbfDelta#*m
\mbfdelta#*m
\mbfE#*m
\mbfe#*m
\mbfeight#*m
\mbfEpsilon#*m
\mbfepsilon#*m
\mbfEta#*m
\mbfeta#*m
\mbfF#*m
\mbff#*m
\mbffive#*m
\mbffour#*m
\mbffrakA#*m
\mbffraka#*m
\mbffrakB#*m
\mbffrakb#*m
\mbffrakC#*m
\mbffrakc#*m
\mbffrakD#*m
\mbffrakd#*m
\mbffrakE#*m
\mbffrake#*m
\mbffrakF#*m
\mbffrakf#*m
\mbffrakG#*m
\mbffrakg#*m
\mbffrakH#*m
\mbffrakh#*m
\mbffrakI#*m
\mbffraki#*m
\mbffrakJ#*m
\mbffrakj#*m
\mbffrakK#*m
\mbffrakk#*m
\mbffrakL#*m
\mbffrakl#*m
\mbffrakM#*m
\mbffrakm#*m
\mbffrakN#*m
\mbffrakn#*m
\mbffrakO#*m
\mbffrako#*m
\mbffrakP#*m
\mbffrakp#*m
\mbffrakQ#*m
\mbffrakq#*m
\mbffrakR#*m
\mbffrakr#*m
\mbffrakS#*m
\mbffraks#*m
\mbffrakT#*m
\mbffrakt#*m
\mbffrakU#*m
\mbffraku#*m
\mbffrakV#*m
\mbffrakv#*m
\mbffrakW#*m
\mbffrakw#*m
\mbffrakX#*m
\mbffrakx#*m
\mbffrakY#*m
\mbffraky#*m
\mbffrakZ#*m
\mbffrakz#*m
\mbfG#*m
\mbfg#*m
\mbfGamma#*m
\mbfgamma#*m
\mbfH#*m
\mbfh#*m
\mbfI#*m
\mbfi#*m
\mbfIota#*m
\mbfiota#*m
\mbfitA#*m
\mbfita#*m
\mbfitAlpha#*m
\mbfitalpha#*m
\mbfitB#*m
\mbfitb#*m
\mbfitBeta#*m
\mbfitbeta#*m
\mbfitC#*m
\mbfitc#*m
\mbfitChi#*m
\mbfitchi#*m
\mbfitD#*m
\mbfitd#*m
\mbfitDelta#*m
\mbfitdelta#*m
\mbfitE#*m
\mbfite#*m
\mbfitEpsilon#*m
\mbfitepsilon#*m
\mbfitEta#*m
\mbfiteta#*m
\mbfitF#*m
\mbfitf#*m
\mbfitG#*m
\mbfitg#*m
\mbfitGamma#*m
\mbfitgamma#*m
\mbfitH#*m
\mbfith#*m
\mbfitI#*m
\mbfiti#*m
\mbfitIota#*m
\mbfitiota#*m
\mbfitJ#*m
\mbfitj#*m
\mbfitK#*m
\mbfitk#*m
\mbfitKappa#*m
\mbfitkappa#*m
\mbfitL#*m
\mbfitl#*m
\mbfitLambda#*m
\mbfitlambda#*m
\mbfitM#*m
\mbfitm#*m
\mbfitMu#*m
\mbfitmu#*m
\mbfitN#*m
\mbfitn#*m
\mbfitnabla#*m
\mbfitNu#*m
\mbfitnu#*m
\mbfitO#*m
\mbfito#*m
\mbfitOmega#*m
\mbfitomega#*m
\mbfitOmicron#*m
\mbfitomicron#*m
\mbfitP#*m
\mbfitp#*m
\mbfitpartial#*m
\mbfitPhi#*m
\mbfitphi#*m
\mbfitPi#*m
\mbfitpi#*m
\mbfitPsi#*m
\mbfitpsi#*m
\mbfitQ#*m
\mbfitq#*m
\mbfitR#*m
\mbfitr#*m
\mbfitRho#*m
\mbfitrho#*m
\mbfitS#*m
\mbfits#*m
\mbfitsansA#*m
\mbfitsansa#*m
\mbfitsansAlpha#*m
\mbfitsansalpha#*m
\mbfitsansB#*m
\mbfitsansb#*m
\mbfitsansBeta#*m
\mbfitsansbeta#*m
\mbfitsansC#*m
\mbfitsansc#*m
\mbfitsansChi#*m
\mbfitsanschi#*m
\mbfitsansD#*m
\mbfitsansd#*m
\mbfitsansDelta#*m
\mbfitsansdelta#*m
\mbfitsansE#*m
\mbfitsanse#*m
\mbfitsansEpsilon#*m
\mbfitsansepsilon#*m
\mbfitsansEta#*m
\mbfitsanseta#*m
\mbfitsansF#*m
\mbfitsansf#*m
\mbfitsansG#*m
\mbfitsansg#*m
\mbfitsansGamma#*m
\mbfitsansgamma#*m
\mbfitsansH#*m
\mbfitsansh#*m
\mbfitsansI#*m
\mbfitsansi#*m
\mbfitsansIota#*m
\mbfitsansiota#*m
\mbfitsansJ#*m
\mbfitsansj#*m
\mbfitsansK#*m
\mbfitsansk#*m
\mbfitsansKappa#*m
\mbfitsanskappa#*m
\mbfitsansL#*m
\mbfitsansl#*m
\mbfitsansLambda#*m
\mbfitsanslambda#*m
\mbfitsansM#*m
\mbfitsansm#*m
\mbfitsansMu#*m
\mbfitsansmu#*m
\mbfitsansN#*m
\mbfitsansn#*m
\mbfitsansnabla#*m
\mbfitsansNu#*m
\mbfitsansnu#*m
\mbfitsansO#*m
\mbfitsanso#*m
\mbfitsansOmega#*m
\mbfitsansomega#*m
\mbfitsansOmicron#*m
\mbfitsansomicron#*m
\mbfitsansP#*m
\mbfitsansp#*m
\mbfitsanspartial#*m
\mbfitsansPhi#*m
\mbfitsansphi#*m
\mbfitsansPi#*m
\mbfitsanspi#*m
\mbfitsansPsi#*m
\mbfitsanspsi#*m
\mbfitsansQ#*m
\mbfitsansq#*m
\mbfitsansR#*m
\mbfitsansr#*m
\mbfitsansRho#*m
\mbfitsansrho#*m
\mbfitsansS#*m
\mbfitsanss#*m
\mbfitsansSigma#*m
\mbfitsanssigma#*m
\mbfitsansT#*m
\mbfitsanst#*m
\mbfitsansTau#*m
\mbfitsanstau#*m
\mbfitsansTheta#*m
\mbfitsanstheta#*m
\mbfitsansU#*m
\mbfitsansu#*m
\mbfitsansUpsilon#*m
\mbfitsansupsilon#*m
\mbfitsansV#*m
\mbfitsansv#*m
\mbfitsansvarepsilon#*m
\mbfitsansvarkappa#*m
\mbfitsansvarphi#*m
\mbfitsansvarpi#*m
\mbfitsansvarrho#*m
\mbfitsansvarsigma#*m
\mbfitsansvarTheta#*m
\mbfitsansvartheta#*m
\mbfitsansW#*m
\mbfitsansw#*m
\mbfitsansX#*m
\mbfitsansx#*m
\mbfitsansXi#*m
\mbfitsansxi#*m
\mbfitsansY#*m
\mbfitsansy#*m
\mbfitsansZ#*m
\mbfitsansz#*m
\mbfitsansZeta#*m
\mbfitsanszeta#*m
\mbfitSigma#*m
\mbfitsigma#*m
\mbfitT#*m
\mbfitt#*m
\mbfitTau#*m
\mbfittau#*m
\mbfitTheta#*m
\mbfittheta#*m
\mbfitU#*m
\mbfitu#*m
\mbfitUpsilon#*m
\mbfitupsilon#*m
\mbfitV#*m
\mbfitv#*m
\mbfitvarepsilon#*m
\mbfitvarkappa#*m
\mbfitvarphi#*m
\mbfitvarpi#*m
\mbfitvarrho#*m
\mbfitvarsigma#*m
\mbfitvarTheta#*m
\mbfitvartheta#*m
\mbfitW#*m
\mbfitw#*m
\mbfitX#*m
\mbfitx#*m
\mbfitXi#*m
\mbfitxi#*m
\mbfitY#*m
\mbfity#*m
\mbfitZ#*m
\mbfitz#*m
\mbfitZeta#*m
\mbfitzeta#*m
\mbfJ#*m
\mbfj#*m
\mbfK#*m
\mbfk#*m
\mbfKappa#*m
\mbfkappa#*m
\mbfL#*m
\mbfl#*m
\mbfLambda#*m
\mbflambda#*m
\mbfM#*m
\mbfm#*m
\mbfMu#*m
\mbfmu#*m
\mbfN#*m
\mbfn#*m
\mbfnabla#*m
\mbfnine#*m
\mbfNu#*m
\mbfnu#*m
\mbfO#*m
\mbfo#*m
\mbfOmega#*m
\mbfomega#*m
\mbfOmicron#*m
\mbfomicron#*m
\mbfone#*m
\mbfP#*m
\mbfp#*m
\mbfpartial#*m
\mbfPhi#*m
\mbfphi#*m
\mbfPi#*m
\mbfpi#*m
\mbfPsi#*m
\mbfpsi#*m
\mbfQ#*m
\mbfq#*m
\mbfR#*m
\mbfr#*m
\mbfRho#*m
\mbfrho#*m
\mbfS#*m
\mbfs#*m
\mbfsansA#*m
\mbfsansa#*m
\mbfsansAlpha#*m
\mbfsansalpha#*m
\mbfsansB#*m
\mbfsansb#*m
\mbfsansBeta#*m
\mbfsansbeta#*m
\mbfsansC#*m
\mbfsansc#*m
\mbfsansChi#*m
\mbfsanschi#*m
\mbfsansD#*m
\mbfsansd#*m
\mbfsansDelta#*m
\mbfsansdelta#*m
\mbfsansE#*m
\mbfsanse#*m
\mbfsanseight#*m
\mbfsansEpsilon#*m
\mbfsansepsilon#*m
\mbfsansEta#*m
\mbfsanseta#*m
\mbfsansF#*m
\mbfsansf#*m
\mbfsansfive#*m
\mbfsansfour#*m
\mbfsansG#*m
\mbfsansg#*m
\mbfsansGamma#*m
\mbfsansgamma#*m
\mbfsansH#*m
\mbfsansh#*m
\mbfsansI#*m
\mbfsansi#*m
\mbfsansIota#*m
\mbfsansiota#*m
\mbfsansJ#*m
\mbfsansj#*m
\mbfsansK#*m
\mbfsansk#*m
\mbfsansKappa#*m
\mbfsanskappa#*m
\mbfsansL#*m
\mbfsansl#*m
\mbfsansLambda#*m
\mbfsanslambda#*m
\mbfsansM#*m
\mbfsansm#*m
\mbfsansMu#*m
\mbfsansmu#*m
\mbfsansN#*m
\mbfsansn#*m
\mbfsansnabla#*m
\mbfsansnine#*m
\mbfsansNu#*m
\mbfsansnu#*m
\mbfsansO#*m
\mbfsanso#*m
\mbfsansOmega#*m
\mbfsansomega#*m
\mbfsansOmicron#*m
\mbfsansomicron#*m
\mbfsansone#*m
\mbfsansP#*m
\mbfsansp#*m
\mbfsanspartial#*m
\mbfsansPhi#*m
\mbfsansphi#*m
\mbfsansPi#*m
\mbfsanspi#*m
\mbfsansPsi#*m
\mbfsanspsi#*m
\mbfsansQ#*m
\mbfsansq#*m
\mbfsansR#*m
\mbfsansr#*m
\mbfsansRho#*m
\mbfsansrho#*m
\mbfsansS#*m
\mbfsanss#*m
\mbfsansseven#*m
\mbfsansSigma#*m
\mbfsanssigma#*m
\mbfsanssix#*m
\mbfsansT#*m
\mbfsanst#*m
\mbfsansTau#*m
\mbfsanstau#*m
\mbfsansTheta#*m
\mbfsanstheta#*m
\mbfsansthree#*m
\mbfsanstwo#*m
\mbfsansU#*m
\mbfsansu#*m
\mbfsansUpsilon#*m
\mbfsansupsilon#*m
\mbfsansV#*m
\mbfsansv#*m
\mbfsansvarepsilon#*m
\mbfsansvarkappa#*m
\mbfsansvarphi#*m
\mbfsansvarpi#*m
\mbfsansvarrho#*m
\mbfsansvarsigma#*m
\mbfsansvarTheta#*m
\mbfsansvartheta#*m
\mbfsansW#*m
\mbfsansw#*m
\mbfsansX#*m
\mbfsansx#*m
\mbfsansXi#*m
\mbfsansxi#*m
\mbfsansY#*m
\mbfsansy#*m
\mbfsansZ#*m
\mbfsansz#*m
\mbfsanszero#*m
\mbfsansZeta#*m
\mbfsanszeta#*m
\mbfscrA#*m
\mbfscrB#*m
\mbfscrC#*m
\mbfscrD#*m
\mbfscrE#*m
\mbfscrF#*m
\mbfscrG#*m
\mbfscrH#*m
\mbfscrI#*m
\mbfscrJ#*m
\mbfscrK#*m
\mbfscrL#*m
\mbfscrM#*m
\mbfscrN#*m
\mbfscrO#*m
\mbfscrP#*m
\mbfscrQ#*m
\mbfscrR#*m
\mbfscrS#*m
\mbfscrT#*m
\mbfscrU#*m
\mbfscrV#*m
\mbfscrW#*m
\mbfscrX#*m
\mbfscrY#*m
\mbfscrZ#*m
\mbfseven#*m
\mbfSigma#*m
\mbfsigma#*m
\mbfsix#*m
\mbfT#*m
\mbft#*m
\mbfTau#*m
\mbftau#*m
\mbfTheta#*m
\mbftheta#*m
\mbfthree#*m
\mbftwo#*m
\mbfU#*m
\mbfu#*m
\mbfUpsilon#*m
\mbfupsilon#*m
\mbfV#*m
\mbfv#*m
\mbfvarepsilon#*m
\mbfvarkappa#*m
\mbfvarphi#*m
\mbfvarpi#*m
\mbfvarrho#*m
\mbfvarsigma#*m
\mbfvarTheta#*m
\mbfvartheta#*m
\mbfW#*m
\mbfw#*m
\mbfX#*m
\mbfx#*m
\mbfXi#*m
\mbfxi#*m
\mbfY#*m
\mbfy#*m
\mbfZ#*m
\mbfz#*m
\mbfzero#*m
\mbfZeta#*m
\mbfzeta#*m
\mfrakA#*m
\mfraka#*m
\mfrakB#*m
\mfrakb#*m
\mfrakC#*m
\mfrakc#*m
\mfrakD#*m
\mfrakd#*m
\mfrakE#*m
\mfrake#*m
\mfrakF#*m
\mfrakf#*m
\mfrakG#*m
\mfrakg#*m
\mfrakH#*m
\mfrakh#*m
\mfraki#*m
\mfrakJ#*m
\mfrakj#*m
\mfrakK#*m
\mfrakk#*m
\mfrakL#*m
\mfrakl#*m
\mfrakM#*m
\mfrakm#*m
\mfrakN#*m
\mfrakn#*m
\mfrakO#*m
\mfrako#*m
\mfrakP#*m
\mfrakp#*m
\mfrakQ#*m
\mfrakq#*m
\mfrakr#*m
\mfrakS#*m
\mfraks#*m
\mfrakT#*m
\mfrakt#*m
\mfrakU#*m
\mfraku#*m
\mfrakV#*m
\mfrakv#*m
\mfrakW#*m
\mfrakw#*m
\mfrakX#*m
\mfrakx#*m
\mfrakY#*m
\mfraky#*m
\mfrakZ#*m
\mfrakz#*m
\mitA#*m
\mita#*m
\mitAlpha#*m
\mitalpha#*m
\mitB#*m
\mitb#*m
\mitBbbD#*m
\mitBbbd#*m
\mitBbbe#*m
\mitBbbi#*m
\mitBbbj#*m
\mitBeta#*m
\mitbeta#*m
\mitC#*m
\mitc#*m
\mitChi#*m
\mitchi#*m
\mitD#*m
\mitd#*m
\mitDelta#*m
\mitdelta#*m
\mitE#*m
\mite#*m
\mitEpsilon#*m
\mitepsilon#*m
\mitEta#*m
\miteta#*m
\mitF#*m
\mitf#*m
\mitG#*m
\mitg#*m
\mitGamma#*m
\mitgamma#*m
\mitH#*m
\mitI#*m
\miti#*m
\mitIota#*m
\mitiota#*m
\mitJ#*m
\mitj#*m
\mitK#*m
\mitk#*m
\mitKappa#*m
\mitkappa#*m
\mitL#*m
\mitl#*m
\mitLambda#*m
\mitlambda#*m
\mitM#*m
\mitm#*m
\mitMu#*m
\mitmu#*m
\mitN#*m
\mitn#*m
\mitnabla#*m
\mitNu#*m
\mitnu#*m
\mitO#*m
\mito#*m
\mitOmega#*m
\mitomega#*m
\mitOmicron#*m
\mitomicron#*m
\mitP#*m
\mitp#*m
\mitpartial#*m
\mitPhi#*m
\mitphi#*m
\mitPi#*m
\mitpi#*m
\mitPsi#*m
\mitpsi#*m
\mitQ#*m
\mitq#*m
\mitR#*m
\mitr#*m
\mitRho#*m
\mitrho#*m
\mitS#*m
\mits#*m
\mitsansA#*m
\mitsansa#*m
\mitsansB#*m
\mitsansb#*m
\mitsansC#*m
\mitsansc#*m
\mitsansD#*m
\mitsansd#*m
\mitsansE#*m
\mitsanse#*m
\mitsansF#*m
\mitsansf#*m
\mitsansG#*m
\mitsansg#*m
\mitsansH#*m
\mitsansh#*m
\mitsansI#*m
\mitsansi#*m
\mitsansJ#*m
\mitsansj#*m
\mitsansK#*m
\mitsansk#*m
\mitsansL#*m
\mitsansl#*m
\mitsansM#*m
\mitsansm#*m
\mitsansN#*m
\mitsansn#*m
\mitsansO#*m
\mitsanso#*m
\mitsansP#*m
\mitsansp#*m
\mitsansQ#*m
\mitsansq#*m
\mitsansR#*m
\mitsansr#*m
\mitsansS#*m
\mitsanss#*m
\mitsansT#*m
\mitsanst#*m
\mitsansU#*m
\mitsansu#*m
\mitsansV#*m
\mitsansv#*m
\mitsansW#*m
\mitsansw#*m
\mitsansX#*m
\mitsansx#*m
\mitsansY#*m
\mitsansy#*m
\mitsansZ#*m
\mitsansz#*m
\mitSigma#*m
\mitsigma#*m
\mitT#*m
\mitt#*m
\mitTau#*m
\mittau#*m
\mitTheta#*m
\mittheta#*m
\mitU#*m
\mitu#*m
\mitUpsilon#*m
\mitupsilon#*m
\mitV#*m
\mitv#*m
\mitvarepsilon#*m
\mitvarkappa#*m
\mitvarphi#*m
\mitvarpi#*m
\mitvarrho#*m
\mitvarsigma#*m
\mitvarTheta#*m
\mitvartheta#*m
\mitW#*m
\mitw#*m
\mitX#*m
\mitx#*m
\mitXi#*m
\mitxi#*m
\mitY#*m
\mity#*m
\mitZ#*m
\mitz#*m
\mitZeta#*m
\mitzeta#*m
\msansA#*m
\msansa#*m
\msansB#*m
\msansb#*m
\msansC#*m
\msansc#*m
\msansD#*m
\msansd#*m
\msansE#*m
\msanse#*m
\msanseight#*m
\msansF#*m
\msansf#*m
\msansfive#*m
\msansfour#*m
\msansG#*m
\msansg#*m
\msansH#*m
\msansh#*m
\msansI#*m
\msansi#*m
\msansJ#*m
\msansj#*m
\msansK#*m
\msansk#*m
\msansL#*m
\msansl#*m
\msansM#*m
\msansm#*m
\msansN#*m
\msansn#*m
\msansnine#*m
\msansO#*m
\msanso#*m
\msansone#*m
\msansP#*m
\msansp#*m
\msansQ#*m
\msansq#*m
\msansR#*m
\msansr#*m
\msansS#*m
\msanss#*m
\msansseven#*m
\msanssix#*m
\msansT#*m
\msanst#*m
\msansthree#*m
\msanstwo#*m
\msansU#*m
\msansu#*m
\msansV#*m
\msansv#*m
\msansW#*m
\msansw#*m
\msansX#*m
\msansx#*m
\msansY#*m
\msansy#*m
\msansZ#*m
\msansz#*m
\msanszero#*m
\mscrA#*m
\mscrB#*m
\mscrC#*m
\mscrD#*m
\mscrE#*m
\mscrF#*m
\mscrG#*m
\mscrH#*m
\mscrI#*m
\mscrJ#*m
\mscrK#*m
\mscrL#*m
\mscrM#*m
\mscrN#*m
\mscrO#*m
\mscrP#*m
\mscrQ#*m
\mscrR#*m
\mscrS#*m
\mscrT#*m
\mscrU#*m
\mscrV#*m
\mscrW#*m
\mscrX#*m
\mscrY#*m
\mscrZ#*m
\mttA#*m
\mtta#*m
\mttB#*m
\mttb#*m
\mttC#*m
\mttc#*m
\mttD#*m
\mttd#*m
\mttE#*m
\mtte#*m
\mtteight#*m
\mttF#*m
\mttf#*m
\mttfive#*m
\mttfour#*m
\mttG#*m
\mttg#*m
\mttH#*m
\mtth#*m
\mttI#*m
\mtti#*m
\mttJ#*m
\mttj#*m
\mttK#*m
\mttk#*m
\mttL#*m
\mttl#*m
\mttM#*m
\mttm#*m
\mttN#*m
\mttn#*m
\mttnine#*m
\mttO#*m
\mtto#*m
\mttone#*m
\mttP#*m
\mttp#*m
\mttQ#*m
\mttq#*m
\mttR#*m
\mttr#*m
\mttS#*m
\mtts#*m
\mttseven#*m
\mttsix#*m
\mttT#*m
\mttt#*m
\mttthree#*m
\mtttwo#*m
\mttU#*m
\mttu#*m
\mttV#*m
\mttv#*m
\mttW#*m
\mttw#*m
\mttX#*m
\mttx#*m
\mttY#*m
\mtty#*m
\mttZ#*m
\mttz#*m
\mttzero#*m
\Mu#*m
\mupAlpha#*m
\mupalpha#*m
\mupBeta#*m
\mupbeta#*m
\mupChi#*m
\mupchi#*m
\mupDelta#*m
\mupdelta#*m
\mupEpsilon#*m
\mupepsilon#*m
\mupEta#*m
\mupeta#*m
\mupGamma#*m
\mupgamma#*m
\mupIota#*m
\mupiota#*m
\mupKappa#*m
\mupkappa#*m
\mupLambda#*m
\muplambda#*m
\mupMu#*m
\mupmu#*m
\mupNu#*m
\mupnu#*m
\mupOmega#*m
\mupomega#*m
\mupOmicron#*m
\mupomicron#*m
\mupPhi#*m
\mupphi#*m
\mupPi#*m
\muppi#*m
\mupPsi#*m
\muppsi#*m
\mupRho#*m
\muprho#*m
\mupSigma#*m
\mupsigma#*m
\mupTau#*m
\muptau#*m
\mupTheta#*m
\muptheta#*m
\mupUpsilon#*m
\mupupsilon#*m
\mupvarepsilon#*m
\mupvarkappa#*m
\mupvarphi#*m
\mupvarpi#*m
\mupvarrho#*m
\mupvarsigma#*m
\mupvartheta#*m
\mupvarTheta#*m
\mupXi#*m
\mupxi#*m
\mupZeta#*m
\mupzeta#*m
\Nu#*m
\Omicron#*m
\omicron#*m
\Rho#*m
\Tau#*m
\upAlpha#*m
\upalpha#*m
\upBeta#*m
\upbeta#*m
\upChi#*m
\upchi#*m
\upDelta#*m
\updelta#*m
\upEpsilon#*m
\upepsilon#*m
\upEta#*m
\upeta#*m
\upGamma#*m
\upgamma#*m
\upIota#*m
\upiota#*m
\upKappa#*m
\upkappa#*m
\upLambda#*m
\uplambda#*m
\upMu#*m
\upmu#*m
\upNu#*m
\upnu#*m
\upOmega#*m
\upomega#*m
\upOmicron#*m
\upomicron#*m
\upPhi#*m
\upphi#*m
\upPi#*m
\uppi#*m
\upPsi#*m
\uppsi#*m
\upRho#*m
\uprho#*m
\upSigma#*m
\upsigma#*m
\upTau#*m
\uptau#*m
\upTheta#*m
\uptheta#*m
\upUpsilon#*m
\upupsilon#*m
\upvarepsilon#*m
\upvarkappa#*m
\upvarphi#*m
\upvarpi#*m
\upvarrho#*m
\upvarsigma#*m
\upvarTheta#*m
\upvartheta#*m
\upXi#*m
\upxi#*m
\upZeta#*m
\upzeta#*m
\varkappa#m
\Zeta#*m

# math symbol commands defined by default font (computer modern)
\acwopencirclearrow#m
\adots#m
\approxeq#m
\approxident#m
\arceq#m
\assert#m
\asteraccent{arg}#m
\awint#m
\backcong#m
\backsim#m
\backsimeq#m
\barvee#m
\barwedge#m
\because#m
\beth#m
\between#m
\bigblacktriangledown#m
\bigblacktriangleup#m
\bigbot#m
\bigcupdot#m
\bigsqcap#m
\bigtimes#m
\bigtop#m
\blacktriangleleft#m
\blacktriangleright#m
\blockfull#m
\blockhalfshaded#m
\blockqtrshaded#m
\blockthreeqtrshaded#m
\boxdot#m
\boxminus#m
\boxplus#m
\boxtimes#m
\bumpeq#m
\Bumpeq#m
\Cap#m
\carriagereturn#m
\checkmark#m
\circeq#m
\circledast#m
\circledcirc#m
\circleddash#m
\circledequal#m
\Colon#m
\coloneq#m
\complement#m
\concavediamond#m
\concavediamondtickleft#m
\concavediamondtickright#m
\Cup#m
\cupdot#m
\cupleftarrow#m
\curlyeqprec#m
\curlyeqsucc#m
\curlyvee#m
\curlywedge#m
\curvearrowleft#m
\curvearrowright#m
\cwopencirclearrow#m
\daleth#m
\dashcolon#m
\DashVDash#m
\dashVdash#m
\diagdown#m
\diagup#m
\divideontimes#m
\Doteq#m
\dotminus#m
\dotplus#m
\dotsminusdots#m
\dottedsquare#m
\downdownarrows#m
\downharpoonleft#m
\downharpoonright#m
\downuparrows#m
\downwhitearrow#m
\enclosecircle#m
\enclosediamond#m
\enclosesquare#m
\enclosetriangle#m
\eqcirc#m
\eqcolon#m
\eqdef#m
\eqgtr#m
\eqless#m
\eqsim#m
\eqslantgtr#m
\eqslantless#m
\equalparallel#m
\Equiv#m
\Eulerconst#m
\fallingdotseq#m
\geqq#m
\geqslant#m
\ggg#m
\gimel#m
\gnapprox#m
\gneq#m
\gneqq#m
\gnsim#m
\gtrapprox#m
\gtrdot#m
\gtreqless#m
\gtreqqless#m
\gtrless#m
\gtrsim#m
\hermitmatrix#m
\horizbar#m
\hrectangle#m
\hrectangleblack#m
\hslash#m
\imageof#m
\increment#m
\intbottom#*m
\intclockwise#m
\intercal#m
\inttop#*m
\invlazys#m
\invnot#m
\kernelcontraction#m
\lAngle#m
\lbracelend#*m
\lbracemid#*m
\lbraceuend#*m
\lBrack#m
\lbrackextender#*m
\lbracklend#*m
\lbrackuend#*m
\Ldsh#m
\leftarrowtail#m
\leftharpoonaccent{arg}#m
\leftleftarrows#m
\leftrightarrows#m
\leftrightharpoons#m
\leftrightsquigarrow#m
\leftsquigarrow#m
\leftthreearrows#m
\leftthreetimes#m
\leftwhitearrow#m
\leqq#m
\leqslant#m
\lessapprox#m
\lessdot#m
\lesseqgtr#m
\lesseqqgtr#m
\lessgtr#m
\lesssim#m
\lgwhtcircle#m
\linefeed#m
\llcorner#*m
\Lleftarrow#m
\lll#m
\lnapprox#m
\lneq#m
\lneqq#m
\lnsim#m
\longdashv#m
\longleftsquigarrow#m
\longmapsfrom#m
\Longmapsfrom#m
\Longmapsto#m
\longrightsquigarrow#m
\looparrowleft#m
\looparrowright#m
\lozengeminus#m
\lparen#m
\lparenextender#*m
\lparenlend#*m
\lparenuend#*m
\lrcorner#*m
\Lsh#m
\ltimes#m
\maltese#m
\mapsdown#m
\mapsfrom#m
\Mapsfrom#m
\Mapsto#m
\mapsup#m
\mathexclam#m
\mathunderbar{arg}#*m
\mdlgblkcircle#m
\mdlgblksquare#m
\mdlgwhtcircle#m
\mdlgwhtlozenge#m
\mdlgwhtsquare#m
\measeq#m
\measuredangle#m
\measuredrightangle#m
\minus#m
\multimap#m
\multimapinv#m
\napprox#m
\nasymp#m
\ncong#m
\Nearrow#m
\nequiv#m
\nexists#m
\ngeq#m
\ngtr#m
\ngtrless#m
\ngtrsim#m
\nleftarrow#m
\nLeftarrow#m
\nleftrightarrow#m
\nLeftrightarrow#m
\nleq#m
\nless#m
\nlessgtr#m
\nlesssim#m
\nmid#m
\nni#m
\notaccent{arg}#*m
\nparallel#m
\nprec#m
\npreccurlyeq#m
\nrightarrow#m
\nRightarrow#m
\nsim#m
\nsime#m
\nsimeq#m
\nsqsubseteq#m
\nsqsupseteq#m
\nsubset#m
\nsubseteq#m
\nsucc#m
\nsucccurlyeq#m
\nsupset#m
\nsupseteq#m
\ntrianglelefteq#m
\ntrianglerighteq#m
\nvartriangleleft#m
\nvartriangleright#m
\nvdash#m
\nvDash#m
\nVdash#m
\nVDash#m
\Nwarrow#m
\obrbrak#m
\ocirc{arg}#m
\oiiint#m
\oiint#m
\ointctrclockwise#m
\origof#m
\overbar{arg}#m
\overbracket{arg}#m
\overleftharpoon{arg}#m
\overparen{arg}#m
\overrightharpoon{arg}#m
\ovhook{arg}#m
\Planckconst#m
\preccurlyeq#m
\precnsim#m
\precsim#m
\QED#m
\questeq#m
\rAngle#m
\rbracelend#*m
\rbracemid#*m
\rbraceuend#*m
\rBrack#m
\rbrackextender#*m
\rbracklend#*m
\rbrackuend#*m
\Rdsh#m
\reversesolidus#m
\rightangle#m
\rightarrowonoplus#m
\rightarrowtail#m
\rightharpoonaccent{arg}#m
\rightleftarrows#m
\rightrightarrows#m
\rightsquigarrow#m
\rightthreearrows#m
\rightthreetimes#m
\rightwhitearrow#m
\risingdotseq#m
\rparen#m
\rparenextender#*m
\rparenlend#*m
\rparenuend#*m
\Rrightarrow#m
\Rsh#m
\rtimes#m
\Searrow#m
\sime#m
\simneqq#m
\sinewave#m
\smallin#m
\smallni#m
\smallsetminus#m
\smblksquare#m
\smwhtdiamond#m
\smwhtsquare#m
\sqrtbottom#m
\sqsubset#m
\sqsubsetneq#m
\sqsupset#m
\sqsupsetneq#m
\stareq#m
\Subset#m
\subsetneq#m
\succcurlyeq#m
\succnsim#m
\succsim#m
\sumbottom#m
\sumtop#m
\Supset#m
\supsetneq#m
\Swarrow#m
\therefore#m
\threeunderdot{arg}#m
\trianglelefteq#m
\triangleq#m
\trianglerighteq#m
\turnednot#m
\twoheaddownarrow#m
\twoheadleftarrow#m
\twoheadrightarrow#m
\twoheaduparrow#m
\twolowline#m
\ubrbrak#m
\ulcorner#*m
\underbracket{arg}#m
\underleftharpoondown{arg}#m
\underparen{arg}#m
\underrightharpoondown{arg}#m
\unicodecdots#*m
\updownarrows#m
\upharpoonleft#m
\upharpoonright#m
\upuparrows#m
\upwhitearrow#m
\urcorner#*m
\varbarwedge#m
\varclubsuit#m
\vardiamondsuit#m
\vardoublebarwedge#m
\varheartsuit#m
\varlrtriangle#m
\varnothing#m
\varointclockwise#m
\varspadesuit#m
\vartriangleleft#m
\vartriangleright#m
\vbraceextender#*m
\VDash#m
\vDash#m
\Vdash#m
\vectimes#m
\veebar#m
\veeeq#m
\vertoverlay{arg}#m
\vlongdash#m
\Vvdash#m
\vysmblkcircle#m
\vysmwhtcircle#m
\wedgeq#m
\widebreve{arg}#m
\widebridgeabove{arg}#m
\widecheck{arg}#m
\wideoverbar{arg}#m
\wideutilde{arg}#m

# only available if mathtools loaded
\MToverbracket{arg}#Sm
\MTunderbracket{arg}#Sm
\Uoverbracket{arg}#Sm
\Uunderbracket{arg}#Sm

## For fonts beside the default (STIX, Asana, etc.), the remaining symbols are
# listed here so as not to be marked invalid, but with #S to prevent being shown
# in completer when using fonts that don't have them.
## If the font has an associated package (fourier-otf, kpfonts-otf) then the extra
# symbols it defines are listed in that package's cwl without the #S.
\accurrent#Sm
\acidfree#Sm
\acwcirclearrow#Sm
\acwgapcirclearrow#Sm
\acwleftarcarrow#Sm
\acwoverarcarrow#Sm
\acwunderarcarrow#Sm
\angdnr#Sm
\angles#Sm
\angleubar#Sm
\annuity{arg}#Sm
\APLboxquestion#Sm
\APLboxupcaret#Sm
\APLnotbackslash#Sm
\APLnotslash#Sm
\approxeqq#Sm
\arabichad#Sm
\arabicmaj#Sm
\asteq#Sm
\astrosun#Sm
\backepsilon#Sm
\bagmember#Sm
\barcap#Sm
\barcup#Sm
\bardownharpoonleft#Sm
\bardownharpoonright#Sm
\barleftarrow#Sm
\barleftarrowrightarrowbar#Sm
\barleftharpoondown#Sm
\barleftharpoonup#Sm
\barovernorthwestarrow#Sm
\barrightarrowdiamond#Sm
\barrightharpoondown#Sm
\barrightharpoonup#Sm
\baruparrow#Sm
\barupharpoonleft#Sm
\barupharpoonright#Sm
\Barv#Sm
\barV#Sm
\bbrktbrk#Sm
\bdtriplevdash#Sm
\benzenr#Sm
\biginterleave#Sm
\bigslopedvee#Sm
\bigslopedwedge#Sm
\bigstar#Sm
\bigtalloblong#Sm
\bigtriangleleft#Sm
\bigwhitestar#Sm
\blackcircledownarrow#Sm
\blackcircledrightdot#Sm
\blackcircledtwodots#Sm
\blackcircleulquadwhite#Sm
\blackdiamonddownarrow#Sm
\blackhourglass#Sm
\blackinwhitediamond#Sm
\blackinwhitesquare#Sm
\blacklefthalfcircle#Sm
\blackpointerleft#Sm
\blackpointerright#Sm
\blackrighthalfcircle#Sm
\blacksmiley#Sm
\blacktriangle#Sm
\blacktriangledown#Sm
\blkhorzoval#Sm
\blkvertoval#Sm
\blocklefthalf#Sm
\blocklowhalf#Sm
\blockrighthalf#Sm
\blockuphalf#Sm
\bNot#Sm
\botsemicircle#Sm
\boxast#Sm
\boxbar#Sm
\boxbox#Sm
\boxbslash#Sm
\boxcircle#Sm
\boxdiag#Sm
\boxonbox#Sm
\bsimilarleftarrow#Sm
\bsimilarrightarrow#Sm
\bsolhsub#Sm
\btimes#Sm
\bullseye#Sm
\bumpeqq#Sm
\candra{arg}#Sm
\capbarcup#Sm
\capdot#Sm
\capovercup#Sm
\capwedge#Sm
\caretinsert#Sm
\ccwundercurvearrow#Sm
\cirbot#Sm
\circlebottomhalfblack#Sm
\circledbullet#Sm
\circledownarrow#Sm
\circledparallel#Sm
\circledrightdot#Sm
\circledstar#Sm
\circledtwodots#Sm
\circledvert#Sm
\circledwhitebullet#Sm
\circlehbar#Sm
\circlelefthalfblack#Sm
\circlellquad#Sm
\circlelrquad#Sm
\circleonleftarrow#Sm
\circleonrightarrow#Sm
\circlerighthalfblack#Sm
\circletophalfblack#Sm
\circleulquad#Sm
\circleurquad#Sm
\circleurquadblack#Sm
\circlevertfill#Sm
\cirE#Sm
\cirfnint#Sm
\cirmid#Sm
\cirscir#Sm
\closedvarcap#Sm
\closedvarcup#Sm
\closedvarcupsmashprod#Sm
\closure#Sm
\Coloneq#Sm
\commaminus#Sm
\congdot#Sm
\conictaper#Sm
\conjquant#Sm
\csub#Sm
\csube#Sm
\csup#Sm
\csupe#Sm
\cuberoot{arg}#Sm
\cuberootsign{arg}#Sm
\cupbarcap#Sm
\cupovercap#Sm
\cupvee#Sm
\curvearrowleftplus#Sm
\curvearrowrightminus#Sm
\cwcirclearrow#Sm
\cwgapcirclearrow#Sm
\cwrightarcarrow#Sm
\cwundercurvearrow#Sm
\danger#Sm
\dashleftharpoondown#Sm
\dashrightharpoondown#Sm
\dashV#Sm
\Dashv#Sm
\DashV#Sm
\dbkarow#Sm
\dbkarrow#Sm
\ddotseq#Sm
\DDownarrow#Sm
\Ddownarrow#Sm
\diamondbotblack#Sm
\diamondcdot#Sm
\diamondleftarrow#Sm
\diamondleftarrowbar#Sm
\diamondleftblack#Sm
\diamondrightblack#Sm
\diamondtopblack#Sm
\dicei#Sm
\diceii#Sm
\diceiii#Sm
\diceiv#Sm
\dicev#Sm
\dicevi#Sm
\Digamma#Sm
\digamma#Sm
\dingasterisk#Sm
\disin#Sm
\disjquant#Sm
\dotequiv#Sm
\dotsim#Sm
\dottedcircle#Sm
\dottimes#Sm
\doublebarvee#Sm
\doublebarwedge#Sm
\doubleplus#Sm
\downarrowbar#Sm
\downarrowbarred#Sm
\downdasharrow#Sm
\downfishtail#Sm
\downharpoonleftbar#Sm
\downharpoonrightbar#Sm
\downharpoonsleftright#Sm
\downrightcurvedarrow#Sm
\downtriangleleftblack#Sm
\downtrianglerightblack#Sm
\downupharpoonsleftright#Sm
\downzigzagarrow#Sm
\draftingarrow#Sm
\drbkarow#Sm
\drbkarrow#Sm
\droang{arg}#Sm
\dsol#Sm
\dsub#Sm
\dualmap#Sm
\egsdot#Sm
\elinters#Sm
\elsdot#Sm
\emptysetoarr#Sm
\emptysetoarrl#Sm
\emptysetobar#Sm
\emptysetocirc#Sm
\enleadertwodots#Sm
\eparsl#Sm
\eqdot#Sm
\eqeq#Sm
\eqeqeq#Sm
\eqqgtr#Sm
\eqqless#Sm
\eqqplus#Sm
\eqqsim#Sm
\eqqslantgtr#Sm
\eqqslantless#Sm
\equalleftarrow#Sm
\equalrightarrow#Sm
\equivDD#Sm
\equivVert#Sm
\equivVvert#Sm
\eqvparsl#Sm
\errbarblackcircle#Sm
\errbarblackdiamond#Sm
\errbarblacksquare#Sm
\errbarcircle#Sm
\errbardiamond#Sm
\errbarsquare#Sm
\Exclam#Sm
\fbowtie#Sm
\fcmp#Sm
\fdiagovnearrow#Sm
\fdiagovrdiag#Sm
\female#Sm
\fint#Sm
\Finv#Sm
\fisheye#Sm
\fltns#Sm
\forks#Sm
\forksnot#Sm
\forkv#Sm
\fourthroot{arg}#Sm
\fourthrootsign{arg}#Sm
\fourvdots#Sm
\fullouterjoin#Sm
\Game#Sm
\geqqslant#Sm
\gescc#Sm
\gesdot#Sm
\gesdoto#Sm
\gesdotol#Sm
\gesles#Sm
\gggnest#Sm
\gla#Sm
\glE#Sm
\gleichstark#Sm
\glj#Sm
\gsime#Sm
\gsiml#Sm
\Gt#Sm
\gtcc#Sm
\gtcir#Sm
\gtlpar#Sm
\gtquest#Sm
\gtrarr#Sm
\harrowextender#Sm
\hatapprox#Sm
\Hermaphrodite#Sm
\hexagon#Sm
\hexagonblack#Sm
\hknearrow#Sm
\hknwarrow#Sm
\hksearow#Sm
\hksearrow#Sm
\hkswarow#Sm
\hkswarrow#Sm
\hourglass#Sm
\house#Sm
\hyphenbullet#Sm
\hzigzag#Sm
\iinfin#Sm
\intbar#Sm
\intBar#Sm
\intcap#Sm
\intcup#Sm
\interleave#Sm
\intextender#Sm
\intlarhk#Sm
\intprod#Sm
\intprodr#Sm
\intx#Sm
\inversebullet#Sm
\inversewhitecircle#Sm
\invwhitelowerhalfcircle#Sm
\invwhiteupperhalfcircle#Sm
\isindot#Sm
\isinE#Sm
\isinobar#Sm
\isins#Sm
\isinvb#Sm
\Join#Sm
\langledot#Sm
\laplac#Sm
\lat#Sm
\late#Sm
\lbag#Sm
\lblkbrbrak#Sm
\lBrace#Sm
\lbracklltick#Sm
\lbrackubar#Sm
\lbrackultick#Sm
\Lbrbrak#Sm
\lbrbrak#Sm
\lcurvyangle#Sm
\leftarrowapprox#Sm
\leftarrowbackapprox#Sm
\leftarrowbsimilar#Sm
\leftarrowless#Sm
\leftarrowonoplus#Sm
\leftarrowplus#Sm
\leftarrowshortrightarrow#Sm
\leftarrowsimilar#Sm
\leftarrowsubset#Sm
\leftarrowtriangle#Sm
\leftarrowx#Sm
\leftbkarrow#Sm
\leftcurvedarrow#Sm
\leftdasharrow#Sm
\leftdbkarrow#Sm
\leftdbltail#Sm
\leftdotarrow#Sm
\leftdowncurvedarrow#Sm
\leftfishtail#Sm
\leftharpoondownbar#Sm
\leftharpoonsupdown#Sm
\leftharpoonupbar#Sm
\leftharpoonupdash#Sm
\leftmoon#Sm
\leftouterjoin#Sm
\leftrightarrowcircle#Sm
\leftrightarrowtriangle#Sm
\leftrightharpoondowndown#Sm
\leftrightharpoondownup#Sm
\leftrightharpoonsdown#Sm
\leftrightharpoonsup#Sm
\leftrightharpoonupdown#Sm
\leftrightharpoonupup#Sm
\lefttail#Sm
\leftwavearrow#Sm
\leqqslant#Sm
\lescc#Sm
\lesdot#Sm
\lesdoto#Sm
\lesdotor#Sm
\lesges#Sm
\lfbowtie#Sm
\lftimes#Sm
\lgblkcircle#Sm
\lgblksquare#Sm
\lgE#Sm
\lgwhtsquare#Sm
\llangle#Sm
\llarc#Sm
\llblacktriangle#Sm
\LLeftarrow#Sm
\lllnest#Sm
\llparenthesis#Sm
\lltriangle#Sm
\longdivision{arg}#Sm
\longdivisionsign{arg}#Sm
\lowint#Sm
\lParen#Sm
\Lparengtr#Sm
\lparenless#Sm
\lrarc#Sm
\lrblacktriangle#Sm
\lrtriangle#Sm
\lrtriangleeq#Sm
\lsime#Sm
\lsimg#Sm
\lsqhook#Sm
\Lt#Sm
\ltcc#Sm
\ltcir#Sm
\ltlarr#Sm
\ltquest#Sm
\ltrivb#Sm
\lvboxline#Sm
\lvzigzag#Sm
\Lvzigzag#Sm
\male#Sm
\mbfDigamma#Sm
\mbfdigamma#Sm
\mbfscra#Sm
\mbfscrb#Sm
\mbfscrc#Sm
\mbfscrd#Sm
\mbfscre#Sm
\mbfscrf#Sm
\mbfscrg#Sm
\mbfscrh#Sm
\mbfscri#Sm
\mbfscrj#Sm
\mbfscrk#Sm
\mbfscrl#Sm
\mbfscrm#Sm
\mbfscrn#Sm
\mbfscro#Sm
\mbfscrp#Sm
\mbfscrq#Sm
\mbfscrr#Sm
\mbfscrs#Sm
\mbfscrt#Sm
\mbfscru#Sm
\mbfscrv#Sm
\mbfscrw#Sm
\mbfscrx#Sm
\mbfscry#Sm
\mbfscrz#Sm
\mdblkcircle#Sm
\mdblkdiamond#Sm
\mdblklozenge#Sm
\mdblksquare#Sm
\mdlgblkdiamond#Sm
\mdlgblklozenge#Sm
\mdlgwhtdiamond#Sm
\mdsmblkcircle#Sm
\mdsmblksquare#Sm
\mdsmwhtcircle#Sm
\mdsmwhtsquare#Sm
\mdwhtcircle#Sm
\mdwhtdiamond#Sm
\mdwhtlozenge#Sm
\mdwhtsquare#Sm
\measangledltosw#Sm
\measangledrtose#Sm
\measangleldtosw#Sm
\measanglelutonw#Sm
\measanglerdtose#Sm
\measanglerutone#Sm
\measangleultonw#Sm
\measangleurtone#Sm
\measuredangleleft#Sm
\medblackstar#Sm
\medwhitestar#Sm
\midbarvee#Sm
\midbarwedge#Sm
\midcir#Sm
\minusdot#Sm
\minusfdots#Sm
\minusrdots#Sm
\mlcp#Sm
\modtwosum#Sm
\mscra#Sm
\mscrb#Sm
\mscrc#Sm
\mscrd#Sm
\mscre#Sm
\mscrf#Sm
\mscrg#Sm
\mscrh#Sm
\mscri#Sm
\mscrj#Sm
\mscrk#Sm
\mscrl#Sm
\mscrm#Sm
\mscrn#Sm
\mscro#Sm
\mscrp#Sm
\mscrq#Sm
\mscrr#Sm
\mscrs#Sm
\mscrt#Sm
\mscru#Sm
\mscrv#Sm
\mscrw#Sm
\mscrx#Sm
\mscry#Sm
\mscrz#Sm
\neovnwarrow#Sm
\neovsearrow#Sm
\neswarrow#Sm
\neuter#Sm
\nHdownarrow#Sm
\nhpar#Sm
\nHuparrow#Sm
\nhVvert#Sm
\niobar#Sm
\nis#Sm
\nisd#Sm
\Not#Sm
\npolint#Sm
\nvinfty#Sm
\nvleftarrow#Sm
\nVleftarrow#Sm
\nvLeftarrow#Sm
\nvleftarrowtail#Sm
\nVleftarrowtail#Sm
\nvleftrightarrow#Sm
\nVleftrightarrow#Sm
\nvLeftrightarrow#Sm
\nvrightarrow#Sm
\nVrightarrow#Sm
\nvRightarrow#Sm
\nvrightarrowtail#Sm
\nVrightarrowtail#Sm
\nvtwoheadleftarrow#Sm
\nVtwoheadleftarrow#Sm
\nvtwoheadleftarrowtail#Sm
\nVtwoheadleftarrowtail#Sm
\nvtwoheadrightarrow#Sm
\nVtwoheadrightarrow#Sm
\nvtwoheadrightarrowtail#Sm
\nVtwoheadrightarrowtail#Sm
\nwovnearrow#Sm
\nwsearrow#Sm
\obar#Sm
\obot#Sm
\obslash#Sm
\ocommatopright{arg}#Sm
\odiv#Sm
\odotslashdot#Sm
\ogreaterthan#Sm
\olcross#Sm
\olessthan#Sm
\operp#Sm
\opluslhrim#Sm
\oplusrhrim#Sm
\Otimes#Sm
\otimeshat#Sm
\otimeslhrim#Sm
\otimesrhrim#Sm
\oturnedcomma{arg}#Sm
\parallelogram#Sm
\parallelogramblack#Sm
\parsim#Sm
\partialmeetcontraction#Sm
\pentagon#Sm
\pentagonblack#Sm
\perps#Sm
\pitchfork#Sm
\plusdot#Sm
\pluseqq#Sm
\plushat#Sm
\plussim#Sm
\plussubtwo#Sm
\plustrif#Sm
\pointint#Sm
\postalmark#Sm
\Prec#Sm
\precapprox#Sm
\preceqq#Sm
\precnapprox#Sm
\precneq#Sm
\precneqq#Sm
\profline#Sm
\profsurf#Sm
\PropertyLine#Sm
\prurel#Sm
\pullback#Sm
\pushout#Sm
\quarternote#Sm
\Question#Sm
\rangledot#Sm
\rangledownzigzagarrow#Sm
\rbag#Sm
\rblkbrbrak#Sm
\rBrace#Sm
\rbracklrtick#Sm
\rbrackubar#Sm
\rbrackurtick#Sm
\Rbrbrak#Sm
\rbrbrak#Sm
\rcurvyangle#Sm
\rdiagovfdiag#Sm
\rdiagovsearrow#Sm
\revangle#Sm
\revangleubar#Sm
\revemptyset#Sm
\revnmid#Sm
\rfbowtie#Sm
\rftimes#Sm
\rightanglemdot#Sm
\rightanglesqr#Sm
\rightarrowapprox#Sm
\rightarrowbackapprox#Sm
\rightarrowbar#Sm
\rightarrowbsimilar#Sm
\rightarrowdiamond#Sm
\rightarrowgtr#Sm
\rightarrowplus#Sm
\rightarrowshortleftarrow#Sm
\rightarrowsimilar#Sm
\rightarrowsupset#Sm
\rightarrowtriangle#Sm
\rightarrowx#Sm
\rightbkarrow#Sm
\rightcurvedarrow#Sm
\rightdasharrow#Sm
\rightdbltail#Sm
\rightdotarrow#Sm
\rightdowncurvedarrow#Sm
\rightfishtail#Sm
\rightharpoondownbar#Sm
\rightharpoonsupdown#Sm
\rightharpoonupbar#Sm
\rightharpoonupdash#Sm
\rightimply#Sm
\rightleftharpoonsdown#Sm
\rightleftharpoonsup#Sm
\rightmoon#Sm
\rightouterjoin#Sm
\rightpentagon#Sm
\rightpentagonblack#Sm
\righttail#Sm
\rightwavearrow#Sm
\ringplus#Sm
\rParen#Sm
\rparengtr#Sm
\Rparenless#Sm
\rppolint#Sm
\rrangle#Sm
\RRightarrow#Sm
\rrparenthesis#Sm
\rsolbar#Sm
\rsqhook#Sm
\rsub#Sm
\rtriltri#Sm
\ruledelayed#Sm
\rvboxline#Sm
\rvzigzag#Sm
\Rvzigzag#Sm
\sansLmirrored#Sm
\sansLturned#Sm
\scpolint#Sm
\scurel#Sm
\seovnearrow#Sm
\shortdowntack#Sm
\shortlefttack#Sm
\shortrightarrowleftarrow#Sm
\shortuptack#Sm
\shuffle#Sm
\simgE#Sm
\simgtr#Sm
\similarleftarrow#Sm
\similarrightarrow#Sm
\simlE#Sm
\simless#Sm
\simminussim#Sm
\simplus#Sm
\simrdots#Sm
\smallblacktriangleleft#Sm
\smallblacktriangleright#Sm
\smalltriangleleft#Sm
\smalltriangleright#Sm
\smashtimes#Sm
\smblkdiamond#Sm
\smblklozenge#Sm
\smeparsl#Sm
\smt#Sm
\smte#Sm
\smwhitestar#Sm
\smwhtlozenge#Sm
\sphericalangleup#Sm
\Sqcap#Sm
\Sqcup#Sm
\sqint#Sm
\sqlozenge#Sm
\squarebotblack#Sm
\squarecrossfill#Sm
\squarehfill#Sm
\squarehvfill#Sm
\squareleftblack#Sm
\squarellblack#Sm
\squarellquad#Sm
\squarelrblack#Sm
\squarelrquad#Sm
\squareneswfill#Sm
\squarenwsefill#Sm
\squarerightblack#Sm
\squaretopblack#Sm
\squareulblack#Sm
\squareulquad#Sm
\squareurblack#Sm
\squareurquad#Sm
\squarevfill#Sm
\squoval#Sm
\sslash#Sm
\strns#Sm
\subedot#Sm
\submult#Sm
\subrarr#Sm
\subsetapprox#Sm
\subsetcirc#Sm
\subsetdot#Sm
\subseteqq#Sm
\subsetneqq#Sm
\subsetplus#Sm
\subsim#Sm
\subsub#Sm
\subsup#Sm
\Succ#Sm
\succapprox#Sm
\succeqq#Sm
\succnapprox#Sm
\succneq#Sm
\succneqq#Sm
\sumint#Sm
\sun#Sm
\supdsub#Sm
\supedot#Sm
\suphsol#Sm
\suphsub#Sm
\suplarr#Sm
\supmult#Sm
\supsetapprox#Sm
\supsetcirc#Sm
\supsetdot#Sm
\supseteqq#Sm
\supsetneqq#Sm
\supsetplus#Sm
\supsim#Sm
\supsub#Sm
\supsup#Sm
\talloblong#Sm
\thermod#Sm
\threedangle#Sm
\threedotcolon#Sm
\tieinfty#Sm
\timesbar#Sm
\tminus#Sm
\toea#Sm
\tona#Sm
\topbot#Sm
\topcir#Sm
\topfork#Sm
\topsemicircle#Sm
\tosa#Sm
\towa#Sm
\tplus#Sm
\trapezium#Sm
\trianglecdot#Sm
\triangledown#Sm
\triangleleftblack#Sm
\triangleminus#Sm
\triangleodot#Sm
\triangleplus#Sm
\trianglerightblack#Sm
\triangles#Sm
\triangleserifs#Sm
\triangletimes#Sm
\triangleubar#Sm
\tripleplus#Sm
\trslash#Sm
\turnangle#Sm
\turnediota#Sm
\twocaps#Sm
\twocups#Sm
\twoheadleftarrowtail#Sm
\twoheadleftdbkarrow#Sm
\twoheadmapsfrom#Sm
\twoheadmapsto#Sm
\twoheadrightarrowtail#Sm
\twoheaduparrowcircle#Sm
\twonotes#Sm
\typecolon#Sm
\ularc#Sm
\ulblacktriangle#Sm
\ultriangle#Sm
\uminus#Sm
\upand#Sm
\uparrowbarred#Sm
\uparrowoncircle#Sm
\upbackepsilon#Sm
\updasharrow#Sm
\upDigamma#Sm
\updigamma#Sm
\updownarrowbar#Sm
\updownharpoonleftleft#Sm
\updownharpoonleftright#Sm
\updownharpoonrightleft#Sm
\updownharpoonrightright#Sm
\updownharpoonsleftright#Sm
\upfishtail#Sm
\upharpoonleftbar#Sm
\upharpoonrightbar#Sm
\upharpoonsleftright#Sm
\upin#Sm
\upint#Sm
\uprightcurvearrow#Sm
\urarc#Sm
\urblacktriangle#Sm
\urtriangle#Sm
\UUparrow#Sm
\Uuparrow#Sm
\varcarriagereturn#Sm
\varhexagon#Sm
\varhexagonblack#Sm
\varhexagonlrbonds#Sm
\varisinobar#Sm
\varisins#Sm
\varniobar#Sm
\varnis#Sm
\varstar#Sm
\vartriangle#Sm
\varVdash#Sm
\varveebar#Sm
\vBar#Sm
\Vbar#Sm
\vBarv#Sm
\vbrtri#Sm
\vDdash#Sm
\Vee#Sm
\veedot#Sm
\veedoublebar#Sm
\veemidvert#Sm
\veeodot#Sm
\veeonvee#Sm
\veeonwedge#Sm
\viewdata#Sm
\vrectangle#Sm
\vrectangleblack#Sm
\Vvert#Sm
\vysmblksquare#Sm
\vysmwhtsquare#Sm
\vzigzag#Sm
\Wedge#Sm
\wedgebar#Sm
\wedgedot#Sm
\wedgedoublebar#Sm
\wedgemidvert#Sm
\wedgeodot#Sm
\wedgeonwedge#Sm
\whitearrowupfrombar#Sm
\whiteinwhitetriangle#Sm
\whitepointerleft#Sm
\whitepointerright#Sm
\whitesquaretickleft#Sm
\whitesquaretickright#Sm
\whthorzoval#Sm
\whtvertoval#Sm
\wideangledown#Sm
\wideangleup#Sm
\xbsol#Sm
\xsol#Sm
\Yup#Sm
\Zbar#Sm
\zcmp#Sm
\zpipe#Sm
\zproject#Sm
