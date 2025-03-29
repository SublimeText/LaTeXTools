# glossaries-extra-bib2gls package
# Matthew Bertucci 2025/02/09 for v1.56

\dgls{label}#r
\dgls[options%keyvals]{label}#r
\dgls{label}[insert]#*r
\dgls[options%keyvals]{label}[insert]#*r
\dGls{label}#r
\dGls[options%keyvals]{label}#r
\dGls{label}[insert]#*r
\dGls[options%keyvals]{label}[insert]#*r
\dGLS{label}#r
\dGLS[options%keyvals]{label}#r
\dGLS{label}[insert]#*r
\dGLS[options%keyvals]{label}[insert]#*r
\dglspl{label}#r
\dglspl[options%keyvals]{label}#r
\dglspl{label}[insert]#*r
\dglspl[options%keyvals]{label}[insert]#*r
\dGlspl{label}#r
\dGlspl[options%keyvals]{label}#r
\dGlspl{label}[insert]#*r
\dGlspl[options%keyvals]{label}[insert]#*r
\dGLSpl{label}#r
\dGLSpl[options%keyvals]{label}#r
\dGLSpl{label}[insert]#*r
\dGLSpl[options%keyvals]{label}[insert]#*r
\dglslink{label}{link text}#r
\dglslink[options%keyvals]{label}{link text}#r
\dGlslink{label}{link text}#r
\dGlslink[options%keyvals]{label}{link text}#r
\dglsdisp{label}{link text}#r
\dglsdisp[options%keyvals]{label}{link text}#r
\dGlsdisp{label}{link text}#r
\dGlsdisp[options%keyvals]{label}{link text}#r
\dglsfield{label}{field-label}{text}#r
\dglsfield[options%keyvals]{label}{field-label}{text}#r
\dGlsfield{label}{field-label}{text}#r
\dGlsfield[options%keyvals]{label}{field-label}{text}#r
\dGLSfield{label}{field-label}{text}#r
\dGLSfield[options%keyvals]{label}{field-label}{text}#r

\newdglsfield{field}{cs%cmd}#d
\newdglsfield[default-options%keyvals]{field}{cs%cmd}#d
\newdglsfieldlike{field}{cs%cmd}{Cs%cmd}{CS%cmd}#d
\newdglsfieldlike[default-options%keyvals]{field}{cs%cmd}{Cs%cmd}{CS%cmd}#d

#keyvals:\dgls#c,\dGls#c,\dGLS#c,\dglspl#c,\dGlspl#c,\dGLSpl#c,\dglslink#c,\dGlslink#c,\dglsdisp#c,\dGlsdisp#c,\dglsfield#c,\dGlsfield#c,\dGLSfield#c,\newdglsfield#c,\newdglsfieldlike#c
# glossaries-extra options
hyperoutside#true,false
textformat=%<csname%>
innertextformat=%<csname%>
postunset=#global,local,none
prereset
prereset=#global,local,none
preunset=#global,local,none
noindex#true,false
wrgloss=#before,after
thevalue=%<location%>
theHvalue=%<the-H-value%>
prefix=%<link-prefix%>
# glossaries options
hyper#true,false
format=%<csname%>
counter=%<counter%>
local#true,false
#endkeyvals

\glsxtrmultientryadjustedname{sublist1}{name}{sublist2}{label}#*r
\Glsxtrmultientryadjustedname{sublist1}{name}{sublist2}{label}#*r
\GlsXtrmultientryadjustedname{sublist1}{name}{sublist2}{label}#*r
\GLSxtrmultientryadjustedname{sublist1}{name}{sublist2}{label}#*r
\glsxtrmultientryadjustednamesep{pre label}{post label}#*
\glsxtrmultientryadjustednamepresep{pre label}{post label}#*
\glsxtrmultientryadjustednamepostsep{pre label}{post label}#*
\glsxtrmultientryadjustednamefmt{text}#*
\Glsxtrmultientryadjustednamefmt{text}#*
\GlsXtrmultientryadjustednamefmt{text}#*
\GLSxtrmultientryadjustednamefmt{text}#*
\glsxtrmultientryadjustednameother{label}#*r
\Glsxtrmultientryadjustednameother{label}#*r
\GlsXtrmultientryadjustednameother{label}#*r
\GLSxtrmultientryadjustednameother{label}#*r
\glsxtrprovidecommand{cmd}{definition}#*d
\glsxtrprovidecommand{cmd}[args]{definition}#*d
\glsxtrprovidecommand{cmd}[args][default]{definition}#*d
\glsrenewcommand{cmd}{definition}#*
\glsrenewcommand{cmd}[args]{definition}#*
\glsrenewcommand{cmd}[args][default]{definition}#*
\GlsXtrIndexCounterLink{text}{label}#*
\GlsXtrDualBackLink{text}{label}#*r
\GlsXtrDualField#*
\glsxtrSetWidest{type}{level}{text}#*
\glsxtrSetWidestFallback{max depth}{list}#*
\glsxtrdisplaysupploc{prefix}{counter}{format}{src}{location}#*
\glsxtrmultisupplocation{location}{src}{format}#*
\glsxtrdisplaylocnameref{prefix}{counter}{format}{location}{title%text}{href}{hcounter}{file}#*
\glsxtrnamereflink{format}{title%text}{target}{file}#*
\glsxtrfmtinternalnameref{target}{format}{title%text}#*
\glsxtrfmtexternalnameref{target}{format}{title%text}{file}#*
\glsxtrnameloclink{prefix}{counter}{format}{location}{title%text}{file}#*
\glshex#*
\glscapturedgroup#*
\GlsXtrResourceInitEscSequences#*
\GlsXtrIfHasNonZeroChildCount{label}{true}{false}#*r
\GlsXtrBibTeXEntryAliases#*
\GlsXtrProvideBibTeXFields#*
\glsxtrcontrolrules#*
\glsxtrspacerules#*
\glsxtrnonprintablerules#*
\glsxtrcombiningdiacriticrules#*
\glsxtrcombiningdiacriticIrules#*
\glsxtrcombiningdiacriticIIrules#*
\glsxtrcombiningdiacriticIIIrules#*
\glsxtrcombiningdiacriticIVrules#*
\glsxtrcontrolIrules#*
\glsxtrcontrolIIrules#*
\glsxtrhyphenrules#*
\glsxtrgeneralpuncrules#*
\glsxtrgeneralpuncIrules#*
\glsxtrcurrencyrules#*
\glsxtrgeneralpuncIIrules#*
\glsxtrdigitrules#*
\glsxtrBasicDigitrules#*
\glsxtrSubScriptDigitrules#*
\glsxtrSuperScriptDigitrules#*
\glsxtrfractionrules#*
\glsxtrGeneralLatinIrules#*
\glsxtrGeneralLatinIIrules#*
\glsxtrGeneralLatinIIIrules#*
\glsxtrGeneralLatinIVrules#*
\glsxtrGeneralLatinVrules#*
\glsxtrGeneralLatinVIrules#*
\glsxtrGeneralLatinVIIrules#*
\glsxtrGeneralLatinVIIIrules#*
\glsxtrLatinA#*
\glsxtrLatinE#*
\glsxtrLatinH#*
\glsxtrLatinK#*
\glsxtrLatinI#*
\glsxtrLatinL#*
\glsxtrLatinM#*
\glsxtrLatinN#*
\glsxtrLatinO#*
\glsxtrLatinP#*
\glsxtrLatinS#*
\glsxtrLatinT#*
\glsxtrLatinX#*
\glsxtrLatinEszettSs#*
\glsxtrLatinEszettSz#*
\glsxtrLatinEth#*
\glsxtrLatinThorn#*
\glsxtrLatinAELigature#*
\glsxtrLatinOELigature#*
\glsxtrLatinOslash#*
\glsxtrLatinLslash#*
\glsxtrLatinWynn#*
\glsxtrLatinInsularG#*
\glsxtrLatinSchwa#*
\glsxtrLatinAA#*
\glsxtrMathGreekIrules#*
\glsxtrMathGreekIIrules#*
\glsxtrMathUpGreekIrules#*
\glsxtrMathUpGreekIIrules#*
\glsxtrMathItalicGreekIrules#*
\glsxtrMathItalicGreekIIrules#*
\glsxtrMathItalicUpperGreekIrules#*
\glsxtrMathItalicUpperGreekIIrules#*
\glsxtrMathItalicLowerGreekIrules#*
\glsxtrMathItalicLowerGreekIIrules#*
\glsxtrMathItalicPartial#*
\glsxtrMathItalicNabla#*
\Alpha#*
\Beta#*
\Epsilon#*
\Zeta#*
\Eta#*
\Iota#*
\Kappa#*
\Mu#*
\Nu#*
\Omicron#*
\Rho#*
\Tau#*
\Chi#*
\Digamma#*
\omicron#*
\CurrentTrackedScript#*
\glsxtrMathItalicAlpha#*
\glsxtrMathItalicBeta#*
\glsxtrMathItalicChi#*
\glsxtrMathItalicDelta#*
\glsxtrMathItalicEpsilon#*
\glsxtrMathItalicEta#*
\glsxtrMathItalicGamma#*
\glsxtrMathItalicIota#*
\glsxtrMathItalicKappa#*
\glsxtrMathItalicLambda#*
\glsxtrMathItalicMu#*
\glsxtrMathItalicNu#*
\glsxtrMathItalicOmega#*
\glsxtrMathItalicOmicron#*
\glsxtrMathItalicPhi#*
\glsxtrMathItalicPi#*
\glsxtrMathItalicPsi#*
\glsxtrMathItalicRho#*
\glsxtrMathItalicSigma#*
\glsxtrMathItalicTau#*
\glsxtrMathItalicTheta#*
\glsxtrMathItalicUpsilon#*
\glsxtrMathItalicXi#*
\glsxtrMathItalicZeta#*
\glsxtrUpAlpha#*
\glsxtrUpBeta#*
\glsxtrUpChi#*
\glsxtrUpDelta#*
\glsxtrUpDigamma#*
\glsxtrUpEpsilon#*
\glsxtrUpEta#*
\glsxtrUpGamma#*
\glsxtrUpIota#*
\glsxtrUpKappa#*
\glsxtrUpLambda#*
\glsxtrUpMu#*
\glsxtrUpNu#*
\glsxtrUpOmega#*
\glsxtrUpOmicron#*
\glsxtrUpPhi#*
\glsxtrUpPi#*
\glsxtrUpPsi#*
\glsxtrUpRho#*
\glsxtrUpSigma#*
\glsxtrUpTau#*
\glsxtrUpTheta#*
\glsxtrUpUpsilon#*
\glsxtrUpXi#*
\glsxtrUpZeta#*
\IfTeXParserLib{TeX-parser-lib-code}{TeX-code}#*
\IfNotBibGls{LaTeX code}{bib2gls code}#*
\glshashchar#*
\glsxtrrecentanchor#*
\glsxtrlocationanchor#*
\glsxtractualanchor#*
\glsxtrsetactualanchor{counter}#*
\glsxtrtitlednamereflink{format}{location}{title%text}{file}#*
\glsxtrequationlocfmt{location}{title%text}#*
\glsxtrwrglossarylocfmt{location}{title%text}#*
\glsxtraddlabelprefix{prefix}#*
\glsxtrprependlabelprefix{prefix}#*
\glsxtrclearlabelprefixes#*
\glsxtrifinlabelprefixlist{prefix}{true}{false}#*
\ifGlsXtrPrefixLabelFallbackLast#*
\GlsXtrPrefixLabelFallbackLasttrue#*
\GlsXtrPrefixLabelFallbackLastfalse#*
\dglsfieldcurrentfieldlabel#*
\dglsfieldfallbackfieldlabel#*
\dglsfieldactualfieldlabel#*
\glsxtrIgnorableRules#*
\glsxtrGeneralInitRules#*
\glsxtrgeneralpuncmarksrules#*
\glsxtrgeneralpuncaccentsrules#*
\glsxtrgeneralpuncquoterules#*
\glsxtrgeneralpuncbracketrules#*
\glsxtrgeneralpuncsignrules#*
\glsxtrGeneralLatinAtoMrules#*
\glsxtrGeneralLatinNtoZrules#*
\glsxtrGeneralLatinAtoGrules#*
\glsxtrGeneralLatinHtoMrules#*
\glsxtrGeneralLatinNtoSrules#*
\glsxtrGeneralLatinTtoZrules#*
\glsxtrGeneralPuncRules#*
\glsxtrhyphenIrules#*
\glsxtrhyphenIIrules#*
\glsxtrminusrules#*
\glsxtrgeneralpuncdotrules#*
\glsxtrgeneralpuncbracketIrules#*
\glsxtrgeneralpuncbracketIIrules#*
\glsxtrgeneralpuncbracketIIIrules#*
\glsxtrgeneralpuncbracketIVrules#*
\glsxtrgeneralpuncIIIrules#*
