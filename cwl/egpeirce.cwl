# egpeirce package
# Matthew Bertucci 2023/03/21 for v1.0.0

#include:pstricks
#include:pst-node
#include:pst-text
#include:pstricks-add
#include:fancybox
#include:setspace
#include:calc
#include:graphicx
#include:everypage

\begin{inline}
\begin{inline}[stretch factor]
\end{inline}

\ifnotinline#S
\notinlinetrue
\notinlinefalse
\cut{text}
\ifellipsecut#S
\ellipsecuttrue
\ellipsecutfalse
\ontop{above \\ below%text}
\ontopl{above \\ below%text}
\ontopr{above \\ below%text}
\vcut{text}
\vvcut{text}
\scroll{left%text}{right%text}
\scroll*{left-width}{left%text}{middle-width}{right%text}{right-width}
\vscroll{top%text}{bottom%text}
\vscroll*{top-width}{top%text}{middle-width}{bottom%text}{bottom-width}
\inversescroll{left%text}{right%text}
\inversescroll*{left-width}{left%text}{middle-width}{right%text}{right-width}
\inversevscroll{top%text}{bottom%text}
\inversevscroll*{top-width}{top%text}{middle-width}{bottom%text}{bottom-width}
\longscroll{left%text}{right%text}
\longscroll*{left-width}{left%text}{middle-width}{right%text}{right-width}
\longvscroll{top%text}{bottom%text}
\longvscroll*{top-width}{top%text}{middle-width}{bottom%text}{bottom-width}
\longinversescroll{left%text}{right%text}
\longinversescroll*{left-width}{left%text}{middle-width}{right%text}{right-width}
\longinversevscroll{top%text}{bottom%text}
\longinversevscroll*{top-width}{top%text}{middle-width}{bottom%text}{bottom-width}
\nscroll{A,B,C,...%text}
\nscroll*{A,B,C,...%text}{center%text}
\nscrollwidth{factor}
\nscrolldistance{factor}
\defaultscrollwidth#*
\defaultscrolldistance#*
\defaultnscrollangle#*
\ifcolouredcuts#S
\colouredcutstrue
\colouredcutsfalse
\cutx{text}
\vcutx{text}
\vvcutx{text}
\hk{text}
\li{num1}{num2}
\li[gap spec]{num1}{num2}
\upright{num1}{num2}
\upright[gap spec]{num1}{num2}
\downright{num1}{num2}
\downright[gap spec]{num1}{num2}
\rightdown{num1}{num2}
\rightdown[gap spec]{num1}{num2}
\rightup{num1}{num2}
\rightup[gap spec]{num1}{num2}
\sligature{num1}{num2}
\sligature[gap spec]{num1}{num2}
\hsligature{num1}{num2}
\hsligature[gap spec]{num1}{num2}
\reflexivel{num1}{num2}
\reflexivel[gap spec]{num1}{num2}
\reflexiver{num1}{num2}
\reflexiver[gap spec]{num1}{num2}
\ifdebugmode#S
\debugmodetrue
\debugmodefalse
\gcut{text}
\gvcut{text}
\gvvcut{text}
\dbcut{text}
\pcut{text}
\ncut{text}
\shk{text}
\everygraphhook{arg}#*
\DefNodes{ref}{text}
\egatn
\vv
\cutwidth#L
\ligaturewidth#L
\cutxfillcolour
\cutxwidth#L
\cutxcolour
\xfillstyle
\cutcolour
\licolour
\scrollstretch
\commoncoefficient#*
\ifscaledsymbols#S
\scaledsymbolstrue
\scaledsymbolsfalse
\aggregate
\varaggregate
\Paries
\dragonhead
\reversedragonhead
\flatinfty
\fsymbol
\implicates
\cursiveimplicates
\varinclusion
\Ppropto
\Pinversepropto
\varwedge
\weirdone
\weirdtwo
\weirdthree
\weirdfour
\napierianbase
\Pratiocircdia
\boxxoperator{lines%keyvals}
#keyvals:\boxxoperator
t
b
l
r
#endkeyvals
\PPi
\PSigma
\heartright
\heartleft
\heartleftnofill
\heartdown
\heartup
\norlike
\inversenorlike
\whiskers{text1}{text2}{text3}
\inversewhiskers{text1}{text2}{text3}
\whiskersdot{text1}{text2}{text3}
\inversewhiskersdot{text1}{text2}{text3}
\agoverline{text}
\reverseagoverline{text}
\inlineagoverline{text}
\reverseinlineagoverline{text}
\croverline{text}
\reversecroverline{text}
\cuoverline{text}
\reversecuoverline{text}

# not documented
\ahk{arg1}{arg2}#S
\bydefaultblack#S
\correvlenght#S
\cutcenter#S
\cutlength#S
\cutskip#S
\dbgnolength#S
\doublescroll#S
\drawboxb#S
\drawboxl#S
\drawboxr#S
\drawboxt#S
\drawboxx#S
\EgDLength#S
\Egeee#S
\EgELength#S
\Egexpandcoord{arg1}{arg2}#S
\Egexpandcoordaux{arg1}{arg2}#S
\EgFLength#S
\egpopin#S
\egpopout#S
\Egshiftamount#S
\EgTbox#S
\Egtolastnode#S
\EgTTBox#S
\Egwholewidth#S
\forscale#S
\getcurrentfontsize#S
\halfpiwidth#S
\halfsigmawidth#S
\holdsthenormalsize#S
\iahk{arg}#S
\ifempty{arg}#S
\ifinnerloop#S
\ifintbox#S
\innerloopfalse#S
\innerlooptrue#S
\intboxfalse#S
\intboxtrue#S
\isitscaled#S
\iter{arg}#S
\lastnodewidth#S
\miniscule#S
\negboxx#S
\revcsymbollength#S
\revnsymbollength#S
\revsymbollength#S
\revtextlenght#S
\scalecoefficient#S
\scalesymbol{arg}#S
\scrollscroll#S
\scrollscrollalt#S
\scrolltokenlist#S
\sep#S
\TAGbox#S
\TAGHeight#S
\therheme#S
\thesubiter#S
\TTAGHeight#S
\TWidht#S
\varsubsumption#S
\whiskerswidth#S
\wholenscrollwidth#S
\wholeshiftamount#S
\xoperb#S
\xoperl#S
\xoperr#S
\xopert#S
\xscroll#S