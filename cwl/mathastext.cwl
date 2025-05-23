# mathastext package
# Matthew Bertucci 2024/07/29 for v1.4b

#keyvals:\usepackage/mathastext#c
italic
frenchmath
ncccomma
decimalcomma
binarysemicolon
frenchmath*
frenchmath+
endash
noendash
emdash
alldelims
nolessnomore
nosmalldelims
noplus
nominus
noplusnominus
noparenthesis
nopunctuation
noequal
noexclam
asterisk
nospecials
basic
nohbar
activedigits
nodigits
defaultimath
noletters
mathaccents
unimathaccents
symboldelimiters
symboldigits
symbolgreek
symbolre
symbolmisc
symbol
symbolmax
eulerdigits
eulergreek
selfGreek
selfGreeks
LGRgreek
LGRgreeks
LGRgreek+
LGRgreeks+
itgreek
upgreek
itGreek
upGreek
defaultnormal
defaultrm
defaultbf
defaultit
defaultsf
defaulttt
defaultalphabets
defaultmathsizes
12pt
fouriervec
subdued
everymath
#endkeyvals

#ifOption:ncccomma
#include:ncccomma
#endif

#ifOption:decimalcomma
#include:decimalcomma
#endif

#ifOption:frenchmath*
#include:decimalcomma
#endif

#ifOption:frenchmath+
#include:ncccomma
#endif

\HUGE
\Mathastext
\Mathastext[name]
\mathastext#*
\mathastext[name]#*
\MTencoding{encoding}#*
\MTfamily{family}#*
\MTseries{series}#*
\MTshape{shape}#*
\MTlettershape{shape}#*
\MTWillUse{encoding}{family}{series}{shape}#*
\MTWillUse[lettershape]{encoding}{family}{series}{shape}#*
\MathastextWillUse#S
\Mathastextwilluse#S
\MTDeclareVersion{encoding}{family}{series}{shape}
\MTDeclareVersion[lettershape]{encoding}{family}{series}{shape}
\MTDeclareVersion[lettershape]{encoding}{family}{series}{shape}[other version]#*
\MathastextDeclareVersion#S
\MTboldvariant{variant}#*
\MTEulerScale{factor}#*
\MTSymbolScale{factor}#*

\MTmathactiveletters#*
\MTmathactiveLetters#*
\MTmathstandardletters#*
\MTicinmath#*
\MTnoicinmath#*
\MTICinmath#*
\MTnoICinmath#*
\MTicalsoinmathxx#*
\MTnormalasterisk#*
\MTactiveasterisk#*
\MTeasynonlettersobeymathxx#*
\MTeasynonlettersdonotobeymathxx#*
\MTnonlettersobeymathxx#*
\MTnonlettersdonotobeymathxx#*
\MTexplicitbracesobeymathxx#*
\MTexplicitbracesdonotobeymathxx#*
\MTnormalprime#*
\MTprimedoesskip#*
\MTeverymathdefault#*
\MTeverymathoff#*
\MTfixfonts#*
\MTdonotfixfonts#*
\MTfixmathfonts#*m
\MTsetmathskips{letter}{mu-glue-before}{mu-glue-after}#*
\MTunsetmathskips{letter}#*
\MTexistsskip{math glue}#*
\MTnormalexists#*
\MTexistsdoesskip#*
\MTforallskip{math glue}#*
\MTnormalforall#*
\MTforalldoesskip#*
\MTprimeskip{math glue}#*
\MTlowerast{dimen%l}#*
\MTmathoperatorsobeymathxx#*
\MTmathoperatorsdonotobeymathxx#*
\MTversion{math version}
\MTversion[text version]{math version}
\MTversion*{math version}
\Mathastextversion#S
\MTversion#S
\mathastextversion#S
\MTcustomgreek#*
\Mathastextcustomgreek#S
\MTstandardgreek#*
\Mathastextstandardgreek#S
\MTgreekupdefault#*
\MTgreekitdefault#*
\MTrecordstandardgreek#*
\MTresetnewmcodes#*
\MTcustomizenewmcodes#*
\MTmathactivedigits#*
\MTmathstandarddigits#*

\pmvec{arg}#m
\Mathnormal{arg}#*m
\Mathrm{arg}#*m
\Mathbf{arg}#*m
\Mathit{arg}#*m
\Mathsf{arg}#*m
\Mathtt{arg}#*m
\mathnormalbold{arg}#m
\Mathnormalbold{arg}#*m
\inodot#m
\jnodot#m

#ifOption:LGRgreek
\MTitgreek
\Mathastextitgreek#S
\MTupgreek
\Mathastextupgreek#S
\MTitGreek
\MathastextitGreek#S
\MTupGreek
\MathastextupGreek#S
\MTgreekfont{font family}
\Mathastextgreekfont#S
\Digamma#m
\digamma#m
\Alpha#m
\Beta#m
\Epsilon#m
\Zeta#m
\Eta#m
\Iota#m
\Kappa#m
\Mu#m
\Nu#m
\Omicron#m
\Rho#m
\Tau#m
\Chi#m
\omicron#m
\mathgreekup{letter}#m
\mathgreekit{letter}#m
\mathgreekupbold{letter}#m
\mathgreekitbold{letter}#m
\Alphaup#m
\Betaup#m
\Epsilonup#m
\Zetaup#m
\Etaup#m
\Iotaup#m
\Kappaup#m
\Muup#m
\Nuup#m
\Omicronup#m
\Rhoup#m
\Tauup#m
\Chiup#m
\Alphait#m
\Betait#m
\Epsilonit#m
\Zetait#m
\Etait#m
\Iotait#m
\Kappait#m
\Muit#m
\Nuit#m
\Omicronit#m
\Rhoit#m
\Tauit#m
\Chiit#m
\Digammaup#m
\Digammait#m
\Gammaup#m
\Deltaup#m
\Thetaup#m
\Lambdaup#m
\Xiup#m
\Piup#m
\Sigmaup#m
\Upsilonup#m
\Phiup#m
\Psiup#m
\Omegaup#m
\Gammait#m
\Deltait#m
\Thetait#m
\Lambdait#m
\Xiit#m
\Piit#m
\Sigmait#m
\Upsilonit#m
\Phiit#m
\Psiit#m
\Omegait#m
\alphaup#m
\betaup#m
\gammaup#m
\deltaup#m
\epsilonup#m
\zetaup#m
\etaup#m
\thetaup#m
\iotaup#m
\kappaup#m
\lambdaup#m
\muup#m
\nuup#m
\xiup#m
\omicronup#m
\piup#m
\rhoup#m
\sigmaup#m
\tauup#m
\upsilonup#m
\phiup#m
\chiup#m
\psiup#m
\omegaup#m
\digammaup#m
\varsigmaup#m
\alphait#m
\betait#m
\gammait#m
\deltait#m
\epsilonit#m
\zetait#m
\etait#m
\thetait#m
\iotait#m
\kappait#m
\lambdait#m
\muit#m
\nuit#m
\xiit#m
\omicronit#m
\piit#m
\rhoit#m
\sigmait#m
\tauit#m
\upsilonit#m
\phiit#m
\chiit#m
\psiit#m
\omegait#m
\digammait#m
\varsigmait#m
#endif

#ifOption:LGRgreeks
\MTitgreek
\Mathastextitgreek#S
\MTupgreek
\Mathastextupgreek#S
\MTitGreek
\MathastextitGreek#S
\MTupGreek
\MathastextupGreek#S
\MTgreekfont{font family}
\Mathastextgreekfont#S
\Digamma#m
\digamma#m
\Alpha#m
\Beta#m
\Epsilon#m
\Zeta#m
\Eta#m
\Iota#m
\Kappa#m
\Mu#m
\Nu#m
\Omicron#m
\Rho#m
\Tau#m
\Chi#m
\omicron#m
\mathgreekup{letter}#m
\mathgreekit{letter}#m
\mathgreekupbold{letter}#m
\mathgreekitbold{letter}#m
\Alphaup#m
\Betaup#m
\Epsilonup#m
\Zetaup#m
\Etaup#m
\Iotaup#m
\Kappaup#m
\Muup#m
\Nuup#m
\Omicronup#m
\Rhoup#m
\Tauup#m
\Chiup#m
\Alphait#m
\Betait#m
\Epsilonit#m
\Zetait#m
\Etait#m
\Iotait#m
\Kappait#m
\Muit#m
\Nuit#m
\Omicronit#m
\Rhoit#m
\Tauit#m
\Chiit#m
\Digammaup#m
\Digammait#m
\Gammaup#m
\Deltaup#m
\Thetaup#m
\Lambdaup#m
\Xiup#m
\Piup#m
\Sigmaup#m
\Upsilonup#m
\Phiup#m
\Psiup#m
\Omegaup#m
\Gammait#m
\Deltait#m
\Thetait#m
\Lambdait#m
\Xiit#m
\Piit#m
\Sigmait#m
\Upsilonit#m
\Phiit#m
\Psiit#m
\Omegait#m
\alphaup#m
\betaup#m
\gammaup#m
\deltaup#m
\epsilonup#m
\zetaup#m
\etaup#m
\thetaup#m
\iotaup#m
\kappaup#m
\lambdaup#m
\muup#m
\nuup#m
\xiup#m
\omicronup#m
\piup#m
\rhoup#m
\sigmaup#m
\tauup#m
\upsilonup#m
\phiup#m
\chiup#m
\psiup#m
\omegaup#m
\digammaup#m
\varsigmaup#m
\alphait#m
\betait#m
\gammait#m
\deltait#m
\epsilonit#m
\zetait#m
\etait#m
\thetait#m
\iotait#m
\kappait#m
\lambdait#m
\muit#m
\nuit#m
\xiit#m
\omicronit#m
\piit#m
\rhoit#m
\sigmait#m
\tauit#m
\upsilonit#m
\phiit#m
\chiit#m
\psiit#m
\omegait#m
\digammait#m
\varsigmait#m
#endif

#ifOption:LGRgreek+
\MTitgreek
\Mathastextitgreek#S
\MTupgreek
\Mathastextupgreek#S
\MTitGreek
\MathastextitGreek#S
\MTupGreek
\MathastextupGreek#S
\MTgreekfont{font family}
\Mathastextgreekfont#S
\Digamma#m
\digamma#m
\Alpha#m
\Beta#m
\Epsilon#m
\Zeta#m
\Eta#m
\Iota#m
\Kappa#m
\Mu#m
\Nu#m
\Omicron#m
\Rho#m
\Tau#m
\Chi#m
\omicron#m
\mathgreekup{letter}#m
\mathgreekit{letter}#m
\mathgreekupbold{letter}#m
\mathgreekitbold{letter}#m
\Alphaup#m
\Betaup#m
\Epsilonup#m
\Zetaup#m
\Etaup#m
\Iotaup#m
\Kappaup#m
\Muup#m
\Nuup#m
\Omicronup#m
\Rhoup#m
\Tauup#m
\Chiup#m
\Alphait#m
\Betait#m
\Epsilonit#m
\Zetait#m
\Etait#m
\Iotait#m
\Kappait#m
\Muit#m
\Nuit#m
\Omicronit#m
\Rhoit#m
\Tauit#m
\Chiit#m
\Digammaup#m
\Digammait#m
\Gammaup#m
\Deltaup#m
\Thetaup#m
\Lambdaup#m
\Xiup#m
\Piup#m
\Sigmaup#m
\Upsilonup#m
\Phiup#m
\Psiup#m
\Omegaup#m
\Gammait#m
\Deltait#m
\Thetait#m
\Lambdait#m
\Xiit#m
\Piit#m
\Sigmait#m
\Upsilonit#m
\Phiit#m
\Psiit#m
\Omegait#m
\alphaup#m
\betaup#m
\gammaup#m
\deltaup#m
\epsilonup#m
\zetaup#m
\etaup#m
\thetaup#m
\iotaup#m
\kappaup#m
\lambdaup#m
\muup#m
\nuup#m
\xiup#m
\omicronup#m
\piup#m
\rhoup#m
\sigmaup#m
\tauup#m
\upsilonup#m
\phiup#m
\chiup#m
\psiup#m
\omegaup#m
\digammaup#m
\varsigmaup#m
\alphait#m
\betait#m
\gammait#m
\deltait#m
\epsilonit#m
\zetait#m
\etait#m
\thetait#m
\iotait#m
\kappait#m
\lambdait#m
\muit#m
\nuit#m
\xiit#m
\omicronit#m
\piit#m
\rhoit#m
\sigmait#m
\tauit#m
\upsilonit#m
\phiit#m
\chiit#m
\psiit#m
\omegait#m
\digammait#m
\varsigmait#m
#endif

#ifOption:LGRgreeks+
\MTitgreek
\Mathastextitgreek#S
\MTupgreek
\Mathastextupgreek#S
\MTitGreek
\MathastextitGreek#S
\MTupGreek
\MathastextupGreek#S
\MTgreekfont{font family}
\Mathastextgreekfont#S
\Digamma#m
\digamma#m
\Alpha#m
\Beta#m
\Epsilon#m
\Zeta#m
\Eta#m
\Iota#m
\Kappa#m
\Mu#m
\Nu#m
\Omicron#m
\Rho#m
\Tau#m
\Chi#m
\omicron#m
\mathgreekup{letter}#m
\mathgreekit{letter}#m
\mathgreekupbold{letter}#m
\mathgreekitbold{letter}#m
\Alphaup#m
\Betaup#m
\Epsilonup#m
\Zetaup#m
\Etaup#m
\Iotaup#m
\Kappaup#m
\Muup#m
\Nuup#m
\Omicronup#m
\Rhoup#m
\Tauup#m
\Chiup#m
\Alphait#m
\Betait#m
\Epsilonit#m
\Zetait#m
\Etait#m
\Iotait#m
\Kappait#m
\Muit#m
\Nuit#m
\Omicronit#m
\Rhoit#m
\Tauit#m
\Chiit#m
\Digammaup#m
\Digammait#m
\Gammaup#m
\Deltaup#m
\Thetaup#m
\Lambdaup#m
\Xiup#m
\Piup#m
\Sigmaup#m
\Upsilonup#m
\Phiup#m
\Psiup#m
\Omegaup#m
\Gammait#m
\Deltait#m
\Thetait#m
\Lambdait#m
\Xiit#m
\Piit#m
\Sigmait#m
\Upsilonit#m
\Phiit#m
\Psiit#m
\Omegait#m
\alphaup#m
\betaup#m
\gammaup#m
\deltaup#m
\epsilonup#m
\zetaup#m
\etaup#m
\thetaup#m
\iotaup#m
\kappaup#m
\lambdaup#m
\muup#m
\nuup#m
\xiup#m
\omicronup#m
\piup#m
\rhoup#m
\sigmaup#m
\tauup#m
\upsilonup#m
\phiup#m
\chiup#m
\psiup#m
\omegaup#m
\digammaup#m
\varsigmaup#m
\alphait#m
\betait#m
\gammait#m
\deltait#m
\epsilonit#m
\zetait#m
\etait#m
\thetait#m
\iotait#m
\kappait#m
\lambdait#m
\muit#m
\nuit#m
\xiit#m
\omicronit#m
\piit#m
\rhoit#m
\sigmait#m
\tauit#m
\upsilonit#m
\phiit#m
\chiit#m
\psiit#m
\omegait#m
\digammait#m
\varsigmait#m
#endif

#ifOption:eulergreek
\MathEuler{letter}#m
\MathEulerBold{letter}#m
\Digamma#m
\Alpha#m
\Beta#m
\Epsilon#m
\Zeta#m
\Eta#m
\Iota#m
\Kappa#m
\Mu#m
\Nu#m
\Omicron#m
\Rho#m
\Tau#m
\Chi#m
\omicron#m
#endif

#ifOption:selfGreek
\Digamma#m
\Alpha#m
\Beta#m
\Epsilon#m
\Zeta#m
\Eta#m
\Iota#m
\Kappa#m
\Mu#m
\Nu#m
\Omicron#m
\Rho#m
\Tau#m
\Chi#m
#endif

#ifOption:selfGreeks
\Digamma#m
\Alpha#m
\Beta#m
\Epsilon#m
\Zeta#m
\Eta#m
\Iota#m
\Kappa#m
\Mu#m
\Nu#m
\Omicron#m
\Rho#m
\Tau#m
\Chi#m
#endif

#ifOption:eulerdigits
\MathEuler{letter}#m
\MathEulerBold{letter}#m
#endif

#ifOption:fouriervec
\fouriervec{arg}#m
#endif

#ifOption:symboldelimiters
\MathPSymbol{arg}#m
#endif

#ifOption:symboldigits
\MathPSymbol{arg}#m
#endif

#ifOption:symbolgreek
\MathPSymbol{arg}#m
\Alpha#m
\Beta#m
\Epsilon#m
\Zeta#m
\Eta#m
\Iota#m
\Kappa#m
\Mu#m
\Nu#m
\Omicron#m
\Rho#m
\Tau#m
\Chi#m
\omicron#m
#endif

#ifOption:symbolre
\MathPSymbol{arg}#m
\DotTriangle#m
#endif

#ifOption:symbolmisc
\MathPSymbol{arg}#m
\implies#m
\impliedby#m
\shortiff#m
\longto#m
\inftypsy#m
\proptopsy#m
\MToriginalprod#*m
\MToriginalsum#*m
#endif

#ifOption:symbol
\MathPSymbol{arg}#m
\Alpha#m
\Beta#m
\Epsilon#m
\Zeta#m
\Eta#m
\Iota#m
\Kappa#m
\Mu#m
\Nu#m
\Omicron#m
\Rho#m
\Tau#m
\Chi#m
\omicron#m
\implies#m
\impliedby#m
\shortiff#m
\longto#m
\inftypsy#m
\proptopsy#m
\DotTriangle#m
\MToriginalprod#*m
\MToriginalsum#*m
#endif

#ifOption:symbolmax
\MathPSymbol{arg}#m
\Alpha#m
\Beta#m
\Epsilon#m
\Zeta#m
\Eta#m
\Iota#m
\Kappa#m
\Mu#m
\Nu#m
\Omicron#m
\Rho#m
\Tau#m
\Chi#m
\omicron#m
\implies#m
\impliedby#m
\shortiff#m
\longto#m
\inftypsy#m
\proptopsy#m
\DotTriangle#m
\MToriginalprod#*m
\MToriginalsum#*m
#endif
