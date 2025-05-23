# tkz-doc class
# Matthew Bertucci 2022/07/16 for v1.45c

#include:class-scrartcl
#include:tikz
# loads dvipsnames and svgnames options of xcolor
#include:tikzlibrarydecorations.shapes
#include:tikzlibrarydecorations.text
#include:tikzlibrarydecorations.pathreplacing
#include:tikzlibrarydecorations.pathmorphing
#include:tikzlibrarydecorations.markings
#include:tikzlibraryshadows
#include:ragged2e
#include:footmisc
#include:framed
#include:eso-pic
#include:scrlayer-scrpage
#include:datetime
#include:booktabs
#include:cellspace
#include:multicol

#keyvals:\documentclass/tkz-doc#c
cadre
#endkeyvals

\begin{NewEnvBox}{envname}
\end{NewEnvBox}
\begin{NewMacroBox}{csname}{suffix}
\end{NewMacroBox}

\ActivBoxName#*
\addbs{text}
\BS
\bslash
\cmd{cmd}
\cn{csname}
\cs{csname}
\defoffile{definition}
\env{envname}
\filedate#S
\fn{file}
\Iaccent{csname}{accents}
\Iarg{csname}{args}
\IargEnv{envname}{args}
\IargName{csname}{args}
\IargNameEnv{envname}{args}
\Ienv{envname}
\Ilib{library}
\Imacro{csname}
\Iopt{csname}{opts}
\IoptEnv{envname}{opts}
\IoptName{csname}{opts}
\IoptNameEnv{envname}{opts}
\Istyle{csname}{styles}
\IstyleEnv{csname}{styles}
\LATEX
\marg{arg}
\meta{arg}
\NameDist{distribution}
\NameFonct{function}
\NameLib{library}
\nameoffile{file}
\NamePack{package}
\NameSys{os}
\nodeshadowedone(x,y){arg}
\ntt
\oarg{arg}
\ooarg{arg}
\opt{option}
\PackageName#*
\PackageVersion#*
\parg{arg}
\pdf
\PGF     
\pgfname
\pkg{package}
\presentation
\restorelastnode#*
\savelastnode#*
\SectionFontStyle#*
\TAline{args}{text1}{text2}
\tbody
\TEX
\thead
\thecnt#*
\TIKZ
\tikzname
\titleinframe#*
\tkz
\tkzAttention{text}{skip}{color}
\tkzBomb
\tkzbox#*
\tkzcname{csname}
\tkzdft
\tkzHand
\tkzHandBomb
\tkzhname{csname}
\tkzimp{text}
\tkzname{text}
\tkzNameDist{distribution}
\tkzNameEnv{envname}
\tkzNameMacro{cmd}
\tkzNamePack{package}
\tkzNameSys{os}
\tkzSetUpColors[keyvals]
\tkzsubf{arg1}{arg2}
\tkzTitleFrame{text}
\tkzTwoBomb
\TMline{csname}{text1}{text2}
\TOenvline{opts}{text1}{text2}
\TOline{args}{text1}{text2}
\var{arg}
\vara{arg}
\varp{arg}

#keyvals:\tkzSetUpColors
background=#%color
text=#%color
#endkeyvals

# from tkz-doc.cfg
bistre#B
bistre#B
codebackground#B
codeonlybackground#B 
commencolor#B
fondpaille#B
framecolor#B
graphicbackground#B
myblue#B
numbackground#B
numcolor#B
pdffilecolor#B
pdflinkcolor#B
pdfurlcolor#B
sectioncolor#B
stringcolor#B
textcodecolor#B
textcolor#B
titlecolorbox#B

# from svgnames option of xcolor
AliceBlue#B
DarkKhaki#B
Green#B
LightSlateGrey#B
AntiqueWhite#B
DarkMagenta#B
GreenYellow#B
LightSteelBlue#B
Aqua#B
DarkOliveGreen#B
Grey#B
LightYellow#B
Aquamarine#B
DarkOrange#B
Honeydew#B
Lime#B
Azure#B
DarkOrchid#B
HotPink#B
LimeGreen#B
Beige#B
DarkRed#B
IndianRed#B
Linen#B
Bisque#B
DarkSalmon#B
Indigo#B
Magenta#B
Black#B
DarkSeaGreen#B
Ivory#B
Maroon#B
BlanchedAlmond#B
DarkSlateBlue#B
Khaki#B
MediumAquamarine#B
Blue#B
DarkSlateGray#B
Lavender#B
MediumBlue#B
BlueViolet#B
DarkSlateGrey#B
LavenderBlush#B
MediumOrchid#B
Brown#B
DarkTurquoise#B
LawnGreen#B
MediumPurple#B
BurlyWood#B
DarkViolet#B
LemonChiffon#B
MediumSeaGreen#B
CadetBlue#B
DeepPink#B
LightBlue#B
MediumSlateBlue#B
Chartreuse#B
DeepSkyBlue#B
LightCoral#B
MediumSpringGreen#B
Chocolate#B
DimGray#B
LightCyan#B
MediumTurquoise#B
Coral#B
DimGrey#B
LightGoldenrod#B
MediumVioletRed#B
CornflowerBlue#B
DodgerBlue#B
LightGoldenrodYellow#B
MidnightBlue#B
Cornsilk#B
FireBrick#B
LightGray#B
MintCream#B
Crimson#B
FloralWhite#B
LightGreen#B
MistyRose#B
Cyan#B
ForestGreen#B
LightGrey#B
Moccasin#B
DarkBlue#B
Fuchsia#B
LightPink#B
NavajoWhite#B
DarkCyan#B
Gainsboro#B
LightSalmon#B
Navy#B
DarkGoldenrod#B
GhostWhite#B
LightSeaGreen#B
NavyBlue#B
DarkGray#B
Gold#B
LightSkyBlue#B
OldLace#B
DarkGreen#B
Goldenrod#B
LightSlateBlue#B
Olive#B
DarkGrey#B
Gray#B
LightSlateGray#B
OliveDrab#B
Orange#B
Plum#B
Sienna#B
Thistle#B
OrangeRed#B
PowderBlue#B
Silver#B
Tomato#B
Orchid#B
Purple#B
SkyBlue#B
Turquoise#B
PaleGoldenrod#B
Red#B
SlateBlue#B
Violet#B
PaleGreen#B
RosyBrown#B
SlateGray#B
VioletRed#B
PaleTurquoise#B
RoyalBlue#B
SlateGrey#B
Wheat#B
PaleVioletRed#B
SaddleBrown#B
Snow#B
White#B
PapayaWhip#B
Salmon#B
SpringGreen#B
WhiteSmoke#B
PeachPuff#B
SandyBrown#B
SteelBlue#B
Yellow#B
Peru#B
SeaGreen#B
Tan#B
YellowGreen#B
Pink#B
Seashell#B
Teal#B

# from dvipsnames option of xcolor
Apricot#B
Aquamarine#B
Bittersweet#B
Black#B
Blue#B
BlueGreen#B
BlueViolet#B
BrickRed#B
Brown#B
BurntOrange#B
CadetBlue#B
CarnationPink#B
Cerulean#B
CornflowerBlue#B
Cyan#B
Dandelion#B
DarkOrchid#B
Emerald#B
ForestGreen#B
Fuchsia#B
Goldenrod#B
Gray#B
Green#B
GreenYellow#B
JungleGreen#B
Lavender#B
LimeGreen#B
Magenta#B
Mahogany#B
Maroon#B
Melon#B
MidnightBlue#B
Mulberry#B
NavyBlue#B
OliveGreen#B
Orange#B
OrangeRed#B
Orchid#B
Peach#B
Periwinkle#B
PineGreen#B
Plum#B
ProcessBlue#B
Purple#B
RawSienna#B
Red#B
RedOrange#B
RedViolet#B
Rhodamine#B
RoyalBlue#B
RoyalPurple#B
RubineRed#B
Salmon#B
SeaGreen#B
Sepia#B
SkyBlue#B
SpringGreen#B
Tan#B
TealBlue#B
Thistle#B
Turquoise#B
Violet#B
VioletRed#B
White#B
WildStrawberry#B
Yellow#B
YellowGreen#B
YellowOrange#B
