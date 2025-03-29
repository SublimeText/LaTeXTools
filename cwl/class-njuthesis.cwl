# njuthesis class
# Matthew Bertucci 2024/04/22 for v1.4.1

#include:xtemplate
#include:class-ctexbook
#include:geometry
#include:fancyhdr
#include:footmisc
#include:setspace
#include:mathtools
#include:unicode-math
#include:booktabs
#include:caption
#include:graphicx
#include:enumitem
#include:hyperref
#include:cleveref
#include:emptypage
#include:xeCJKfntef
#include:lua-ul
#include:tabularray
#include:biblatex
# loads style=gb7714-2015 option of biblatex
#include:ntheorem
# loads thmmarks option of ntheorem
#include:njuvisual

#keyvals:\documentclass/njuthesis#c
type=#bachelor,master,doctor,postdoc
degree=#academic,professional
nl-cover#true,false
decl-page#true,false
oneside
twoside
draft
anonymous
anonymous-mode/no-nju#true,false
biblatex#true,false
cleveref#true,false
ntheorem#true,false
enumitem#true,false
footmisc#true,false
unicode-math#true,false
minimal
config={%<文件%>}
cjk-font=#fandol,founder,mac,macoffice,noto,source,win,none
latin-font=#fandol,gyre,mac,macoffice,win,none
math-font=#asana,cambria,fira,garamond,lm,libertinus,stix,bonum,dejavu,pagella,schola,termes,xits,none
#endkeyvals

\njusetup{设置项%keyvals}
\njusetup[键路径]{设置项%keyvals}

#keyvals:\njusetup#c
info/title={%<标题%>}
info/title*={%<英文标题%>}
info/keywords={%<关键词%>}
info/keywords*={%<英文关键词%>}
info/grade={%<20XX%>}
info/student-id={%<学号%>}
info/author={%<你的名字%>}
info/author*={%<姓名拼音%>}
info/department={%<院系%>}
info/department*={%<院系%>}
info/major={%<专业%>}
info/major={%<专业%>,%<专业全称%>}
info/major*={%<专业%>}
info/field={%<方向%>}
info/field*={%<方向%>}
info/supervisor={%<导师姓名,职称%>}
info/supervisor*={%<导师英文全称%>}
info/supervisor-ii={%<第二导师姓名,职称%>}
info/supervisor-ii*={%<第二导师英文全称%>}
info/submit-date={%<yyyy-mm-dd%>}
info/defend-date={%<yyyy-mm-dd%>}
info/confer-date={%<yyyy-mm-dd%>}
info/bottom-date={%<yyyy-mm-dd%>}
info/chairman={%<答辩主席姓名职称%>}
info/reviewer={%<答辩评委姓名职称%>}
info/clc={%<中图分类号%>}
info/udc={%<udc%>}
info/secret-level={%<密级%>}
info/supervisor-contact={%<导师联系方式%>}
info/school-code={%<number%>}
info/degree={%<中文学位名%>}
info/degree*={%<英文学位名%>}
header/content={{%<位置%>}{%<内容%>}%<,{位置}{内容},...%>}
header/content*={{%<位置%>}{%<内容%>}%<,{位置}{内容},...%>}
footer/content={{%<位置%>}{%<内容%>}%<,{位置}{内容},...%>}
footer/content*={{%<位置%>}{%<内容%>}%<,{位置}{内容},...%>}
image/path={%<{路径1},{路径2},...%>}
image/nju-emblem={%<文件%>}
image/nju-name={%<文件%>}
footnote/style=#plain,pifont,circled,circled*
footnote/hang#true,false
footnote/circledtext-option=%<选项列表%>
math/style=#TeX,ISO,GB
math/integral=#upright,slanted
math/integral-limits#true,false
math/less-than-or-equal=#slanted,horizontal
math/math-ellipsis=#centered,lower
math/partial=#upright,italic
math/real-part=#roman,fraktur
math/vector=#boldfont,arrow
math/uppercase-greek=#upright,italic
theorem/style=#plain,break,change,margin,empty
theorem/header-font={%<头部字体格式%>}
theorem/body-font={%<内部字体格式%>}
theorem/qed-symbol=%<证毕符号%>
theorem/counter=%<counter%>
theorem/share-counter#true,false
theorem/type={%<{环境名,类型标识}{头名称},...%>}
theorem/define
label-sep/figure=%<符号%>
label-sep/table=%<符号%>
label-sep/equation=%<符号%>
bib/style=%<自定义样式%>
bib/option={%<选项列表%>}
bib/resource={%<文件%>}
abstract/toc-entry#true,false
abstract/underline#true,false
abstract/title-style=#strict,centered,natural
tableofcontents/dotline=#chapter,section
tableofcontents/toc-entry#true,false
listoffigures/toc-entry#true,false
listoftables/toc-entry#true,false
#endkeyvals

\njuline{文字%text}
\begin{abstract}
\end{abstract}
\begin{abstract*}
\end{abstract*}
\begin{preface}
\end{preface}
\begin{notation}
\begin{notation}[说明宽度]
\begin{notation}[说明宽度][符号宽度]
\end{notation}
\begin{notation*}
\begin{notation*}[说明宽度]
\begin{notation*}[说明宽度][符号宽度]
\end{notation*}
\begin{acknowledgement}
\end{acknowledgement}
\njuchapter{title}#L1
\njupaperlist{bibid}#C
\njupaperlist[标题]{bibid}#C
\njusetname{名称}{内容%text}
\njusetname{名称}[变体]{内容%text}
\njusetname*{名称}{内容%text}
\njusetname*{名称}[变体]{内容%text}
\njusettext{名称}{内容%text}
\njusettext{名称}[变体]{内容%text}
\njusettext*{名称}{内容%text}
\njusettext*{名称}[变体]{内容%text}
\njusetlength{名称}{长度}
\njusetlength*{名称}{长度}
\njusetformat{名称}{样式}
\bigger#*

# requires theorem/define option of \njusetup
\begin{axiom}
\begin{axiom}[heading%text]
\end{axiom}
\begin{corollary}
\begin{corollary}[heading%text]
\end{corollary}
\begin{definition}
\begin{definition}[heading%text]
\end{definition}
\begin{example}
\begin{example}[heading%text]
\end{example}
\begin{lemma}
\begin{lemma}[heading%text]
\end{lemma}
\begin{proof}
\begin{proof}[heading%text]
\end{proof}
\begin{theorem}
\begin{theorem}[heading%text]
\end{theorem}

# from thmmarks option of ntheorem
\theoremsymbol{symbol}
\theendNonectr#S
\thecurrNonectr#S
\ifsetendmark#S
\setendmarktrue#S
\setendmarkfalse#S

# from style=gb7714-2015 option of biblatex
#ifOption:style=gb7714-2015
#keyvals:\usepackage/biblatex#c,\ExecuteBibliographyOptions#c
# from gb7714-2015.bbx
citexref#true,false
gbmedium#true,false
gbannote#true,false
gbfieldtype#true,false
gbfootbibfmt#true,false
gbfnperpage#true,false
gbfootbib#true,false
gbstyle#true,false
gbtype#true,false
gbcodegbk#true,false
gbstrict#true,false
gbtitlelink#true,false
gbctexset#true,false
gbnoauthor#true,false
gbfieldstd#true,false
gbpub#true,false
gbpunctin#true,false
gblanorder=#chineseahead,englishahead,%<string%>
gbcitelocal=#gb7714-2015,chinese,english
gbbiblocal=#gb7714-2015,chinese,english
gblocal=#gb7714-2015,chinese,english
gbbiblabel=#bracket,parens,plain,dot,box,circle
gbnamefmt=#uppercase,lowercase,givenahead,familyahead,pinyin,quanpin,reverseorder
gbalign=#right,left,center,gb7714-2015,gb7714-2015ay
# from gb7714-2015.cbx
gblabelref#true,false
gbcitecomp#true,false
gbcitelabel=#bracket,parens,plain,dot,box,circle
#endkeyvals
# from gb7714-2015.bbx
#include:xstring
\versionofgbtstyle#S
\versionofbiblatex#S
\defversion{arg1}{arg2}{arg3}#S
\switchversion{arg1}{arg2}#S
\testCJKfirst{field}#*
\multivolparser{arg}#*
\multinumberparser{arg}#*
\BracketLift#*
\gbleftparen#*
\gbrightparen#*
\gbleftbracket#*
\gbrightbracket#*
\execgbfootbibfmt#*
\SlashFont#*
\footbibmargin#*
\footbiblabelsep#*
\execgbfootbib#*
\thegbnamefmtcase#*
\mkgbnumlabel{arg}#*
\thegbalignlabel#*
\thegbcitelocalcase#*
\thegbbiblocalcase#*
\lancnorder#S
\lanjporder#S
\lankrorder#S
\lanenorder#S
\lanfrorder#S
\lanruorder#S
\execlanodeah#*
\thelanordernum#*
\execlanodudf{string}#*
\setlocalbibstring{string}{text}
\setlocalbiblstring{string}{text}
\dealsortlan#*
\bibitemindent#*
\biblabelextend#*
\setaligngbstyle#*
\lengthid#*
\lengthlw#*
\itemcmd#*
\setaligngbstyleay#*
\publocpunct#*
\bibtitlefont#*
\bibauthorfont#*
\bibpubfont#*
\execgbfdfmtstd#*
\aftertransdelim#*
\gbcaselocalset#*
\gbpinyinlocalset#*
\gbquanpinlocalset#*
\defdoublelangentry{match}{fieldvalue}
\entrykeya#S
\entrykeyb#S
\userfieldabcde#S
# from gb7714-2015.cbx
\mkbibleftborder#*
\mkbibrightborder#*
\mkbibsuperbracket{text}#*
\mkbibsuperscriptusp{text}#*
\upcite{bibid}#*C
\upcite[postnote]{bibid}#*C
\upcite[prenote][postnote]{bibid}#*C
\pagescite{bibid}#C
\pagescite[postnote]{bibid}#C
\pagescite[prenote][postnote]{bibid}#C
\yearpagescite{bibid}#C
\yearpagescite[postnote]{bibid}#C
\yearpagescite[prenote][postnote]{bibid}#C
\yearcite{bibid}#C
\yearcite[postnote]{bibid}#C
\yearcite[prenote][postnote]{bibid}#C
\authornumcite{bibid}#C
\authornumcite[postnote]{bibid}#C
\authornumcite[prenote][postnote]{bibid}#C
\citet{bibid}#*C
\citet[postnote]{bibid}#*C
\citet[prenote][postnote]{bibid}#*C
\citep{bibid}#*C
\citep[postnote]{bibid}#*C
\citep[prenote][postnote]{bibid}#*C
\citetns{bibid}#*C
\citetns[postnote]{bibid}#*C
\citetns[prenote][postnote]{bibid}#*C
\citepns{bibid}#*C
\citepns[postnote]{bibid}#*C
\citepns[prenote][postnote]{bibid}#*C
\inlinecite{bibid}#*C
\inlinecite[postnote]{bibid}#*C
\inlinecite[prenote][postnote]{bibid}#*C
\citec{bibid}#C
\citec[postnote]{bibid}#C
\citec[prenote][postnote]{bibid}#C
\citecs{bibid}{bibid}#C
\citecs(post){bibid}{bibid}#*C
\citecs(pre)(post){bibid}{bibid}#C
\citecs(pre)(post)[post]{bibid}[post]{bibid}#*C
\citecs[post]{bibid}[post]{bibid}#*C
\citecs[pre][post]{bibid}[pre][post]{bibid}#*C
\citecs(pre)(post)[pre][post]{bibid}[pre][post]{bibid}#C
\authornumcites{bibid}{bibid}#C
\authornumcites(post){bibid}{bibid}#*C
\authornumcites(pre)(post){bibid}{bibid}#C
\authornumcites(pre)(post)[post]{bibid}[post]{bibid}#*C
\authornumcites[post]{bibid}[post]{bibid}#*C
\authornumcites[pre][post]{bibid}[pre][post]{bibid}#*C
\authornumcites(pre)(post)[pre][post]{bibid}[pre][post]{bibid}#C
