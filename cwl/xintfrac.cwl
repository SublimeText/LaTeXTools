# xintfrac package
# Matthew Bertucci 2022/06/12 for v1.4m

#include:xint

\xintTeXFromSci{%<A/B[n]%>}#m
\xintTeXFrac{%<A/B[n]%>}#m
\xintTeXsignedFrac{%<A/B[n]%>}#m
\xintTeXOver{%<A/B[n]%>}#m
\xintTeXFromScifracmacro{num}{den}#*
\xintTeXsignedOver{%<A/B[n]%>}#m
\xintLen{%<A/B[n]%>}
\xintNum{%<A/B[n]%>}
\xintRaw{%<A/B[n]%>}
\xintRawBraced{%<A/B[n]%>}
\xintiLogTen{%<A/B[n]%>}
\xintNumerator{%<A/B[n]%>}
\xintDenominator{%<A/B[n]%>}
\xintRawWithZeros{%<A/B[n]%>}
\xintREZ{%<A/B[n]%>}
\xintIrr{%<A/B[n]%>}
\xintPIrr{%<A/B[n]%>}
\xintJrr{%<A/B[n]%>}
\xintPRaw{%<A/B[n]%>}
\xintSPRaw{%<A/B[n]%>}#*
\xintFracToSci{%<A/B[n]%>}
\xintFracToDecimal{%<A/B[n]%>}
\xintDecToStringREZ{%<A/B[n]%>}
\xintDecToString{%<A/B[n]%>}
\xintTrunc{%<integer%>}{%<A/B[n]%>}
\xintXTrunc{%<integer%>}{%<A/B[n]%>}
\xintTFrac{%<A/B[n]%>}
\xintRound{%<integer%>}{%<A/B[n]%>}
\xintFloor{%<A/B[n]%>}
\xintCeil{%<A/B[n]%>}
\xintiTrunc{%<integer%>}{%<A/B[n]%>}
\xintTTrunc{%<A/B[n]%>}
\xintiRound{%<integer%>}{%<A/B[n]%>}
\xintiFloor{%<A/B[n]%>}
\xintiCeil{%<A/B[n]%>}
\xintE{%<A/B[n]%>}{%<integer%>}
\xintCmp{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintEq{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintNotEq{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintGeq{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintGt{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintLt{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintGtorEq{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintLtorEq{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintIsZero{%<A/B[n]%>}
\xintIsNotZero{%<A/B[n]%>}
\xintIsOne{%<A/B[n]%>}
\xintOdd{%<A/B[n]%>}
\xintEven{%<A/B[n]%>}
\xintifSgn{%<A/B[n]%>}{%<neg-code%>}{%<zero-code%>}{%<pos-code%>}
\xintifZero{%<A/B[n]%>}{%<zero-code%>}{%<not-zero-code%>}
\xintifNotZero{%<A/B[n]%>}{%<not-zero-code%>}{%<zero-code%>}
\xintifOne{%<A/B[n]%>}{%<one-code%>}{%<not-one-code%>}
\xintifOdd{%<A/B[n]%>}{%<odd-code%>}{%<even-code%>}
\xintifCmp{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}{%<less-code%>}{%<equal-code%>}{%<greater-code%>}
\xintifEq{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}{%<equals-code%>}{%<not-equals-code%>}
\xintifGt{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}{%<greater-code%>}{%<not-greater-code%>}
\xintifLt{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}{%<less-code%>}{%<not-less-code%>}
\xintifInt{%<A/B[n]%>}{%<integer-code%>}{%<not-integer-code%>}
\xintIsInt{%<A/B[n]%>}
\xintSgn{%<A/B[n]%>}
\xintSignBit{%<A/B[n]%>}
\xintOpp{%<A/B[n]%>}
\xintInv{%<A/B[n]%>}
\xintAbs{%<A/B[n]%>}
\xintAdd{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintSub{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintMul{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintDiv{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintDivFloor{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintMod{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintDivMod{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintDivTrunc{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintModTrunc{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintDivRound{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintSqr{%<A/B[n]%>}
\xintPow{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFac{%<A/B[n]%>}
\xintBinomial{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintPFactorial{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintMax{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintMin{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintMaxof{list}
\xintMinof{list}
\xintSum{list}
\xintPrd{list}
\xintGCD{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintLCM{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintGCDof{list}
\xintLCMof{list}
\xintDigits
\xinttheDigits
\xinttheGuardDigits#*
\xintSetDigits{expr}
\xintFloat{%<A/B[n]%>}
\xintFloat[%<digits%>]{%<A/B[n]%>}
\xintFloatBraced{%<A/B[n]%>}
\xintFloatBraced[%<digits%>]{%<A/B[n]%>}
\xintFloatZero
\xintFloatE{%<A/B[n]%>}
\xintFloatE[%<digits%>]{%<A/B[n]%>}
\xintFloatSciExp{%<A/B[n]%>}
\xintFloatSciExp[%<digits%>]{%<A/B[n]%>}
\xintFloatSignificand{%<A/B[n]%>}
\xintFloatSignificand[%<digits%>]{%<A/B[n]%>}
\xintPFloat{%<A/B[n]%>}
\xintPFloat[%<digits%>]{%<A/B[n]%>}
\xintPFloatZero
\xintPFloatE
\xintPFloatNoSciEmax
\xintPFloatNoSciEmin
\xintPFloatIntSuffix
\xintPFloatLengthOneSuffix
\xintPFloatMinTrimmed
\xintFloatToDecimal{%<A/B[n]%>}
\xintFloatToDecimal[%<digits%>]{%<A/B[n]%>}
\xintFloatAdd{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatAdd[%<digits%>]{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatSub{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatSub[%<digits%>]{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatMul{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatMul[%<digits%>]{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatSqr{%<A/B[n]%>}
\xintFloatSqr[%<digits%>]{%<A/B[n]%>}
\xintFloatDiv{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatDiv[%<digits%>]{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatPow{%<A/B[n]%>}{%<power%>}
\xintFloatPow[%<digits%>]{%<A/B[n]%>}{%<power%>}
\xintFloatPower{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatPower[%<digits%>]{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatSqrt{%<A/B[n]%>}
\xintFloatSqrt[%<digits%>]{%<A/B[n]%>}
\xintFloatFac{%<A/B[n]%>}
\xintFloatFac[%<digits%>]{%<A/B[n]%>}
\xintFloatBinomial{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatBinomial[%<digits%>]{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatPFactorial{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintFloatPFactorial[%<digits%>]{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}
\xintifFloatInt{%<A/B[n]%>}{%<integer-code%>}{%<not-integer-code%>}
\xintFloatIsInt{%<A/B[n]%>}
\xintFloatIntType{%<A/B[n]%>}

\XINTinFloat[%<digits%>]{%<A/B[n]%>}#*
\XINTinFloatS[%<digits%>]{%<A/B[n]%>}#*
\XINTinFloatFrac{%<A/B[n]%>}#*
\XINTinFloatAdd{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}#*
\XINTinFloatSub{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}#*
\XINTinFloatMul{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}#*
\XINTinFloatSqr{%<A/B[n]%>}#*
\XINTinFloatInv{%<A/B[n]%>}#*
\XINTinFloatDiv{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}#*
\XINTinFloatPow{%<A1/B1[n1]%>}{%<power%>}#*
\XINTinFloatPower{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}#*
\XINTinFloatFac[%<digits%>]{%<A/B[n]%>}#*
\XINTinFloatPFactorial{%<A/B[n]%>}#*
\XINTinFloatBinomial{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}#*
\XINTinFloatSqrt[%<digits%>]{%<A/B[n]%>}#*
\XINTinFloatE{%<A/B[n]%>}#*
\XINTinFloatMod{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}#*
\XINTinFloatDivFloor{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}#*
\XINTinFloatDivMod{%<A1/B1[n1]%>}{%<A2/B2[n2]%>}#*
\XINTinRandomFloatS[%<digits%>]#*
\XINTinRandomFloatSixteen#*
\XINTFloatiLogTen[%<digits%>]{%<A/B[n]%>}#*
\XINTinFloatMaxof{list}#*
\XINTinFloatMinof{list}#*
\XINTinFloatSum{list}#*
\XINTinFloatPrd{list}#*
\XINTinFloatdigits#*
\XINTinFloatSdigits#*
\XINTFloatiLogTendigits#*
\XINTinRandomFloatSdigits#*
\XINTinFloatFacdigits#*
\XINTinFloatSqrtdigits#*

\xintlen#S
\xinteq#S
\xintifeq#S
\xintgt#S
\xintlt#S
\xintgtoreq#S
\xintltoreq#S
\xintiszero#S
\xintisnotzero#S
\xintodd#S
\xinteven#S
\xintifsgn#S
\xintifcmp#S
\xintifeq#S
\xintifgt#S
\xintiflt#S
\xintifzero#S
\xintifnotzero#S
\xintifone#S
\xintifodd#S
\xintraw#S
\xintrawbraced#S
\xintilogten#S
\xintpraw#S
\xintspraw#S
\xintrawwithzeros#S
\xintdectostring#S
\xintdectostringrez#S
\xintfloor#S
\xintifloor#S
\xintceil#S
\xinticeil#S
\xintnumerator#S
\xintdenominator#S
\xintsignedfrac#S
\xintrez#S
\xinte#S
\xintirr#S
\xintpirr#S
\xintifint#S
\xintisint#S
\xintjrr#S
\xinttfrac#S
\xinttrunc#S
\xintitrunc#S
\xintttrunc#S
\xintround#S
\xintiround#S
\xintadd#S
\xintsub#S
\xintsum#S
\xintmul#S
\xintsqr#S
\xintipow#S
\xintpow#S
\xintfac#S
\xintbinomial#S
\xintipfactorial#S
\xintpfactorial#S
\xintprd#S
\xintdiv#S
\xintdivfloor#S
\xintdivtrunc#S
\xintdivround#S
\xintmodtrunc#S
\xintdivmod#S
\xintmod#S
\xintisone#S
\xintgeq#S
\xintmax#S
\xintmaxof#S
\xintmin#S
\xintminof#S
\xintcmp#S
\xintabs#S
\xintopp#S
\xintinv#S
\xintsgn#S
\xintsignbit#S
\xintgcd#S
\xintgcdof#S
\xintlcm#S
\xintlcmof#S
\XINTdigits#S
\XINTguarddigits#S
\xintfloat#S
\xintfloatbraced#S
\xintpfloatsciexp#S
\xintfloatsignificand#S
\XINTinfloat#S
\XINTinfloatS#S
\XINTfloatilogten#S
\xintpfloat#S
\xintfloattodecimal#S
\XINTinfloatfrac#S
\xintfloatadd#S
\XINTinfloatadd#S
\xintfloatsub#S
\XINTinfloatsub#S
\xintfloatmul#S
\XINTinfloatmul#S
\xintfloatsqr#S
\XINTinfloatsqr#S
\xintfloatdiv#S
\XINTinfloatdiv#S
\xintfloatpow#S
\XINTinfloatpow#S
\xintfloatpower#S
\XINTinfloatpower#S
\xintfloatfac#S
\XINTinfloatfac#S
\xintfloatpfactorial#S
\XINTinfloatpfactorial#S
\xintfloatbinomial#S
\XINTinfloatbinomial#S
\xintfloatsqrt#S
\XINTinfloatsqrt#S
\xintfloate#S
\XINTinfloate#S
\XINTinfloatmod#S
\XINTinfloatdivfloor#S
\XINTinfloatdivmod#S
\xintiffloatint#S
\xintfloatisint#S
\xintfloatinttype#S
\XINTinrandomfloatS#S

# deprecated
\xintTeXfromSci{%<A/B[n]%>}#Sm
