# recorder-fingering package
# Matthew Bertucci 2025/02/03 for v1.4

#include:tikz
#include:tikzlibrarycalc
#include:graphicx

\Sopranino{note}
\Sopranino[parameters%keyvals]{note}
\Soprano{note}
\Soprano[parameters%keyvals]{note}
\Alto{note}
\Alto[parameters%keyvals]{note}
\Tenor{note}
\Tenor[parameters%keyvals]{note}
\Bass{note}
\Bass[parameters%keyvals]{note}
\Whistle{note}
\Whistle[parameters%keyvals]{note}

\fingeringSetup{parameters%keyvals}

#keyvals:\Sopranino,\Soprano,\Alto,\Tenor,\Bass,\Whistle,\fingeringSetup
thumboffset#true,false
width=##L
LHRHdivider#true,false
LHRHspace=##L
trilldir=#L,R,LR
Lpointer=%<symbol%>
Rpointer=%<symbol%>
trill={%<list of holes%>}
revdouble#true,false
#endkeyvals

\NewFfingering{notename}{fingering vector}
\NewFfingering*{notename}{fingering vector}
\NewCfingering{notename}{fingering vector}
\NewCfingering*{notename}{fingering vector}
\NewDfingering{notename}{fingering vector}
\NewDfingering*{notename}{fingering vector}
\AddFingerings{%<key%>}{%<note1={vector1},...%>}

\NewFtrill{notename}{fingering vector}{trill vector}
\NewFtrill*{notename}{fingering vector}{trill vector}
\NewCtrill{notename}{fingering vector}{trill vector}
\NewCtrill*{notename}{fingering vector}{trill vector}
\NewDtrill{notename}{fingering vector}{trill vector}
\NewDtrill*{notename}{fingering vector}{trill vector}
\AddTrills{%<key%>}{%<note1={{fingering vector},{trill vector}},...%>}

\Ftrill{note}
\Ftrill[parameters%keyvals]{note}
\Ctrill{note}
\Ctrill[parameters%keyvals]{note}
\Dtrill{note}
\Dtrill[parameters%keyvals]{note}
