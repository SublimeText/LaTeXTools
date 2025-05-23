# letterswitharrows package
# Matthew Bertucci 2024/10/31

#include:l3keys2e
#include:mathtools

#keyvals:\usepackage/letterswitharrows#c
presets={%<set1,set2,...%>}
pgf
tweaks#true,false
linewidth=%<number%>
#endkeyvals

\arrowoverset{arg}#m
\arrowoverset[xoffset][xscale][yoffset]{arg}#m
\arrowoverset*{arg}#m
\arrowoverset*[xoffset][xscale][yoffset]{arg}#m

\vA#m
\vB#m
\vC#m
\vD#m
\vE#m
\vF#m
\vG#m
\vH#m
\vI#m
\vJ#m
\vK#m
\vL#m
\vM#m
\vN#m
\vO#m
\vP#m
\vQ#m
\vR#m
\vS#m
\vT#m
\vU#m
\vV#m
\vW#m
\vX#m
\vY#m
\vZ#m
\va#m
\vb#m
\vc#m
\vd#m
\ve#m
\vf#m
\vg#m
\vh#m
\vi#m
\vj#m
\vk#m
\vl#m
\vm#m
\vn#m
\vo#m
\vp#m
\vq#m
\vr#m
\vs#m
\vt#m
\vu#m
\vright#m
\vw#m
\vx#m
\vy#m
\vz#m
\Av#m
\Bv#m
\Cv#m
\Dv#m
\Ev#m
\Fv#m
\Gv#m
\Hv#m
\Iv#m
\Jv#m
\Kv#m
\Lv#m
\Mv#m
\Nv#m
\Ov#m
\Pv#m
\Qv#m
\Rv#m
\Sv#m
\Tv#m
\Uv#m
\Vv#m
\Wv#m
\Xv#m
\Yv#m
\Zv#m
\av#m
\bv#m
\cv#m
\dv#m
\ev#m
\fv#m
\gv#m
\hv#m
\iv#m
\jv#m
\kv#m
\lv#m
\mv#m
\nv#m
\ov#m
\pv#m
\qv#m
\rv#m
\sv#m
\tv#m
\uv#m
\vleft#m
\wv#m
\xv#m
\yv#m
\zv#m
\vAv#m
\vBv#m
\vCv#m
\vDv#m
\vEv#m
\vFv#m
\vGv#m
\vHv#m
\vIv#m
\vJv#m
\vKv#m
\vLv#m
\vMv#m
\vNv#m
\vOv#m
\vPv#m
\vQv#m
\vRv#m
\vSv#m
\vTv#m
\vUv#m
\vVv#m
\vWv#m
\vXv#m
\vYv#m
\vZv#m
\vav#m
\vbv#m
\vcv#m
\vdv#m
\vev#m
\vfv#m
\vgv#m
\vhv#m
\viv#m
\vjv#m
\vkv#m
\vlv#m
\vmv#m
\vnv#m
\vov#m
\vpv#m
\vqv#m
\vrv#m
\vsv#m
\vtv#m
\vuv#m
\vwv#m
\vxv#m
\vyv#m
\vzv#m
\vcA#m
\vcB#m
\vcC#m
\vcD#m
\vcE#m
\vcF#m
\vcG#m
\vcH#m
\vcI#m
\vcJ#m
\vcK#m
\vcL#m
\vcM#m
\vcN#m
\vcO#m
\vcP#m
\vcQ#m
\vcR#m
\vcS#m
\vcT#m
\vcU#m
\vcV#m
\vcW#m
\vcX#m
\vcY#m
\vcZ#m
\cAv#m
\cBv#m
\cCv#m
\cDv#m
\cEv#m
\cFv#m
\cGv#m
\cHv#m
\cIv#m
\cJv#m
\cKv#m
\cLv#m
\cMv#m
\cNv#m
\cOv#m
\cPv#m
\cQv#m
\cRv#m
\cSv#m
\cTv#m
\cUv#m
\cVv#m
\cWv#m
\cXv#m
\cYv#m
\cZv#m
\vcAv#m
\vcBv#m
\vcCv#m
\vcDv#m
\vcEv#m
\vcFv#m
\vcGv#m
\vcHv#m
\vcIv#m
\vcJv#m
\vcKv#m
\vcLv#m
\vcMv#m
\vcNv#m
\vcOv#m
\vcPv#m
\vcQv#m
\vcRv#m
\vcSv#m
\vcTv#m
\vcUv#m
\vcVv#m
\vcWv#m
\vcXv#m
\vcYv#m
\vcZv#m
\vell#m
\ellv#m
\vellv#m

#ifOption:presets=vec-cev
\vec{arg}#m
\cev{arg}#m
\vecev{arg}#m
#endif
#ifOption:presets={vec-cev}
\vec{arg}#m
\cev{arg}#m
\vecev{arg}#m
#endif

#ifOption:pgf
#include:pgf
#endif
