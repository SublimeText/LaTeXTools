%%
%% This is file `jurabib.bst',
%% generated with the docstrip utility.
%%
%% The original source files were:
%%
%% jurabib.dtx  (with options: `jurabst')
%% ----------------------------------------
%% BibTeX style for use with the jurabib package version v0.6
%% Copyright (C) 1999-2004 Jens Berger (http://www.jurabib.org)
%% See jurabib.ins  for the copyright details.
%% 
ENTRY{
  address
  author
  booktitle
  chapter
  edition
  editor
  howpublished
  institution
  isbn
  issn
  journal
  key
  language
  month
  note
  number
  organization
  pages
  publisher
  school
  series
  title
  type
  volume
  year
%%
  url
  urldate
  volumetitle
  dissyear
  howcited
  juratitle
  juraauthor
  shorttitle
  shortauthor
  ssedition
  titleaddon
  booktitleaddon
  editortype
  sortkey
  annote
  gender
  translator
  flanguage
  oyear
  oaddress
  opublisher
  updated
  totalpages
  founder
  archive
  subarchive
  shortarchive
  shortsubarchive
  sig1
  sig2
  sig3
  sig4
  archname
  }
  { repeat-authors repeat-titles }
  { label dummy.label extra.label sort.label current-authors }

INTEGERS { output.state before.all mid.sentence after.sentence after.block }

INTEGERS { colon.after  period.dash }

FUNCTION {init.state.consts}
{ #0 'before.all :=
  #1 'mid.sentence :=
  #2 'after.sentence :=
  #3 'after.block :=
  #4 'colon.after :=
  #5 'period.dash :=
}

STRINGS { s t u v w x }

FUNCTION {output.nonnull}
{ 's :=
  output.state after.block =
    { write$ }
    { output.state before.all =
      {  write$ }
      {  output.state colon.after =
         { "" * write$ }
         { output.state period.dash =
           { ", " *  write$ }
           { output.state mid.sentence =
             { " " * write$ }
             { write$ }
           if$
           }
        if$
         }
      if$
       }
     if$
     after.block 'output.state :=
     }
   if$
   s
}

FUNCTION {output}
{ duplicate$ empty$
  'pop$
  'output.nonnull
  if$
}

FUNCTION {output.check}
{ 't :=
  duplicate$ empty$
  { pop$ "Empty " t * " in " * cite$ * warning$ }
  'output.nonnull
  if$
}

FUNCTION {not}
{   { #0 }
  { #1 }
  if$
}

FUNCTION {and}
{   'skip$
  { pop$ #0 }
  if$
}

FUNCTION {or}
{   { pop$ #1 }
  'skip$
  if$
}

FUNCTION {is.num}
{ chr.to.int$
  duplicate$ "0" chr.to.int$ < not
  swap$ "9" chr.to.int$ > not and
}

FUNCTION {extract.num}
{ duplicate$ 't :=
  "" 's :=
  { t empty$ not }
  { t #1 #1 substring$
  t #2 global.max$ substring$ 't :=
  duplicate$ is.num
    { s swap$ * 's := }
    { pop$ "" 't := }
  if$
  }
  while$
  s empty$
  'skip$
  { pop$ s }
  if$
}

FUNCTION {convert.edition.superscript}
{ edition extract.num "l" change.case$ 's :=
  s "first" = s "1" = or s "erste" = or
    { "1" 't := }
    { s "second" = s "2" = or s "zweite" = or
        { "2" 't := }
        { s "third" = s "3" = or s "dritte" = or
            { "3" 't := }
            { s "fourth" = s "4" = or s "vierte" = or
                { "4" 't := }
                { s "fifth" = s "5" = or s "fuenfte" = or
                    { "5" 't := }
                    { s "sixth" = s "6" = or s "sechste" = or
                        { "6" 't := }
                        { s "seventh" = s "7" = or s "siebte" = or s "siebente" = or
                            { "7" 't := }
                            { s "eighth" = s "8" = or s "achte" = or
                                { "8" 't := }
                                { s "nineth" = s "9" = or s "neunte" = or
                                      { "9" 't := }
                                      {  s #1 #1 substring$ is.num
                                           { s "" * 't := }
                                           { edition 't := }
                                         if$
                                      }
                                  if$
                                }
                              if$
                            }
                          if$
                        }
                      if$
                    }
                  if$
                }
              if$
            }
          if$
        }
      if$
    }
  if$
  t
}

FUNCTION {n.dashify}
{ 't :=
  ""
  { t empty$ not }
      { t #1 #1 substring$ "-" =
          { t #1 #2 substring$ "--" = not
               { "--" * t #2 global.max$ substring$ 't := }
               {   { t #1 #1 substring$ "-" = }
                   { "-" * t #2 global.max$ substring$ 't :=  }
                  while$
               }
            if$
          }
          { t #1 #1 substring$ * t #2 global.max$ substring$ 't := }
    if$
  }
  while$
}

FUNCTION {output.bibitem.fst}
{ newline$
  "\bibitem[{" write$
  shortauthor empty$
    { juraauthor empty$
       { author empty$
          { editor empty$
              { organization empty$
                   { archive empty$
                         { "empty" write$ }
                         { archive write$ }
                     if$
                   }
                   { organization write$ }
                if$
              }
              { label write$ }
            if$
          }
          { label write$ }
         if$
       }
       { juraauthor write$ }
     if$
    }
    { shortauthor write$ }
  if$
  "}%" write$
  sortkey empty$
         'skip$
         { newline$ "% SORTKEY: [" sortkey * "]" * write$ }
  if$
  newline$
  shorttitle empty$
   { juratitle empty$
       { journal empty$
          { "         {}%" write$ }
          { volume empty$
                { year empty$
                     { "         {" journal * "}%" * write$ }
                     { "         {" journal * "\jbsy {" * year * "}}%" * write$ }
                  if$
                }
                { year empty$
                     { "         {" journal * "}%" * write$ }
                     { "         {" journal * " " * volume * " " * " \peryearformat {" year * "}}%" * * write$ }
                  if$
                }
            if$
          }
         if$
       }
       { "         {" juratitle * "}%" * write$ }
     if$
    }
    { "         {" shorttitle * "}%" * write$ }
  if$
  newline$
  repeat-authors
    { "         {{1}" write$ }
    { "         {{0}" write$ }
  if$
  howcited empty$
    { "{}" write$ }
    { "{" howcited * "}" * write$ }
  if$
  type$ empty$
    { "{}" write$ }
    { "{" type$ * "}" * write$ }
  if$
  year empty$
    { type$ "book" = dissyear empty$ not and
        { "{" dissyear * write$
          extra.label "" =
              skip$
              { "\el {" write$ extra.label write$ "}" write$ }
          if$
          "}" write$
        }
        {  "{}" write$ }
      if$
    }
    { "{" year * write$
      extra.label "" =
          'skip$
          { "\el {" write$ extra.label write$ "}" write$ }
      if$
      "}" write$
    }
  if$
  edition empty$
    { "{}" write$ }
    { "{" convert.edition.superscript extract.num * "}" * write$ }
  if$
  ssedition empty$
    { "{}" write$ }
    { "{" ssedition * "}" * write$ }
  if$
  language empty$
    { "{}" write$ }
    { "{" language * "}" * write$ }
  if$
  pages empty$
    { "{}%" write$ }
    { "{" write$ pages n.dashify write$ "}%" write$ }
  if$
}

FUNCTION {output.bibitem.snd}
{ newline$
  publisher empty$
    { address empty$
         { year empty$
               { "          {" write$ }
               { "          {" write$
                            year write$
                            extra.label "" =
                              'skip$
                              { "\el {" write$ extra.label write$ "}" write$ }
                            if$
               }
           if$
         }
         { year empty$
               { "          {" write$ address write$ }
               { "          {" write$ address write$ "\bibbdsep {} " write$
                            year write$
                            extra.label "" =
                              'skip$
                              { "\el {" write$ extra.label write$ "}" write$ }
                            if$
               }
           if$
         }
      if$
    }
    { address empty$
        { year empty$
              { "          {" write$ publisher write$ }
              { "          {" write$ publisher write$ "\bibbdsep {} " write$
                           year write$
                           extra.label "" =
                             'skip$
                             { "\el {" write$ extra.label write$ "}" write$ }
                           if$
              }
          if$
        }
        { year empty$
              { "          {" write$ address write$ "\bpubaddr {} " write$ publisher write$ }
              { "          {" write$ address write$ "\bpubaddr {} " write$ publisher write$ "\bibbdsep {} " write$
                           year write$
                           extra.label "" =
                             'skip$
                             { "\el {" write$ extra.label write$ "}" write$ }
                           if$
              }
          if$
        }
      if$
    }
  if$
  "}}%" write$ newline$
  "         {" write$
  title empty$
    { "{}%" write$ newline$ }
    { "{" title *
      type$ "archival" =
          { shortarchive empty$ not
                { ", In: " shortarchive * * }
                { archive empty$ not
                      { ", In: " archive * * }
                      'skip$
                  if$
                }
             if$
             shortsubarchive empty$
                 'skip$
                { ", " shortsubarchive * * }
             if$
             sig1 empty$
                 'skip$
                 { ", " sig1 * *
                   sig2 empty$
                       'skip$
                       { ". " sig2 * *
                         sig3 empty$
                             'skip$
                             { ". " sig3 * *
                               sig4 empty$
                                   'skip$
                                   { ". " sig4 * * }
                               if$
                             }
                         if$
                       }
                  if$
                 }
             if$
             pages empty$
                  'skip$
                  { " \jbArchPages {" pages n.dashify * "}" * * }
             if$
          }
          'skip$
      if$
      "}%" * write$ newline$ }
  if$
  gender empty$
    { "          {}" write$ }
    { "          {" gender * "}" * write$ }
  if$
  oyear empty$
    { "{}" write$ }
    { "{" oyear * "}" * write$ }
  if$
  author empty$
    { editor empty$
         { "{4}" write$ }% author and editor empty
         { "{3}" write$ }% author empty, editor not
      if$
    }
    { editor empty$
         { "{2}" write$ }% editor empty, author not
         { "{1}" write$ }% both author and editor given
      if$
    }
  if$
  "{}{}{}{}{}}%" write$ newline$
  "        ]{" write$
  cite$ write$
  "}" write$
  url empty$
    'skip$
    { newline$ " \jburldef {" write$ cite$ write$ "}{" write$ url write$ "}%" write$ }
  if$
  newline$
  " \jbbibargs {" write$
  ""
  before.all 'output.state :=
}

FUNCTION {output.bibitem}
{ output.bibitem.fst
  output.bibitem.snd
}

FUNCTION {format.note}
{ note empty$
      'skip$
      { output.state before.all =
          {" \jbnote {} {" * note * "} " * }
          {" \jbnote {1} {" * note * "} " * }
       if$
      }
  if$
}

FUNCTION {format.endnote}
{ note empty$
      { "" }
      { "  \jbendnote {" note * "}" * }
  if$
}


FUNCTION {format.juradiss.book}
{ dissyear empty$
  { "" }
  { type empty$
     { school empty$
         { "Dissyear but no school in " cite$ * warning$
           " (\alsothesisname {} \jurthesisname" *
           year empty$ not year missing$ not and
                { "\bibbdsep {} " dissyear * }
                'skip$
           if$
           ")" *
         }
         { " (\alsothesisname {} \jurthesisname, " school *
           year empty$ not year missing$ not and
                { "\bibbdsep {} " dissyear * * }
                'skip$
           if$
           ")" *
         }
       if$
     }
     { school empty$
         { "Dissyear but no school in " cite$ * warning$
           " (\alsothesisname {} " type *
           year empty$ not year missing$ not and
                { "\bibbdsep {} " dissyear * }
                'skip$
           if$
           ")" *
         }
         { " (\alsothesisname {} " type *
           ", " school * *
           year empty$ not year missing$ not and
                { "\bibbdsep {} " dissyear * * }
                'skip$
           if$
           ")" *
         }
       if$
     }
   if$
  }
  if$
}

FUNCTION {format.thesis}
{ year empty$
      { school empty$
              { "No universtiy in " cite$ * warning$ }
              { "There's a university, but no year in " cite$ * warning$ }
        if$
        ""
      }
      { type empty$
            { school empty$
                    { "No university in " cite$ * warning$
                        type$ "mastersthesis" =
                           { "\apyformat {\mastersthesisname" * address empty$ 'skip$ { ", " address * * } if$ "\bibbdsep {} " year * "}" * }
                           { type$ "jurthesis" =
                                 { "\apyformat {\jurthesisname" * address empty$ 'skip$ { ", " address * * } if$ "\bibbdsep {} " year * "}" * }
                                 { "\apyformat {\phdthesisname" * address empty$ 'skip$ { ", " address * * } if$ "\bibbdsep {} " year * "}" * }
                             if$
                           }
                        if$
                    }
                    {  type$ "mastersthesis" =
                           { "\mastersthesisname, \apyformat {" school * address empty$ 'skip$ { ", " address * * } if$ "\bibbdsep {} " year * * "}" * }
                           { type$ "jurthesis" =
                                 { "\jurthesisname, \apyformat {" school * address empty$ 'skip$ { ", " address * * } if$ "\bibbdsep {} " year * * "}" * }
                                 { "\phdthesisname, \apyformat {" school * address empty$ 'skip$ { ", " address * * } if$ "\bibbdsep {} " year * * "}" * }
                             if$
                           }
                       if$
                    }
              if$
            }
            { school empty$
                    { "No university in " cite$ * warning$ type
              address empty$ 'skip$ { " \apyformat {" address * } if$ "\bibbdsep {} " *  * year * "}" * }
                    { type " \apyformat {" * school * address empty$ 'skip$ { ", " address * * } if$ "\bibbdsep {} " year * * "}" * }
              if$
            }
       if$
  }
  if$
}

FUNCTION {set.comma.pages.check}
{ year empty$
  'skip$
  { pages empty$
    { url empty$
      'skip$
      { ", " * }
      if$
    }
    { ", " * }
    if$
  }
  if$
}

FUNCTION {set.period.dash}
{ output.state before.all =
  'skip$
  { period.dash  'output.state := }
  if$
}

FUNCTION {set.period.dash.check}
{ empty$
  'skip$
  'set.period.dash
  if$
}

FUNCTION {new.sentence}
{ output.state before.all =
   'skip$
   { after.sentence 'output.state := }
  if$
}

FUNCTION {part.of.sentence}
{ output.state before.all =
   'skip$
   { mid.sentence 'output.state := }
  if$
}

FUNCTION {new.sentence.checka}
{ empty$
  'skip$
  'new.sentence
  if$
}

FUNCTION {field.or.null}
{ duplicate$ empty$
  { pop$ "" }
  'skip$
  if$
}


FUNCTION {get.final.nonrightbrace.char}
{   { duplicate$
    #-1 #1 substring$
    duplicate$
    "}" =
  }
  { pop$
    #-2 global.max$ substring$
  }
  while$
  swap$ pop$
}


FUNCTION {check.punct.instead.of.add.period}
{ duplicate$
  get.final.nonrightbrace.char
  duplicate$ "." = swap$
  duplicate$ "!" = swap$
  "?" = or or
  { "} " * }
  { "}\bibatsep\ " * }
  if$
}

FUNCTION {check.punct.instead.of.add.period.art}
{ duplicate$
  get.final.nonrightbrace.char
  duplicate$ "." = swap$
  duplicate$ "!" = swap$
  "?" = or or
  { "} " * }
  { pages empty$ note empty$ url empty$ and and
    { "} " * }
    { volume empty$
         { pages empty$
              { "}\ajtsep\ " * }
              { crossref missing$
                    { month empty$
                         { "}\ajtsep\ " * }
                         { "}\ajtsep " * }
                      if$
                    }
                    { "}\ajtsep " * }
                if$
              }
          if$
         }
         { "}\ajtsep\ " * }
       if$
    }
   if$
  }
  if$
}

FUNCTION {emphasize}
{ duplicate$ empty$
       { pop$ "" }
       { "\bibtfont {" swap$ check.punct.instead.of.add.period * }
  if$
}

FUNCTION {journaltitlemarkup}
{ duplicate$ empty$
      { pop$ "" }
      { "\bibJTsep \bibjtfont {" swap$ check.punct.instead.of.add.period.art * }
  if$
}

FUNCTION {incollbooktitlemarkup}
{ duplicate$ empty$
      { pop$ "" }
      { "\bibbtfont {" swap$ check.punct.instead.of.add.period * }
  if$
}

INTEGERS { nameptr namesleft numnames }

FUNCTION { lastnamemarkup }
{ duplicate$ empty$
    { pop$ "" }
    { "\bibnf {" swap$ * "}" * }
  if$
}

FUNCTION { editorlastnamemarkup }
 { duplicate$ empty$
  { pop$ "" }
  { author empty$
       { "\biblenf {" swap$ * "}" * } % lonely editor(s)!
       { "\bibenf {" swap$ * "}" * }
   if$
  }
  if$
}

FUNCTION { othermarkup }
 { duplicate$ empty$
    { pop$ " {}" }
       { " {" swap$ * "}" * }
  if$
}

FUNCTION {article.in.journal}
{ duplicate$ empty$
  { pop$ "" }
  { author missing$
    { title missing$
        'skip$
        { journaltitlemarkup "" swap$ * }
      if$
    }
    { journaltitlemarkup "" swap$ * }
    if$
   }
  if$
}

FUNCTION {format.names} % NEW v0.5
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
  { namesleft #0 > }
  { s nameptr "{ll}" format.name$ 't := t lastnamemarkup 't :=
    s nameptr "{ff}" format.name$ othermarkup 'u :=
    s nameptr "{f.}" format.name$ othermarkup 'v :=
    s nameptr "{vv}" format.name$ othermarkup 'w :=
    s nameptr "{jj}" format.name$ othermarkup 'x :=
    t u * v * w * x * 't :=
     nameptr #1 >
      { namesleft #1 >
          { numnames #3 >
                { "" * }
                { numnames #3 <
                     { "\Bibbtasep " * t * }      % between (exactly) two authors
                     { "\Bibbfsasep " * t * }     % between first and second author (if more than two)
                  if$
                }
            if$
          }
          { t "\bibnf {others} {} {} {} {}" =
            t "\bibnf {others} {} {} {} {} \edfont {\editorsname}" = or
            numnames #3 > or
               { "\bibIMfont {\Bibetal}" * }
               { numnames #3 <
                   { "\Bibbtasep " * t * }  % between (exactly) two authors
                   { "\Bibbstasep " * t * } % between second and third author
                 if$
               }
            if$
          }
        if$
      }
     't
    if$
    nameptr #1 + 'nameptr :=
    namesleft #1 -  'namesleft :=
  }
  while$
}

FUNCTION {format.editor.names} % NEW v0.5
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
  { namesleft #0 > }
  { s nameptr "{ll}" format.name$ 't := t editorlastnamemarkup 't :=
    s nameptr "{ff}" format.name$ othermarkup 'u :=
    s nameptr "{f.}" format.name$ othermarkup 'v :=
    s nameptr "{vv}" format.name$ othermarkup 'w :=
    s nameptr "{jj}" format.name$ othermarkup 'x :=
    t u * v * w * x * 't :=
     nameptr #1 >
      { namesleft #1 >
          { numnames #3 >
                { "" * }
                { numnames #3 <
                     { "\Bibbtesep " * t * }      % between (exactly) two editors
                     { "\Bibbfsesep " * t * }     % between first and second editor (if more than two)
                  if$
                }
            if$
          }
          { t "\bibenf {others} {} {} {} {}" =
            t "\biblenf {others} {} {} {} {}" = or
            t "\bibenf {others} {} {} {} {} \edfont {\editorsname}" = or
            t "\biblenf {others} {} {} {} {} \edfont {\editorsname}" = or
            numnames #3 > or
               { "\bibIMfont {\Bibetal}" * }
               { numnames #3 <
                   { "\Bibbtesep " * t * }  % between (exactly) two editors
                   { "\Bibbstesep " * t * } % between second and third editor
                 if$
               }
            if$
          }
        if$
      }
     't
    if$
    nameptr #1 + 'nameptr :=
    namesleft #1 -  'namesleft :=
  }
  while$
}

FUNCTION {format.name.sig}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
  { namesleft #0 > }
  { s nameptr "{ff}{ vv}{ ll}{ jj}" format.name$ 't :=
      nameptr #1 >
        { namesleft #1 >
            { "" * t * }
            {  t "others" =
                { " et al." * }
                { "" * t * }
              if$
            }
          if$
        }
        't
      if$
    nameptr #1 + 'nameptr :=
    namesleft #1 -  'namesleft :=
  }
  while$
}

FUNCTION {indexmarkup}
{ duplicate$ empty$
       { pop$ "{}" }
       { "{" swap$ * "}" * }
  if$
}

FUNCTION {format.names.for.index}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
  { namesleft #0 > }
  { s nameptr "{ll}" format.name$ 't := t indexmarkup 't :=
    s nameptr "{ff}" format.name$ indexmarkup 'u :=
    s nameptr "{f.}" format.name$ indexmarkup 'v :=
    s nameptr "{vv}" format.name$ indexmarkup 'w :=
    s nameptr "{jj}" format.name$ indexmarkup 'x :=
    t u * v * w * x * 't :=
    t "{others}{}{}{}{}" =
      'skip$
      { nameptr #1 >
         { namesleft #1 >
             { "; " * t * }
             {
               t "others" =
                  'skip$
                  { "; " * t * }
               if$
             }
           if$
          }
          't
        if$
      }
    if$
    nameptr #1 + 'nameptr :=
    namesleft #1 -  'namesleft :=
  }
  while$
}

FUNCTION {format.authors}
{ author empty$
  { "" }
  { author format.names }
  if$
}

FUNCTION {format.founders}
{ founder empty$
   'skip$
   { author empty$
         'skip$
         { " in: " * }
     if$
     founder format.names "\foundername" * *
     editor empty$
        'skip$
        { author empty$
             { "\afterfoundersep {}" * }
             'skip$
          if$
        }
     if$
   }
  if$
}

FUNCTION {format.editors}
{ editor empty$
   { "" }
   { author empty$
        {  editor format.editor.names
           editortype empty$
              { editor num.names$ #1 >
                  { "\fsted {\editorsname}" * }
                  { "\fsted {\editorname}" * }
                if$
              }
              { "\fsted {(" editortype * ")}" * * }
           if$
        }
        {  founder empty$
               { "\bibfnfont {;} " * }
               { type$ "commented" =
                   { "\afterfoundersep {}" * }
                   { "\bibfnfont {;} " * }
                 if$
               }
           if$
           editor format.editor.names *
           editortype empty$
              { editor num.names$ #1 >
                  { " \edfont {\editorsname}" * }
                  { " \edfont {\editorname}" * }
                if$
              }
              { " \edfont {(" editortype * ")}" * * }
           if$
        }
    if$
   }
  if$
}

FUNCTION {format.snd.editors}
{ editor empty$
   { "" * }
   { author empty$
        { editortype empty$
             { editor num.names$ #1 >
                 { "\snded {\sndeditorsname}" * }
                 { "\snded {\sndeditorname}" * }
               if$
             }
             { "\snded {(" editortype * ")}" * * }
          if$
        }
        'skip$
    if$
   }
  if$
}

FUNCTION { format.howcited }
{ "} {\bibhowcited}" format.endnote * }

FUNCTION {fin.entry.endnote}
{ " \jbdoitem {" *
  author empty$
      'skip$
      { author format.names.for.index * }
  if$
  "} {"
  editor empty$
      'skip$
      { editor format.names.for.index * }
  if$
  "} {" *
  organization empty$
      'skip$
      { "{" organization * "}{}{}{}{}" * * }
  if$
  "}" * * write$
  annote missing$
    { " \bibAnnoteFile {" cite$ * "}" * write$ newline$ }
    { " \bibAnnote {" annote * "}" * write$ newline$ }
  if$
}

FUNCTION {count.authors.or.editors}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
  { namesleft #0 > }
  { "" 't :=
      nameptr #1 >
        { namesleft #1 >
            { "" * }
            { "s" * } % more than one author/editor, append `s'
          if$
        }
        't
      if$
    nameptr #1 + 'nameptr :=
    namesleft #1 - 'namesleft :=
  }
  while$
}

FUNCTION { set.after.author.sep }
{ author missing$
     { editor missing$
          { organization missing$
                 { archive missing$
                      { "} {empty} {} {" }
                      { "} {" archive format.name.sig * "} {} {" * }
                   if$
                 }
                 { "} {" organization "} {org} {" * * }
            if$
          }
          { "} {" editor format.name.sig * "} {ed" editor count.authors.or.editors "} {" * * * }
      if$
     }
     { "} {" author format.name.sig * "} {au" author count.authors.or.editors "} {" * * * }
  if$
  author empty$
      { format.snd.editors }
      'skip$
  if$
  "" *
}


FUNCTION {format.names.info}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
  { namesleft #0 > }
  { s nameptr "{ff }{vv }{ll}" format.name$ 't :=
      nameptr #1 >
        { namesleft #1 >
            { " " * t * }
            {  t "others" =
                { " et al." * }
                { " " * t * }
              if$
            }
          if$
        }
        't
      if$
    nameptr #1 + 'nameptr :=
    namesleft #1 -  'namesleft :=
  }
  while$
}

FUNCTION { format.howcited.comment }
{ edition empty$
     { "} {\bibcommenthowcited}" format.endnote * }
     { "} {\bibcommenthowcited}" format.endnote * *
       author empty$ editor empty$ not and
         { " \jbauthorinfo {" editor format.names.info " " title * * * "}{" cite$ "}" * * * }
         { author empty$ shortauthor empty$ not and
               { " \jbauthorinfo {" shortauthor format.names.info " " title * * * "}{" cite$ "}" * * * }
               { " \jbauthorinfo {" author format.names.info " " title * * * "}{" cite$ "}" * * * }
           if$
         }
       if$
     }
  if$
}

FUNCTION { format.howcited.artperiod }
{ "} {\bibartperiodhowcited}" format.endnote * }

FUNCTION {format.proceed.organization}
{  organization empty$
    { "" }
    { organization " \organizationname {}" * }
   if$
}

FUNCTION {format.titleaddon}
{ title empty$
  { "" }
  { titleaddon empty$
       { "" }
       { titleaddon "\bibatsep\ " * }
    if$
  }
  if$
}

FUNCTION {format.title}
{ title empty$
      { "" }
      { "\bibtfont {" title check.punct.instead.of.add.period * format.titleaddon * }
  if$
}

FUNCTION {format.artperiodincoll.title}
{ title empty$
      { "" }
      { "\bibapifont {" title check.punct.instead.of.add.period *  format.titleaddon * }
  if$
}

FUNCTION {format.volumetitle}
{ volumetitle empty$
  { "" }
  { volume empty$
      { "There's a volumetitle but no volume in " cite$ * warning$ volumetitle ", " * }
      { volumetitle ", " * }
    if$
  }
 if$
}

FUNCTION {add.extra.label}
{ extra.label "" =
    'skip$
    { "\bibel {" extra.label * "}" * * }
  if$
}

FUNCTION {format.date}
{ year empty$
  { month empty$
       { "" }
       { "There's a month but no year in " cite$ * warning$  month  }
    if$
  }
  { month empty$
       { edition empty$
            'skip$
            { "\jbssedbd {" convert.edition.superscript extract.num * "}" * * }
         if$
         year
         add.extra.label
       }
       { month " " *
         edition empty$
            'skip$
            { "\jbssedbd {" convert.edition.superscript extract.num * "}" * * }
         if$
         year *
         add.extra.label
       }
    if$
  }
  if$
}

FUNCTION {format.update}
{ updated missing$ not
     { "\updatesep {} \updatename {} " * updated * }
     'skip$
  if$
}

FUNCTION {oaddress.opublisher.oyear.format}
{ type$ "book" = type$ "inbook" = type$ "incollection" = or or
     { oyear empty$
            { opublisher empty$
                 { oaddress empty$
                     'skip$
                     { oaddress "\osep {} " * * }
                   if$
                 }
                 { oaddress empty$
                     { opublisher "\osep {} " * * }
                     { oaddress "\bpubaddr {} " * opublisher "\osep {} " * * * }
                   if$
                 }
              if$
            }
            { year empty$
                 { "oyear without year in " cite$ * warning$ }
                 'skip$
              if$
              opublisher empty$
                 { oaddress empty$
                     { oyear * "\osep {} \reprintname {}, " * }
                     { oaddress "\bibbdsep {} " * oyear "\osep {} " * * * }
                   if$
                 }
                 { oaddress empty$
                     { opublisher * "\bibbdsep {} " * oyear "\osep {} " * * }
                     { oaddress "\bpubaddr {} " * opublisher "\bibbdsep {} " * * oyear "\osep {} " * * * }
                   if$
                 }
              if$
            }
       if$
     }
     'skip$
  if$
}

FUNCTION {make.translators}
{ before.all 'output.state :=
  translator empty$
    { flanguage empty$
        { "" }
        { "\translator {}{" flanguage "l" change.case$ * "}" *
          type$ "incollection" = not
          type$ "article" = not
          and
            { "{1} " * }
            { type$ "incollection" =
                { booktitle empty$
                    { "{} " * }
                    { "{1} " * }
                  if$
                }
                { type$ "article" =
                    { "{1}" * }
                    { series empty$
                        { "{} " * }
                        { "{1} " * }
                      if$
                    }
                  if$
                }
              if$
            }
          if$
        }
      if$
    }
    { "\translator {" translator * "}" *
      flanguage empty$
        { "{}" * }
        { "{" * flanguage "l" change.case$ * "}" * }
      if$
      type$ "incollection" = not
      type$ "article" = not
      and
        { "{1} " * }
        {
          type$ "incollection" =
            { booktitle empty$
                { "{} " * }
                { "{1} " * }
              if$
            }
            { type$ "article" =
                { "{1} " * }
                { series empty$
                    { "{} " * }
                    { "{1} " * }
                  if$
                }
              if$
            }
          if$
        }
      if$
    }
  if$
  before.all 'output.state :=
}


FUNCTION {checked.inst}
{ institution empty$
    { " \apyformat {" *
        oaddress.opublisher.oyear.format
    }
    { address empty$ not
         { " \apyformat {" * }
         'skip$
      if$
    }
  if$
}

FUNCTION {format.address.publisher.year}
{  publisher empty$
     { address empty$
         { year empty$
             { "Neither address nor year in " cite$ * warning$ "" }
             { "No address in " cite$ * warning$
               institution empty$
                 { " \apyformat {" oaddress.opublisher.oyear.format format.date * "}" * }
                 { " \apyformat {" institution * "\bibbdsep {} "  * format.date "}" * * }
               if$
             }
           if$
         }
        { year empty$
            { checked.inst address "}" * }
            { checked.inst address "\bibbdsep {} " format.date * "}" * * }
          if$
        }
       if$
     }
     { address empty$
          { year empty$
                { "There's only a publisher (no address, no year) in " cite$ * warning$ publisher }
                { checked.inst publisher "\bibbdsep {} " * format.date "}" * * }
            if$
          }
          { year empty$
                { checked.inst address * "\bpubaddr {} " publisher "}" * * }%
                { checked.inst address * "\bpubaddr {} " publisher "\bibbdsep {} " * format.date "}" * * * }
            if$
          }
       if$
     }
  if$
}

FUNCTION {format.howpublished.address.year}
{ howpublished empty$
     { address empty$
          { year empty$
               { "Neither address nor year in " cite$ * warning$ "" }
               { "No address in " cite$ * warning$ format.date }
            if$
          }
          { " \apyformat {" oaddress.opublisher.oyear.format address * "\bibbdsep {} " * format.date "}" * * }
       if$
     }
     { address empty$
          { year empty$
               { "There's only a howpublished (no address, no year) in " cite$ * warning$ howpublished }
               { " \apyformat {" oaddress.opublisher.oyear.format howpublished * "\bibbdsep {} " * format.date "}" * * }
            if$
          }
          { year empty$
               { " \apyformat {" oaddress.opublisher.oyear.format address * "\bpubaddr {} " * howpublished "}" * * }
               { " \apyformat {" oaddress.opublisher.oyear.format address * "\bpubaddr {} " * howpublished * "\bibbdsep {} " * format.date "}" * * }
            if$
          }
       if$
     }
  if$
}

FUNCTION {tie.or.space.connect}
{ duplicate$ text.length$ #4 <
     { "~" }
     { " " }
  if$
  swap$ * *
}

FUNCTION {bibvol.tie.or.space.connect}
{ duplicate$ text.length$ #4 <
     { "~" }
     { "{} " }
  if$
  swap$ * *
}

FUNCTION {format.btitle}{ title emphasize format.titleaddon * }

FUNCTION {format.btitle.vol}
{ number empty$
   { series empty$
        { volume empty$
             { title emphasize format.titleaddon * }
             {
               title emphasize format.titleaddon * " \volumeformat {" volume * "} " * *
             }
          if$
        }
        { volume empty$
             { title emphasize format.titleaddon *  }
             {
               title emphasize format.titleaddon * "\volumeformat {" volume * "} " * * series "\bibatsep\ " * *
             }
          if$
        }
     if$
   }
   { title emphasize format.titleaddon * }
  if$
}

FUNCTION {format.btitle.vol.inbook}
{ number empty$
   { series empty$
       { volume empty$
           { "\bibapifont {" title check.punct.instead.of.add.period * format.titleaddon * }
           { "\bibapifont {" title check.punct.instead.of.add.period * format.titleaddon *
             " \volumeformat {" volume * "} " * *
           }
         if$
       }
       { volume empty$
           { "\bibapifont {" title check.punct.instead.of.add.period * format.titleaddon * }
           { series emphasize
             "\volumeformat {" volume * "} " * *
             "\bibapifont {" title check.punct.instead.of.add.period * format.titleaddon * * }
         if$
       }
     if$
   }
   { "\bibapifont {" title check.punct.instead.of.add.period * format.titleaddon * }
  if$
}

FUNCTION {format.url}
{ url empty$
  { "" }
  { author empty$ title empty$ and
        'skip$
        { " " * }
    if$
    urldate empty$
        {"\jburluse {" cite$ * "}" * }
        {"\jburluse {" cite$ * "}\bibbudcsep {}\urldatecomment " * urldate * }
    if$
  }
  if$
}

FUNCTION {format.naked.url}
{ url empty$
  { "" }
  { urldate empty$
    { title empty$
         'skip$
         { title emphasize * }
      if$
      "\jburluse {" cite$ * "}" *
    }
    { title empty$
         'skip$
         { title emphasize * }
      if$
      "\jburluse {" cite$ * "}\bibbudcsep {}\urldatecomment " * urldate *
    }
  if$
  }
  if$
}

FUNCTION {format.series.number}
{ volume empty$
  { number empty$
     { series empty$
          { "" }
          { " \numberandseries {}{" series * "}" * }
       if$
     }
     { series empty$
         { " \numberandseries {" number * "}{}" * "There's a number but no series in " cite$ * warning$ }
         { " \numberandseries {" number * "}{" * series "}" * * }
       if$
     }
    if$
   }
   { series empty$
      { "" }
      { type$ "proceedings" =
          { " \numberandseries {}{" series * "}" * } % { " (" series * ")" * }
          { "" }
        if$
      }
     if$
   }
  if$
}

FUNCTION {first.ed} { "\firstedname" }
FUNCTION {second.ed}{ "\secondedname" }
FUNCTION {third.ed} { "\thirdedname" }
FUNCTION {fourth.ed}{ "\fourthedname" }
FUNCTION {fifth.ed} { "\fifthedname" }
FUNCTION {th.ed}    { "\thedname" }

FUNCTION {convert.edition}
{ edition extract.num "l" change.case$ 's :=
  s "first" = s "1" = or
  { first.ed 't := }
  { s "second" = s "2" = or
    { second.ed 't := }
    { s "third" = s "3" = or
      { third.ed 't := }
      { s "fourth" = s "4" = or
        { fourth.ed 't := }
        { s "fifth" = s "5" = or
          { fifth.ed 't := }
          { s #1 #1 substring$ is.num
            { s th.ed * 't := }
            { edition 't := }
            if$
          }
          if$
        }
        if$
      }
      if$
    }
    if$
  }
  if$
  t
}

FUNCTION {format.edition}
{ edition empty$
     { "" }
     { "\jbedition {" * convert.edition "~\editionname {}\jbaensep} " * }% dot or not ???????
  if$
}

FUNCTION { format.isbn.issn }
{ isbn empty$
   { issn empty$
      { "" }
      { "\jbissn {" issn n.dashify * "}" * }
     if$
   }
   { "\jbisbn {" isbn n.dashify * "}" * }
  if$
}

INTEGERS { multiresult }

FUNCTION {multi.page.check}
{ 't :=
  #0 'multiresult :=
  { multiresult not
    t empty$ not
    and
  }
  { t #1 #1 substring$
    duplicate$ "-" =
    swap$ duplicate$ "," =
    swap$ "+" =
    or or
  { #1 'multiresult := }
  { t #2 global.max$ substring$ 't := }
    if$
  }
  while$
  multiresult
}

FUNCTION {format.pages}
{ pages empty$
     { "" }
     { " \jbPages{" pages n.dashify * "}" *  }
  if$
}

FUNCTION {multi.pagerange.check}
{ 't :=
  #0 'multiresult :=
  { multiresult not
    t empty$ not
    and
  }
  { t #1 #1 substring$
    duplicate$ "-" =
    swap$ duplicate$ "b" =
    swap$ "/" = or or
  { #1 'multiresult := }
  { t #2 global.max$ substring$ 't := }
    if$
  }
  while$
  multiresult
}

FUNCTION {check.missing.pages}
{ pages empty$
    { "Empty pages in " cite$ * warning$ }
    { pages multi.pagerange.check
        { "" * }
        { type$ "article" = type$ "periodical" = or
              { "There's only a starting page, no pagerange in " cite$ * warning$ }
              'skip$
          if$
        }
      if$
    }
  if$
}

FUNCTION {format.pages.book}
{ pages empty$
  { "" }
  { " \jbpages {" pages " \bibtotalpagesname}" *}
  if$
}

FUNCTION {format.totalpages}
{ totalpages empty$
  { "" }
  {
   ", " totalpages "~\bibtotalpagesname" * *
  }
  if$
}

FUNCTION {format.vol.year.num.pages}
{ volume empty$
        { "" }
        { " \artvolumeformat {" volume * "}" *
          year empty$
              { "There's a volume but no year in " cite$ * warning$ }
              'skip$
          if$
        }
  if$
  month empty$
       'skip$
       { "\ " month * * }
  if$
  year empty$
      'skip$
      { " \artyearformat {" year * add.extra.label "}" * * }
  if$
  number empty$
        'skip$
        { "\artnumberformat {" number * "}" * * }
  if$
  pages empty$
       'skip$
       { duplicate$ empty$
                   { pop$ format.pages }
                   { "" format.pages * * }
         if$
       }
  if$
}

FUNCTION {format.vol.bracedyear.num.pages}
{ volume empty$
        { "" }
        { " \pervolumeformat {" volume * "}" *
          year empty$
              { "There's a volume but no year in " cite$ * warning$ }
              'skip$
          if$
        }
  if$
  year empty$
      'skip$
      { " \peryearformat {" year * add.extra.label "}" * * }
  if$
  month empty$
       'skip$
       { ", " month * * }
  if$
  number empty$
        'skip$
        { ", \pernumberformat {" number * "}" * * }
  if$
  pages empty$
       'skip$
       { duplicate$ empty$
                   { pop$ format.pages }
                   { "" format.pages * * }
         if$
       }
  if$
}

FUNCTION {format.chapter.pages}
{ chapter empty$
  'format.pages
    { type empty$
      { "\unskip.\,-- \bibchapterlongname" }
      { "\unskip.\,-- " type * }
    if$
    chapter tie.or.space.connect
    pages empty$
      'skip$
      { format.pages * }
    if$
    }
  if$
}

FUNCTION {format.booktitleaddon}
{ booktitle empty$
  { "" }
  { booktitleaddon empty$
       { "" }
       { booktitleaddon }
    if$
  }
  if$
}

FUNCTION {format.incoll.editor.booktitle}
{ booktitle empty$
  { "" }
  { editor empty$
    { volume empty$
        { "\incolledformat {}{}{" booktitle incollbooktitlemarkup format.booktitleaddon * * "}{}" *
          booktitleaddon empty$
            { "{} " * }
            { "{1} " * }
          if$
        }
        { "\incolledformat {}{}{" booktitle incollbooktitlemarkup format.booktitleaddon * * "}{" * volume * "}" *
            booktitleaddon empty$
              { "{} " * }
              { "{1} " * }
            if$
        }
      if$
    }
    { volume empty$
         { "\incolledformat {"
            editor empty$
               { "" }
               { editor format.editor.names "}" * *
                 editortype empty$
                   { editor num.names$ #1 >
                         { "{\edfont {\editorsname}}{" * }
                         { "{\edfont {\editorname}}{" * }
                     if$
                   }
                   { "{\edfont {(" * editortype * ")}}{" * }
                 if$
               }
            if$
            booktitle incollbooktitlemarkup * format.booktitleaddon * "}{}" *
            booktitleaddon empty$
              { "{} " * }
              { "{1} " * }
            if$
         }
         { "\incolledformat {" *
            editor empty$
               { "" }
               { editor format.editor.names "}" * *
                 editortype empty$
                   { editor num.names$ #1 >
                         { "{\edfont {\editorsname}}{" * }
                         { "{\edfont {\editorname}}{" * }
                     if$
                   }
                   { "{\edfont {(" * editortype * ")}}{" * }
                 if$
               }
            if$
            booktitle incollbooktitlemarkup * format.booktitleaddon * "}{" volume * "}" *
            booktitleaddon empty$
              { "{} " * }
              { "{1} " * }
            if$
         }
      if$
    }
    if$
  }
  if$
}

FUNCTION {format.tr.number.jur}
{ type empty$
   { number empty$
     { " -- \technicalreportname {} " }
     { "~(" number * ").\,-- \technicalreportname {} " * }
     if$
   }
   { number empty$
     { " -- " type  * }
     { "~(" number * ").\,-- " type * " " * * }
     if$
   }
  if$
}

FUNCTION {format.article.crossref.bracedyear}
{ key empty$
    { journal empty$
        { "Need key or journal for " cite$ * " to crossref " * crossref * warning$ "" }
        { "\bibJTsep\bibjtfont {" journal * check.punct.instead.of.add.period.art *  }
      if$
      volume empty$
        { "No volume in " cite$ * warning$ }
        { " \pervolumeformat {" volume * "} " *  }
      if$
      year empty$
        { "No year in " cite$ * warning$ }
        { "\peryearformat {" year * add.extra.label "}" * * }
      if$
      pages empty$
        'skip$
        { duplicate$ empty$
            { pop$ format.pages }
            { format.pages * }
          if$
        }
      if$
    }
    { "" key * }
  if$
  "\ \protect\jbcrossrefchecked {" * crossref * "}\unskip" *
}

FUNCTION {format.article.crossref}
{ key empty$
    { journal empty$
        { "Need key or journal for " cite$ * " to crossref " * crossref * warning$ "" }
        { "\bibJTsep\bibjtfont {" journal * check.punct.instead.of.add.period.art *  }
      if$
    }
    { "" key * }
  if$
  year empty$
      'skip$
      { year * }
  if$
  " \protect\jbcrossrefchecked {" crossref * "}" *
}

FUNCTION {format.book.crossref}
{ editor empty$
  editor field.or.null author field.or.null =
  or
  { key empty$
    { series empty$
      { "Need editor, key, or series for " cite$ * " to crossref " * crossref * warning$ "" * }
      { "" * }
      if$
    }
    { key * }
    if$
  }
  { "" * }
  if$
  volume empty$
  { "Empty volume in " cite$ * "'s crossref of " * crossref * warning$ ""
    " \protect\jbcrossrefchecked {" * crossref * "}\unskip" * }
  { " \protect\jbcrossrefchecked[" * volume * "]{" * crossref "}\unskip" * }
  if$
}

FUNCTION {format.incoll.inproc.crossref}
{ " \protect\jbincollcrossref {" * crossref * "}" *
  editor empty$
     { "{}" * }
     { "{1}" * }
  if$
 format.pages % *<== 0.5f removed too.
}

FUNCTION { format.editors.organization }
{ organization empty$
    'skip$
    { type$ "misc" =
        { organization }
        { author empty$
            { editor empty$
                { " " organization * " \organizationname {}" * }
                { "; " organization * " \organizationname {}" * }
              if$
            }
            { "; " organization * " \organizationname {}" * }
          if$
        }
      if$
    }
  if$
}

FUNCTION {format.address.organization.manual}
{ author empty$
    { organization empty$
        { address empty$
             'skip$
             { address output part.of.sentence
               year empty$ not { "\bibbdsep {}" *} 'skip$ if$
             }
          if$
        }
        'skip$
      if$
    }
    { address empty$
         { organization empty$
             'skip$
             { organization output part.of.sentence
               year empty$ not { "\bibbdsep {}" *} 'skip$ if$
             }
           if$
         }
         { organization empty$
             { address output part.of.sentence }
             { address "\bpubaddr {} " *  organization * output part.of.sentence }
           if$
           year empty$ not { "\bibbdsep {}" *} 'skip$ if$
         }
      if$
    }
  if$
}

FUNCTION {article}
{ output.bibitem
  format.authors "author" output.check
  set.after.author.sep output
  format.artperiodincoll.title "title" output.check
  crossref missing$
      { journal article.in.journal output.nonnull
        new.sentence
        format.vol.year.num.pages output
      }
      { format.article.crossref output.nonnull }
  if$
  format.url output
  format.note
  format.isbn.issn output
  format.howcited.artperiod output
  check.missing.pages
  fin.entry.endnote
}

FUNCTION {commented}
{ output.bibitem
  author empty$
    { editor empty$
        { format.founders }
        { format.founders format.editors "editor" output.check }
      if$
    }
    { editor empty$
        { format.authors format.founders output.nonnull }
        { format.authors format.founders format.editors output.nonnull }
      if$
    }
  if$
  set.after.author.sep output
  crossref missing$
    { format.btitle.vol "title" output.check }
    { format.btitle "title" output.check }
  if$
  format.volumetitle output
  format.edition output
  format.address.publisher.year "publisher" output.check
  format.update
  new.sentence
  crossref missing$
    { format.series.number output }
    { format.book.crossref output.nonnull }
  if$
  format.url output
  format.pages output
  format.note
  format.howcited.comment output
  fin.entry.endnote
}

FUNCTION {periodical}
{ output.bibitem
  format.authors "author" output.check
  set.after.author.sep output
  format.artperiodincoll.title "title" output.check
  crossref missing$
    { journal article.in.journal output.nonnull
      new.sentence
      format.vol.bracedyear.num.pages output
    }
    { new.sentence format.article.crossref.bracedyear output.nonnull }
  if$
  format.url output
  format.note
  format.isbn.issn output
  format.howcited.artperiod output
  fin.entry.endnote
}

FUNCTION {book}
{ output.bibitem
  author empty$
    { editor empty$
        { "" "author and editor" output.check }
        { format.editors output.nonnull }
      if$
    }
    { editor empty$
        { format.authors output.nonnull }
        { format.authors "\jbtiafed {" format.editors * "}" * output.nonnull }
      if$
    }
  if$
  set.after.author.sep output
  crossref missing$
    { format.btitle.vol "title" output.check }
    { format.btitle "title" output.check }
  if$
  author empty$ not editor empty$ not and
      { "\jbedafti {\edbyname {} " editor * "," * * "} " * }
      'skip$
  if$
  make.translators output
  format.volumetitle output
  format.edition output
  format.address.publisher.year "publisher" output.check
  new.sentence
  format.juradiss.book output
  crossref missing$
    { format.series.number output }
    { format.book.crossref output.nonnull }
  if$
  format.url output
  format.pages output
  format.totalpages output
  format.note
  format.isbn.issn output
  format.howcited output
  fin.entry.endnote
}

FUNCTION {inbook}
{ output.bibitem
  author empty$
    { format.editors "author and editor" output.check }
    { editor empty$
        { format.authors output.nonnull }
        { format.authors format.editors output.nonnull }
      if$
    }
  if$
  set.after.author.sep output
  crossref missing$
  { chapter empty$
      { "There's no chapter in " cite$ * warning$ "" * }
      { type empty$
          { "\Bibchaptername{}" }
          { type }
        if$
        chapter tie.or.space.connect " In " * *
      }
    if$
    format.btitle.vol.inbook "title" output.check
    make.translators output
    format.volumetitle output
    format.edition output
    format.address.publisher.year "publisher" output.check
    new.sentence
    format.series.number output
    format.url output
    format.pages "pages" output.check
    format.note
    format.isbn.issn output
  }
  { chapter empty$
      { "There's no chapter in " cite$ * warning$ "" *
        format.btitle.vol.inbook "title" output.check
      }
      { type empty$
        { "\Bibchaptername{}" }
        { type }
      if$
        chapter tie.or.space.connect "" * *
      }
    if$
    format.volumetitle output
    format.book.crossref output.nonnull
    format.url output
    format.pages "pages" output.check
    format.note
  }
  if$
  part.of.sentence
  format.howcited output
  fin.entry.endnote
}

FUNCTION {incollection}
{ output.bibitem
  format.authors "author" output.check
  set.after.author.sep output
  format.artperiodincoll.title "title" output.check
  make.translators output
  crossref missing$
    { format.incoll.editor.booktitle "booktitle" output.check
      format.volumetitle output
      format.edition output
      format.address.publisher.year "publisher" output.check
      new.sentence
      format.series.number output
      format.url output
      format.isbn.issn output
      part.of.sentence
      format.chapter.pages output
      format.note
    }
    { format.volumetitle output
      format.incoll.inproc.crossref output.nonnull
      format.url output
      format.note
    }
  if$
  format.howcited output
  check.missing.pages
  fin.entry.endnote
}

FUNCTION {inproceedings}
{ output.bibitem
  format.authors "author" output.check
  set.after.author.sep output
  format.artperiodincoll.title "title" output.check
  crossref missing$
  { format.incoll.editor.booktitle "booktitle" output.check
    address empty$
      { organization new.sentence.checka
        organization output
        part.of.sentence
        format.address.publisher.year output
      }
      { format.address.publisher.year "publisher" output.check }
    if$
    new.sentence
    series empty$
      'skip$
      { format.series.number output }
    if$
    format.url output
    format.note
    format.isbn.issn output
    part.of.sentence
    format.pages output
  }
  { format.incoll.inproc.crossref output.nonnull
    format.url output
    format.note
  }
  if$
  format.howcited output
  fin.entry.endnote
}

FUNCTION {conference}{inproceedings}

FUNCTION {manual}
{ output.bibitem
  author empty$
    { organization empty$
        'skip$
        { "\bibnf{" organization * "} {} {} {} {}" * output.nonnull }
      if$
    }
    { format.authors output.nonnull }
  if$
  set.after.author.sep output
  format.btitle "title" output.check
  format.edition output
  format.address.organization.manual
  format.date output
  pages set.period.dash.check
  format.pages.book output
  format.url output
  format.note
  format.howcited output
  fin.entry.endnote
}

FUNCTION {mastersthesis}
{ output.bibitem
  format.authors "author" output.check
  set.after.author.sep output
  format.btitle "title" output.check
  format.thesis output
  set.comma.pages.check
  pages new.sentence.checka
  format.pages output
  format.url output
  format.note
  format.howcited output
  fin.entry.endnote
}

FUNCTION {phdthesis}
{ output.bibitem
  format.authors "author" output.check
  set.after.author.sep output
  format.btitle "title" output.check
  format.thesis output
  set.comma.pages.check
  pages new.sentence.checka
  format.pages output
  format.url output
  format.note
  format.howcited output
  fin.entry.endnote
}

FUNCTION {jurthesis}
{ output.bibitem
  format.authors "author" output.check
  set.after.author.sep output
  format.btitle "title" output.check
  format.thesis output
  set.comma.pages.check
  pages new.sentence.checka
  format.pages output
  format.url output
  format.note
  format.howcited output
  fin.entry.endnote
}

FUNCTION {booklet}
{ output.bibitem
  format.authors "author" output.check
  set.after.author.sep output
  format.title "title" output.check
  format.howpublished.address.year output
  format.note
  format.url output
  format.howcited output
  fin.entry.endnote
}

FUNCTION {misc}
{ output.bibitem
  format.authors "author" output.check
  set.after.author.sep output
  format.title output
  format.howpublished.address.year output
  format.note
  format.url output
  format.howcited output
  fin.entry.endnote
}

FUNCTION {proceedings}
{ output.bibitem
  editor empty$
  { organization empty$
     'skip$
     { "\biblnfont {" organization * " \organizationname}" * output }
    if$
  }
  { format.editors output.nonnull }
  if$
  set.after.author.sep output
  format.btitle "title" output.check
  new.sentence
  editor empty$
    'skip$
    {  format.proceed.organization output }
  if$
  new.sentence
  format.series.number output.nonnull
  volume empty$
     { "" output.nonnull }
     { "\volumeformat {" volume * "} " * "volume" output.check }
  if$
  format.address.publisher.year "publisher" output.check
  pages set.period.dash.check
  format.pages.book output
  format.url output
  format.note
  format.isbn.issn output
  format.howcited output
  fin.entry.endnote
}

FUNCTION {techreport}
{ output.bibitem
  author empty$
    { format.editors "author and editor" output.check }
    { editor empty$
        { format.authors output.nonnull }
        { format.authors format.editors output.nonnull }
      if$
    }
  if$
  set.after.author.sep output
  format.title "title" output.check
  institution new.sentence.checka
  format.address.publisher.year output
  number new.sentence.checka
  format.tr.number.jur "number" output.check
  pages set.period.dash.check
  format.pages.book output
  format.url output
  format.note
  format.isbn.issn output
  format.howcited output
  fin.entry.endnote
}

FUNCTION {www}
{ output.bibitem
  format.authors "author" output.check
  set.after.author.sep output
  format.naked.url output
  format.howcited output
  fin.entry.endnote
}

FUNCTION {lexicon}
{ output.bibitem
  set.after.author.sep output
  crossref missing$
    { format.btitle.vol "title" output.check }
    { format.btitle "title" output.check }
  if$
  author empty$
      { editor empty$
            'skip$
            { "\edbyname{} " * editor format.editor.names "," * *  }
        if$
      }
      { "\byname{} " author format.names * "," * * }
  if$
  make.translators output
  format.volumetitle output
  format.edition output
  format.address.publisher.year "publisher" output.check
  new.sentence
  format.juradiss.book output
  crossref missing$
    { format.series.number output }
    { format.book.crossref output.nonnull }
  if$
  format.url output
  format.pages output
  format.totalpages output
  format.note
  format.isbn.issn output
  format.howcited output
  fin.entry.endnote
}

STRINGS { last.archive last.subarchive }

FUNCTION {init.last.archive }
{ "" 'last.archive :=
  "" 'last.subarchive := }

FUNCTION {archival}
{ output.bibitem
  archive empty$
    { "" 'last.archive := }
    { archive last.archive =
        { "} {" archive format.name.sig * "} {} {\jbsamearch{} " * *  }
        { "\bibanfont{" archive *  "archive" output.check
          shortarchive empty$
              'skip$
              { " \jbshortarchformat{" shortarchive * "}" * * }
          if$
          "}" *
          "} {" archive format.name.sig * "} {} {\jbnotsamearch{} " * *
        }
      if$
      archive 'last.archive :=
    }
  if$
  subarchive empty$
    { "" 'last.subarchive := }
    { subarchive last.subarchive =
        'skip$
        { subarchive output
          shortsubarchive empty$
              'skip$
              { " \jbshortsubarchformat{" shortsubarchive * "}" * * }
          if$
          "\jbsubarchsep{} " *
        }
      if$
      subarchive 'last.subarchive :=
    }
  if$
  sig1 empty$
     'skip$
     { "\jbarchsig {" *
       subarchive empty$
          'skip$
          { "\jbsamesubarchindent{} " * }
       if$
       sig1 *
       sig2 empty$
          'skip$
          { ". " sig2 * *
            sig3 empty$
               'skip$
               { ". " sig3 * *
                 sig4 empty$
                    'skip$
                    { ". " sig4 * * }
                 if$
               }
            if$
          }
       if$
       "} {" *
     }
  if$
  archname missing$
      { "}" * }
      { archname "}" * output }
  if$
  format.howcited output
  fin.entry.endnote
}

FUNCTION {unpublished}{misc}

FUNCTION {default.type}{misc}

MACRO {jan} {"\janname\ "}
MACRO {feb} {"\febname\ "}
MACRO {mar} {"\marname\ "}
MACRO {apr} {"\aprname\ "}
MACRO {may} {"\mayname\ "}
MACRO {jun} {"\junname\ "}
MACRO {jul} {"\julname\ "}
MACRO {aug} {"\augname\ "}
MACRO {sep} {"\sepname\ "}
MACRO {oct} {"\octname\ "}
MACRO {nov} {"\novname\ "}
MACRO {dec} {"\decname\ "}

READ

FUNCTION {sortify}{ purify$ "l" change.case$ }

INTEGERS { len }

FUNCTION {chop.word}
{ 's :=
  'len :=
  s #1 len substring$ =
  { s len #1 + global.max$ substring$ }
  's
  if$
}

FUNCTION {format.lab.names}
{ 's :=                                  % for two: (Jones/de~Bruijn)
   s #1 "{vv~}{ll}" format.name$         % for three: (Jones/de~Bruijn/Smith)
   s num.names$ duplicate$               % for more: (Jones et\,al.)
   #2 <
   'pop$                                 % for just one person
   { duplicate$ duplicate$
     #3 >
     swap$ s swap$ "{ff }{vv }{ll}{ jj}" format.name$ "others" =
     or
     { pop$ "\Bibetal" * }              % for 4 or more, or last is `others'
     { #2 =
       {  "\jbbtasep " * s #2 "{vv~}{ll}" format.name$ * } % for (exactly) two
       { "\jbbfsasep " * s #2 "{vv~}{ll}" format.name$ *   % for three
         "\jbbstasep " * s #3 "{vv~}{ll}" format.name$ *
       }
       if$
     }
     if$
   }
   if$
   year missing$
      'skip$
      { "\jbdy {" year * "}" * * }% dummy year to prevent from `1993a' and `2001b' for works by the same author
   if$
}

FUNCTION {format.editor.lab.names}
{ 's :=                                  % for two: (Jones/de~Bruijn)
  s #1 "{vv~}{ll}" format.name$         % for three: (Jones/de~Bruijn/Smith)
  s num.names$ duplicate$               % for more: (Jones et\,al.)
  #2 <
  'pop$                                 % for just one person
  { duplicate$ duplicate$
    #3 >
    swap$ s swap$ "{ff }{vv }{ll}{ jj}" format.name$ "others" =
    or
    { pop$ "\Bibetal" * }              % for 4 or more, or last is `others'
    { #2 =
      {  "\jbbtesep " * s #2 "{vv~}{ll}" format.name$ * } % for (exactly) two
      { "\jbbfsesep " * s #2 "{vv~}{ll}" format.name$ *   % for three
        "\jbbstesep " * s #3 "{vv~}{ll}" format.name$ *
      }
      if$
    }
    if$
  }
  if$
  year missing$
      'skip$
     { "\jbdy {" year * "}" * * }% dummy year to prevent from `1993a' and `2001b' for works by the same author
  if$
}

FUNCTION {author.key.label}
{ author empty$
  { key empty$
    { cite$ #1 #3 substring$ }
      'key
    if$
  }
  { author format.lab.names }
  if$
}

FUNCTION {author.editor.key.label}
{ author empty$
  { editor empty$
    { key empty$
      { cite$ #1 #3 substring$ }
        'key
      if$
    }
    { editor format.editor.lab.names }
    if$
  }
  { author format.lab.names }
  if$
}

FUNCTION {editor.key.label}
{ editor empty$
  { key empty$
    { cite$ #1 #3 substring$ }
      'key
    if$
  }
  { editor format.editor.lab.names }
  if$
}

FUNCTION {calc.label}
{ type$ "book" = type$ "inbook" = or type$ "incollection" = or type$ "commented" = or type$ "lexicon" = or
  'author.editor.key.label
  { type$ "proceedings" =
    'editor.key.label
    'author.key.label
    if$
  }
  if$
  'label :=
}

FUNCTION {calc.dummy.label}
{ type$ "book" = type$ "inbook" = or type$ "incollection" = or type$ "commented" = or
  'author.editor.key.label
  { type$ "proceedings" =
    'editor.key.label
    'author.key.label
    if$
  }
  if$
  'dummy.label :=
}

FUNCTION {sort.format.names}
{ 's :=
  #1 'nameptr :=
  ""
  s num.names$ 'numnames :=
  numnames 'namesleft :=
  { namesleft #0 > }
  { nameptr #1 >
  { "   " * }
  'skip$
    if$
    s nameptr "{ll{ }}{  ff{ }}{ vv{ }}{  jj{ }}" format.name$ 't :=
    nameptr numnames = t "\bibnf {others} {} {} {} {}" = and
  { "\Bibetal" * }
  { t sortify * }
    if$
    nameptr #1 + 'nameptr :=
    namesleft #1 - 'namesleft :=
  }
  while$
}

FUNCTION {sort.format.title}
{ 't :=
  "A " #2
  "An " #3
    "Der " #4
    "Die " #4
      "Das " #4
      "Ein " #4
        "Eine " #5
          "The " #4 t chop.word
         chop.word
       chop.word
       chop.word
     chop.word
     chop.word
  chop.word
  chop.word
  sortify
  #1 global.max$ substring$
}

FUNCTION {author.sort}
{ author empty$
  { key empty$
  {
%%    "to sort, need author or key in " cite$ * warning$
    ""
  }
  { key sortify }
    if$
  }
  { author sort.format.names }
  if$
}

FUNCTION {author.editor.sort}
{ author empty$
  { editor empty$
  { key empty$
    {
%%        "to sort, need author, editor, or key in " cite$ * warning$
      ""
    }
    { key sortify }
    if$
  }
  { editor sort.format.names }
    if$
  }
  { author sort.format.names }
  if$
}

FUNCTION {editor.sort}
{ editor empty$
  { key empty$
    { "to sort, need editor or key in " cite$ * warning$ "" }
    { key sortify }
    if$
  }
  { editor sort.format.names }
  if$
}

FUNCTION {archival.sort}
{ archive empty$
   { shortarchive empty$
      { "to sort, need archive or shortarchive in " cite$ * warning$ "" }
      { shortarchive sortify }
    if$
  }
  { archive sortify }
  if$
}

FUNCTION {presort}
{ calc.label
  calc.dummy.label
  dummy.label sortify " " *
  sortkey empty$
     { type$ "book" =
         type$ "incollection" =    or
           type$ "inbook" =        or
              type$ "commented" =  or
            'author.editor.sort
            { type$ "proceedings" =
                'editor.sort
                { type$ "archival" =
                      'archival.sort
                      'author.sort
                  if$
                }
              if$
            }
        if$
     }
     { sortkey sort.format.names }
  if$
  type$ "archival" = not
     { "    "
       *
       year field.or.null sortify
       *
       "    "
       *
       title field.or.null
       sort.format.title
       *
     }
     { "    "
       *
       subarchive field.or.null sortify
       *
       "    "
       *
       sig1 field.or.null sortify
       *
       "    "
       *
       sig2 field.or.null sortify
       *
       "    "
       *
       sig3 field.or.null sortify
       *
       "    "
       *
       sig4 field.or.null sortify
       *
     }
  if$
   #1 entry.max$ substring$
   'sort.label :=
   sort.label *
   #1 entry.max$ substring$
   'sort.key$ :=
}

ITERATE {presort}

%% FUNCTION {before.sort} { "BEFORE SORT:" top$ }
%% EXECUTE {before.sort}
%% FUNCTION {print.sort.keys} {sort.key$ top$}
%% ITERATE {print.sort.keys}

SORT

%% FUNCTION {after.sort} {"AFTER SORT:" top$}
%% EXECUTE {after.sort}
%% ITERATE {print.sort.keys}


INTEGERS { last.extra.num number.label extra.extra.num }

FUNCTION {make.extra.label}
{ last.extra.num #122 <
     { last.extra.num #1 + }
     { extra.extra.num #0 =
         { "a" chr.to.int$ }
         { extra.extra.num #1 + }
      if$
      'extra.extra.num :=
      "a" chr.to.int$ }
  if$
  'last.extra.num :=
  extra.extra.num #0 =
     { last.extra.num int.to.chr$ }
     { extra.extra.num int.to.chr$ 'extra.label :=
       extra.label last.extra.num int.to.chr$ * }
  if$
}

FUNCTION {forward.pass}
{ w dummy.label =
    { make.extra.label 'extra.label := }
    { "a" chr.to.int$ 'last.extra.num :=
       #0 'extra.extra.num :=
       "" 'extra.label :=
       dummy.label 'w :=
    }
 if$
 number.label #1 + 'number.label :=
}

FUNCTION {reverse.pass}
{ x "b" =
    { "a" 'extra.label := }
    'skip$
 if$
 extra.label 'x :=
 extra.label
 duplicate$ empty$
    'skip$
    { "" swap$ * }
 if$
 'extra.label :=
 dummy.label extra.label * 'dummy.label :=
}

ITERATE {forward.pass}
REVERSE {reverse.pass}

FUNCTION {bib.sort.order} { sort.label  'sort.key$ := }

ITERATE {bib.sort.order}

SORT

FUNCTION {set.current.authors}
{ author empty$
  { editor empty$
    { organization empty$
      { cite$ 'current-authors := }
      { organization 'current-authors := }
      if$
    }
    { editor format.names #1 entry.max$ substring$ 'current-authors := }
%%           ^^^^^^^^^^^^ NOT format.editor.names, otherwise \jb@@arg is always = 0!!!
    if$
  }
  { author format.names #1 entry.max$ substring$ 'current-authors := }
  if$
}

STRINGS { previous-authors }

FUNCTION {initialize.previous.authors} { "" 'previous-authors := }

FUNCTION {mark.repeat.authors}
{ current-authors previous-authors =
  { #1 'repeat-authors := }
  'skip$
  if$
  current-authors 'previous-authors :=
}

ITERATE {set.current.authors}

EXECUTE {initialize.previous.authors}

ITERATE {mark.repeat.authors}

EXECUTE {initialize.previous.authors}

REVERSE {mark.repeat.authors}

FUNCTION {begin.bib}
{ preamble$ empty$
    'skip$
    { preamble$ write$ newline$ }
  if$
  "%" write$ newline$
  "% This bibliography was produced by using jurabib.bst" write$ newline$
  "%" write$ newline$
  "\begin{thebibliography}{}" write$ newline$
}

EXECUTE {begin.bib}

EXECUTE {init.state.consts}

ITERATE {call.type$}

FUNCTION {end.bib}
{ newline$
  "\end{thebibliography}" write$ newline$
}

EXECUTE {end.bib}
%% 
%%
%% End of file `jurabib.bst'.
