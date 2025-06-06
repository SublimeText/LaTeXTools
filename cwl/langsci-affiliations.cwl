# langsci-affiliations package
# Matthew Bertucci 2024/12/04 for v1.4

\ResolveAffiliations{author}
\ResolveAffiliations[options%keyvals]{author}
\LinkToORCIDinAffiliations{arg}
\CountAuthorsFromAffiliations{author}
\CountAuthorsFromAffiliations[options%keyvals]{author}
\SetupAffiliations{options%keyvals}

#keyvals:\ResolveAffiliations,\CountAuthorsFromAffiliations,\SetupAffiliations
mark style=#alphabetic,numeric,circled,none
output affiliation#true,false
orcid placement=
output in groups#true,false
separator between two=%<separator%>
separator between multiple=%<separator%>
separator between final two=%<separator%>
separator between indices=%<separator%>
separator between affiliations=%<separator%>
output authors paragraph format=
output authors font=%<font commands%>
output affiliation paragraph format=
output affiliation font=%<font commands%>
input names separator=%<separator%>
input affiliation separator=%<separator%>
author affiliation skip=##L
#endkeyvals
