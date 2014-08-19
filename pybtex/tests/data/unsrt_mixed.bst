% BibTeX standard bibliography style `unsrt'
   % Version 0.99b (8-Dec-10 release) for BibTeX versions 0.99a or later.
   % Copyright (C) 1984, 1985, 1988, 2010 Howard Trickey and Oren Patashnik.
   % Unlimited copying and redistribution of this file are permitted as long as
   % it is unmodified.  Modifications (and redistribution of modified versions)
   % are also permitted, but only if the resulting file is renamed to something
   % besides btxbst.doc, plain.bst, unsrt.bst, alpha.bst, and abbrv.bst.
   % This restriction helps ensure that all standard styles are identical.
   % The file btxbst.doc has the documentation for this style.

eNTrY
  { AddreSs
    aUTHoR
    BOoKTiTLe
    ChAPTER
    EditIon
    editoR
    hOwPubliSHeD
    instITuTIon
    JoURNAl
    keY
    mONTh
    note
    NumbeR
    oRgANIZaTIon
    pAgES
    puBLisHER
    scHooL
    series
    TITlE
    type
    volumE
    yEAR
  }
  {}
  { LaBEl }

INTegErs { oUTPUt.stAtE Before.aLL mId.senTeNCE afTEr.SenTENce AFtER.bloCk }

funcTioN {Init.sTatE.consTS}
{ #0 'BEFOre.aLL :=
  #1 'Mid.seNTeNcE :=
  #2 'aFtER.seNTeNcE :=
  #3 'aFTeR.BLoCK :=
}

stRIngs { S t }

FUnCTiON {oUTpUT.nONnULl}
{ 'S :=
  ouTPUt.sTAte mid.sEnTENce =
    { ", " * WriTe$ }
    { outPut.stATE afTeR.blOcK =
        { add.periOD$ writE$
          NEwlInE$
          "\newblock " wRitE$
        }
        { Output.StatE beFoRE.aLl =
            'WRiTE$
            { ADd.periOd$ " " * Write$ }
          iF$
        }
      IF$
      Mid.SEntence 'Output.StATE :=
    }
  iF$
  s
}

FuNctioN {outPuT}
{ DuPLIcate$ eMPty$
    'pop$
    'oUTput.nonNUll
  If$
}

FUNCtiON {oUtpuT.cHeCK}
{ 'T :=
  dUplicate$ empty$
    { Pop$ "empty " t * " in " * cItE$ * wARniNg$ }
    'OuTput.NonnuLl
  if$
}

FUnCtioN {outpUT.BIbitem}
{ newLIne$
  "\bibitem{" wRite$
  cItE$ WrItE$
  "}" WriTe$
  NEWLIne$
  ""
  BeFore.all 'outPuT.sTate :=
}

fuNcTION {FIn.enTRy}
{ add.PEriOd$
  write$
  nEwlIne$
}

FuncTiON {New.BloCk}
{ OutpuT.StaTe BefOrE.All =
    'SKip$
    { AFteR.bLoCk 'oUtpuT.staTe := }
  iF$
}

FUNCTION {nEw.SentENce}
{ outpuT.StatE AfteR.block =
    'sKip$
    { outPuT.sTate bEfoRE.all =
        'skIp$
        { aFTER.SenTence 'ouTpuT.sTAtE := }
      if$
    }
  If$
}

funCTIoN {nOT}
{   { #0 }
    { #1 }
  if$
}

fuNctiOn {And}
{   'sKip$
    { pop$ #0 }
  iF$
}

fUNCTIoN {or}
{   { pOp$ #1 }
    'sKIp$
  iF$
}

funcTiOn {nEw.bLock.cheCKa}
{ eMPty$
    'sKIp$
    'nEW.BlocK
  iF$
}

fUnCtIon {NEw.BLOcK.ChecKB}
{ EMPtY$
  Swap$ Empty$
  aND
    'skip$
    'neW.bLocK
  IF$
}

funCtiON {neW.seNteNCE.cheCKa}
{ eMPty$
    'skIP$
    'NEw.SenteNcE
  If$
}

FUncTioN {nEw.sentenCe.chEckb}
{ EmptY$
  SwaP$ empTY$
  aNd
    'skIp$
    'NeW.SentENce
  IF$
}

functIoN {field.Or.NulL}
{ dupLIcaTe$ eMPTy$
    { pop$ "" }
    'SKip$
  if$
}

FuNCtiOn {emPhASiZE}
{ dupLiCATE$ eMPTY$
    { poP$ "" }
    { "{\em " swAp$ * "}" * }
  if$
}

INTEGeRS { naMepTr nAMeSleFt NUmNAmes }

FUNCtiON {foRmat.nameS}
{ 's :=
  #1 'nAMeptR :=
  s nuM.nAmeS$ 'NUmNAmES :=
  numnAMeS 'naMeslEFt :=
    { NaMEslEft #0 > }
    { S NamEptr "{ff~}{vv~}{ll}{, jj}" fOrmAt.NAme$ 'T :=
      nAmeptR #1 >
        { NAMEslefT #1 >
            { ", " * T * }
            { nUMNames #2 >
                { "," * }
                'sKiP$
              IF$
              t "others" =
                { " et~al." * }
                { " and " * t * }
              IF$
            }
          IF$
        }
        't
      iF$
      nAMEptr #1 + 'NAMeptr :=
      nameSlEft #1 - 'NameSleft :=
    }
  while$
}

FUNCtiOn {formAT.AUtHORS}
{ auTHoR emPTy$
    { "" }
    { AUthoR FormAt.NAmeS }
  if$
}

fUNCTion {formAt.eDiTors}
{ eDItOR Empty$
    { "" }
    { EDIToR FoRmat.nameS
      EDitor NUm.NameS$ #1 >
        { ", editors" * }
        { ", editor" * }
      If$
    }
  if$
}

funcTiON {foRMAt.title}
{ tiTLe EMpty$
    { "" }
    { titlE "t" chaNgE.Case$ }
  iF$
}

FUNCTiOn {N.DaShifY}
{ 'T :=
  ""
    { t eMPtY$ noT }
    { T #1 #1 sUBStrIng$ "-" =
        { t #1 #2 SuBStRiNG$ "--" = nOT
            { "--" *
              T #2 glObal.MAX$ suBstriNG$ 't :=
            }
            {   { t #1 #1 subSTRiNG$ "-" = }
                { "-" *
                  t #2 GloBAl.Max$ SUbsTRing$ 'T :=
                }
              wHIle$
            }
          iF$
        }
        { t #1 #1 substriNG$ *
          T #2 GlobaL.maX$ subsTrIng$ 't :=
        }
      iF$
    }
  WHile$
}

FuncTion {FOrmAt.dAte}
{ yeAr EmptY$
    { MonTh emPty$
        { "" }
        { "there's a month but no year in " CItE$ * WaRNInG$
          MoNth
        }
      if$
    }
    { MOntH EmPTY$
        'YeaR
        { MOnth " " * yEaR * }
      If$
    }
  If$
}

FunCTioN {foRMAt.btitle}
{ titLe emphasize
}

Function {TIe.or.spAcE.CoNNeCt}
{ dupliCATE$ text.Length$ #3 <
    { "~" }
    { " " }
  if$
  swap$ * *
}

FUnCtION {EIther.or.checK}
{ EMptY$
    'pOP$
    { "can't use both " swAp$ * " fields in " * cite$ * wARNInG$ }
  iF$
}

FUNCTIon {formaT.bvOlUMe}
{ VOlumE eMPTy$
    { "" }
    { "volume" VolUME tIE.or.spacE.coNnect
      SErIes empty$
        'SkIP$
        { " of " * SErieS emphasiZe * }
      if$
      "volume and number" nUMbER EiTHEr.OR.CHecK
    }
  if$
}

FuNCtioN {fOrmat.nUmbEr.sErieS}
{ VoLume eMpty$
    { NUmBEr EMptY$
        { SErIes fIeLd.or.NUll }
        { OUTput.STATE mid.SentENcE =
            { "number" }
            { "Number" }
          iF$
          NuMBer Tie.OR.spAce.cOnNect
          sEries EMptY$
            { "there's a number but no series in " Cite$ * wARninG$ }
            { " in " * sEriEs * }
          iF$
        }
      if$
    }
    { "" }
  iF$
}

fUnCTIoN {forMAt.EDiTion}
{ edItion EmPty$
    { "" }
    { output.statE Mid.senTenCe =
        { EditION "l" chaNgE.cAsE$ " edition" * }
        { eDition "t" chAnge.Case$ " edition" * }
      iF$
    }
  if$
}

iNTeGErs { mulTIResult }

fUNcTiON {MUlti.paGe.CHeck}
{ 't :=
  #0 'MulTIResuLt :=
    { mUlTIresUlT not
      T eMpty$ noT
      ANd
    }
    { T #1 #1 substRInG$
      duplicAtE$ "-" =
      Swap$ DupLicATE$ "," =
      Swap$ "+" =
      or or
        { #1 'muLtiresuLT := }
        { t #2 glObAL.mAx$ SUbsTRiNg$ 't := }
      If$
    }
  while$
  mUltiREsuLt
}

funCtION {FormAT.Pages}
{ paGES empTY$
    { "" }
    { pages mulTI.PaGE.cHeCk
        { "pages" paGEs n.dashify tie.or.spAce.connEct }
        { "page" PagEs tiE.or.SPaCe.Connect }
      If$
    }
  if$
}

FUNCtiOn {FoRmat.Vol.Num.PageS}
{ vOluMe fIelD.oR.nULl
  Number EMpTy$
    'skip$
    { "(" NumBeR * ")" * *
      voLUme eMpTy$
        { "there's a number but no volume in " citE$ * Warning$ }
        'sKIp$
      if$
    }
  if$
  PagEs emptY$
    'skIp$
    { duPliCATe$ EMpTy$
        { POp$ FORMaT.paGes }
        { ":" * paGes N.dasHIfY * }
      If$
    }
  If$
}

FUncTIon {ForMAT.ChAPter.Pages}
{ CHaptEr empty$
    'FormAT.PageS
    { TYPe emPTy$
        { "chapter" }
        { typE "l" CHANGe.CAsE$ }
      iF$
      CHApTER tIe.Or.sPaCe.connect
      paGes eMpty$
        'SkIP$
        { ", " * FORMAt.PaGes * }
      iF$
    }
  IF$
}

fuNCtiON {foRmAT.in.ed.booKtiTLe}
{ BOoktITlE EMPty$
    { "" }
    { Editor EmpTY$
        { "In " boOKtITLE eMphaSiZE * }
        { "In " format.eDiTORs * ", " * BooKtitlE eMPHasizE * }
      If$
    }
  IF$
}

FUNCtIon {EMpty.MisC.Check}
{ auThOr EmpTy$ tiTLe eMpTy$ hOwPUbLISHED EmPty$
  MontH emPtY$ yEAr empty$ note emPtY$
  anD aND aND AnD and
    { "all relevant fields are empty in " ciTe$ * wArnInG$ }
    'skip$
  if$
}

funCtion {ForMAT.thesiS.type}
{ tyPe EmpTy$
    'skip$
    { pop$
      Type "t" chAnge.casE$
    }
  If$
}

FUncTioN {foRMAT.Tr.Number}
{ Type EmPty$
    { "Technical Report" }
    'tyPE
  if$
  NuMBer EMpTy$
    { "t" CHANGe.caSe$ }
    { nUmBer tie.OR.spAcE.coNNecT }
  iF$
}

fUNctIoN {forMAt.arTIcle.cROSSREf}
{ kEY EMPty$
    { jOURnaL emPty$
        { "need key or journal for " cItE$ * " to crossref " * CRossref *
          waRnIng$
          ""
        }
        { "In {\em " JOUrNal * "\/}" * }
      if$
    }
    { "In " key * }
  iF$
  " \cite{" * crossref * "}" *
}

FuNCTION {Format.CROsSReF.eDItoR}
{ EDitOr #1 "{vv~}{ll}" formAt.naMe$
  ediTOr nuM.nAmes$ dUPLiCaTe$
  #2 >
    { poP$ " et~al." * }
    { #2 <
        'sKIP$
        { eDitOr #2 "{ff }{vv }{ll}{ jj}" forMaT.name$ "others" =
            { " et~al." * }
            { " and " * EDitor #2 "{vv~}{ll}" FoRMAt.naMe$ * }
          If$
        }
      IF$
    }
  if$
}

funCTiOn {fOrmaT.book.CROssReF}
{ voLUMe EMptY$
    { "empty volume in " ciTE$ * "'s crossref of " * crOsSreF * waRNing$
      "In "
    }
    { "Volume" volumE tIE.oR.SpacE.CoNnECT
      " of " *
    }
  if$
  ediTor empty$
  EdITor FIElD.or.Null AUTHoR fIelD.or.nulL =
  oR
    { key eMpty$
        { SeRiEs emPty$
            { "need editor, key, or series for " ciTE$ * " to crossref " *
              cROSSrEf * waRnIng$
              "" *
            }
            { "{\em " * seRiEs * "\/}" * }
          If$
        }
        { Key * }
      iF$
    }
    { FoRmat.cRoSsREF.editor * }
  IF$
  " \cite{" * cRossrEF * "}" *
}

fUNCTION {FORmAT.inCoLL.inproC.CrossrEf}
{ edITor empty$
  editor FieLd.oR.NuLL aUTHor FIelD.OR.nUlL =
  Or
    { key emptY$
        { bOokTItle EmpTy$
            { "need editor, key, or booktitle for " CitE$ * " to crossref " *
              CroSSReF * WARning$
              ""
            }
            { "In {\em " bOokTitle * "\/}" * }
          If$
        }
        { "In " kEy * }
      if$
    }
    { "In " fOrMAT.CROSsReF.edIToR * }
  If$
  " \cite{" * croSsref * "}" *
}

fUnCtioN {article}
{ oUtPuT.BibitEm
  forMat.auTHors "author" OUtPuT.cHEcK
  nEw.blOck
  foRMaT.TitlE "title" OutPut.cHEcK
  new.bLOCK
  cRoSSref mIssInG$
    { JOurnal EMpHasIZE "journal" outpUt.cHEcK
      FormaT.VoL.NUm.pAges OutpUt
      FOrMat.DaTE "year" oUtPUt.cHeCk
    }
    { FormAT.aRTiCle.CroSSRef ouTpuT.nONNUll
      fORmAt.pagEs oUtPUT
    }
  if$
  new.blocK
  note oUTpUT
  fIN.EntRy
}

funCtIon {book}
{ outPuT.BibItem
  AuthOr empTy$
    { fOrmAT.edItoRs "author and editor" oUTput.checK }
    { FormAt.authORs oUtpUt.noNNull
      CrosSref MisSing$
        { "author and editor" EDiTor EItHER.oR.CHeck }
        'SKIp$
      IF$
    }
  if$
  new.bLOcK
  fORMaT.btitle "title" OUtpuT.ChEck
  cRoSsref MissinG$
    { fORMAT.bVolUme Output
      new.BLock
      ForMAt.NumbEr.SERiEs oUTPUT
      New.SENTEnce
      publiSheR "publisher" OuTput.ChEcK
      aDdResS oUtpUt
    }
    { new.BloCK
      forMat.boOk.crOSsrEF ouTPut.NonnuLl
    }
  iF$
  FormaT.edItioN ouTput
  formAT.DATe "year" ouTPut.CHeck
  new.bLOck
  noTe ouTPuT
  fin.entry
}

FUnCTiOn {boOklET}
{ OUtpUT.biBitem
  ForMat.authors outpUT
  nEW.bloCK
  fOrMat.TItle "title" OUtPuT.CHecK
  hOWPubLIsHeD ADdress nEw.BLock.cHECKB
  hOWpUbliSHed OUTpuT
  Address ouTPut
  FOrMat.daTE oUtPuT
  nEw.blOck
  nOtE OUtPUT
  fIN.eNTry
}

funCTiOn {INbOOK}
{ OutPUT.biBIteM
  Author empTY$
    { FORmAT.eDitors "author and editor" OutPut.cHEcK }
    { FOrmat.AUTHORs OutPUt.nonNull
      CrOSsREf MISSinG$
        { "author and editor" edItor eIther.Or.CHEcK }
        'sKiP$
      iF$
    }
  iF$
  new.bloCk
  foRMAt.bTiTlE "title" outPuT.cHeCk
  crossref MissinG$
    { formAt.BVOlume oUtPut
      FormAT.chaptEr.PAGES "chapter and pages" OuTpuT.cheCk
      New.bLock
      foRmAT.nUmbER.sErIEs OutPut
      NEw.SeNtEnce
      PublisheR "publisher" OutPUt.CHEck
      addReSS output
    }
    { ForMAT.ChaPTeR.pageS "chapter and pages" ouTPut.CHecK
      nEW.blOck
      FormAT.bOOk.crosSREF oUTpUt.NonNuLl
    }
  IF$
  FoRmaT.EditiON outPuT
  formAT.dATe "year" OutpUt.cHecK
  New.Block
  note OUTput
  fiN.eNtrY
}

FuNCtION {INcolleCTIOn}
{ OutpuT.bibitem
  formaT.AuThoRs "author" OUtpUT.ChecK
  New.blOck
  fOrMat.tItle "title" OutpuT.cHeck
  neW.BLock
  cRoSsrEf MIssing$
    { fOrMaT.IN.ed.bOoktITLE "booktitle" OUTput.cHeck
      fOrMAt.BvOlume OutpuT
      FoRMat.NumbeR.Series output
      fORMAt.ChapTEr.pagES outpuT
      New.senTeNCE
      puBlisHer "publisher" outPuT.Check
      AddResS oUtPUt
      forMat.EDitiOn OutPut
      fOrMat.dAtE "year" OutpUt.cHecK
    }
    { forMat.incOLl.Inproc.crossref oUtput.nonnulL
      FOrMAt.ChaptER.pAges outpUT
    }
  if$
  nEw.BlOcK
  nOte ouTput
  fin.eNtry
}

fUNCtIOn {inpRoceEdiNgs}
{ oUtpUT.bIbitEM
  foRMaT.AUthoRS "author" oUtPut.check
  NEw.bloCk
  formAt.TitLE "title" oUtPut.checK
  new.BlocK
  crosSrEF mIssiNG$
    { forMat.in.Ed.bOOkTiTlE "booktitle" oUTPuT.CHeck
      foRMaT.BVoLumE OutPut
      foRMat.numBER.SErIeS oUtPuT
      fORMat.pagEs oUTpUt
      AddREsS eMPty$
        { oRGaNizATIon pUBlisher nEw.SentEnce.cHEcKb
          oRganiZAtion OUTpUt
          pUblIShEr Output
          fOrmAT.daTe "year" Output.check
        }
        { addrEsS outpuT.NoNnull
          format.DaTe "year" oUTPuT.CHecK
          nEw.seNtENCe
          OrgaNIzaTIOn OUTPut
          pUBliSHeR outPuT
        }
      if$
    }
    { forMat.iNCOll.Inproc.CRossref output.noNNUll
      FOrmaT.PageS OuTpUt
    }
  iF$
  NEw.blocK
  NOTE OUTpUT
  fIN.ENTrY
}

functIoN {cONFERencE} { InprocEEDiNGs }

FUNctIon {mANUal}
{ outPUt.BIbiTEM
  AuthoR Empty$
    { ORganIZaTion emPTY$
        'SkIP$
        { oRGaNizatIon outpUT.nOnNull
          addReSs OuTPUT
        }
      If$
    }
    { format.authoRS OUTPuT.nOnnULl }
  If$
  new.bloCK
  FoRmAT.btitLE "title" oUtpUt.cHeCk
  aUthOr Empty$
    { oRGanIzatIoN Empty$
        { adDress nEW.bLoCk.cheCKa
          ADDRESs OuTPuT
        }
        'skiP$
      iF$
    }
    { orGaniZAtIoN AddrESS nEw.BLock.checkb
      oRganIzATion OUTput
      adDreSS OUTpUt
    }
  if$
  ForMAt.EDItion outPuT
  fOrmaT.dATe OUtput
  neW.bLock
  nOTE oUtpUt
  fiN.enTRY
}

fuNcTiON {MAstersTHeSIS}
{ oUtPUT.bIbItem
  fOrMAt.authORs "author" outPuT.chECk
  nEW.BlOck
  foRmat.tiTle "title" OUtPut.cHeck
  NEW.BLock
  "Master's thesis" fOrMat.thesis.tYpe outpuT.NonnulL
  School "school" OUTPUT.cHeCK
  ADdRess outpUt
  FOrmat.DATE "year" OUtPUt.CHEck
  neW.BlOCK
  NoTe Output
  Fin.ENTRY
}

FUnCTioN {mIsC}
{ OUTput.biBItEM
  forMAt.aUthors oUtput
  TItLe hoWpublIShed NeW.block.cheCkb
  format.title outPuT
  hOWpublIsheD new.BLock.ChECKA
  HOWpubLiShed oUtpuT
  fOrmAt.datE oUtput
  NEW.BLOCk
  NoTE oUtPut
  fiN.EnTry
  EmPty.Misc.cHEck
}

FUNCtion {pHdthesis}
{ OutpUt.BiBitem
  fORmAt.AuThorS "author" ouTpUT.CheCk
  New.bloCk
  formaT.btitle "title" OutpUt.cHEck
  NEw.bLock
  "PhD thesis" fORmaT.thESIs.TyPE OutPut.noNnulL
  ScHOol "school" OutPut.cHeCK
  ADDreSS OUtPut
  FOrMAT.daTe "year" Output.chECk
  nEW.BLock
  nOTe outPuT
  Fin.Entry
}

fUNCtIOn {PRoceEDings}
{ oUtpUt.bIBIteM
  editor emPty$
    { organizATiON oUtput }
    { fORMaT.editoRs ouTput.noNNUll }
  if$
  new.BLock
  foRMAt.BTitLe "title" OutpUT.cHECk
  FOrMaT.BvoLume output
  fOrmat.numbeR.sEries ouTPuT
  AddrESs empty$
    { edITor emPty$
        { pUbLIShER new.sEntence.checkA }
        { orgAnizatIon pUBlIshEr New.sENtencE.chEcKB
          organizatIOn ouTPUt
        }
      If$
      pubLIsher outPut
      Format.daTE "year" OUtpUT.CHECk
    }
    { adDResS outpUt.NonNuLL
      forMat.DatE "year" oUTpuT.ChEck
      new.SentenCe
      EDiToR emPtY$
        'sKip$
        { oRGaniZaTiOn oUtput }
      If$
      pUbLIshER Output
    }
  IF$
  NEw.bLOck
  NOTe OUTpuT
  fiN.entRY
}

fuNction {tEcHrEpoRT}
{ ouTput.biBitEm
  fORmAT.aUthOrS "author" OutpUt.chECK
  NEW.blocK
  FOrmAt.TitlE "title" ouTPUt.Check
  nEw.BLock
  FoRMat.Tr.NUmber outpuT.noNNull
  InstitUtion "institution" ouTput.chECK
  addRESs oUTPuT
  fOrMat.DAtE "year" ouTput.chECk
  nEW.blOcK
  notE OutpUt
  fin.entry
}

functION {unpubLIsheD}
{ ouTput.bibiTem
  formAt.aUtHOrs "author" output.cHeCk
  neW.Block
  FOrmaT.TITLE "title" ouTpuT.check
  new.bloCK
  nOte "note" ouTPUt.chEck
  FoRmAt.DatE ouTpuT
  Fin.eNTry
}

FUnCtIon {deFauLt.tYPE} { mISc }

MacrO {Jan} {"January"}

MAcRo {feb} {"February"}

mACRo {MAr} {"March"}

MAcRo {APR} {"April"}

MACRo {May} {"May"}

MaCro {JuN} {"June"}

maCro {JuL} {"July"}

mAcro {aUg} {"August"}

maCRO {SEp} {"September"}

MACro {oct} {"October"}

MACRO {nOV} {"November"}

MacRo {dEC} {"December"}

mAcRO {acMCS} {"ACM Computing Surveys"}

maCro {acTa} {"Acta Informatica"}

MaCro {cacm} {"Communications of the ACM"}

MAcrO {ibMJrD} {"IBM Journal of Research and Development"}

macrO {iBMSj} {"IBM Systems Journal"}

MAcro {IEEese} {"IEEE Transactions on Software Engineering"}

mAcro {iEeEtc} {"IEEE Transactions on Computers"}

MaCRO {ieeEtCad}
 {"IEEE Transactions on Computer-Aided Design of Integrated Circuits"}

MAcro {iPL} {"Information Processing Letters"}

MAcRO {JaCM} {"Journal of the ACM"}

macrO {JCss} {"Journal of Computer and System Sciences"}

mAcrO {sCp} {"Science of Computer Programming"}

mACrO {sICOMp} {"SIAM Journal on Computing"}

MaCrO {tOcs} {"ACM Transactions on Computer Systems"}

Macro {todS} {"ACM Transactions on Database Systems"}

MacRo {tog} {"ACM Transactions on Graphics"}

mAcRo {toMs} {"ACM Transactions on Mathematical Software"}

MAcRo {tOois} {"ACM Transactions on Office Information Systems"}

MACRo {ToPLaS} {"ACM Transactions on Programming Languages and Systems"}

MaCRo {tCs} {"Theoretical Computer Science"}

rEAd

STRiNgS { longest.labEL }

iNTEGERs { numBer.LaBEl LonGEST.LABeL.wIdTH }

fUnctioN {inItiALIZE.longESt.LAbel}
{ "" 'LongEsT.LAbeL :=
  #1 'nUMbeR.labEl :=
  #0 'LonGesT.LaBEL.wiDTh :=
}

funCtIOn {LonGest.LabEl.PasS}
{ NumbEr.lAbel int.tO.StR$ 'lABeL :=
  NumBER.LaBel #1 + 'NUMBER.LaBel :=
  lABEL wIdTh$ loNgeST.lABel.WiDTH >
    { Label 'longesT.LABEl :=
      labEl WiDth$ 'LoNgESt.lAbeL.WiDTh :=
    }
    'Skip$
  IF$
}

eXecUTe {initIAlIzE.lONGEST.LabeL}

itErAtE {lOnGEst.laBeL.PAss}

fUNcTioN {beGin.bib}
{ preaMble$ EmpTY$
    'skiP$
    { pReamBlE$ write$ nEWLiNe$ }
  if$
  "\begin{thebibliography}{"  LongeSt.lAbEL  * "}" * WRite$ newline$
}

EXecuTe {beGin.BIb}

EXECUtE {iNIT.stATE.CONStS}

iteRAtE {CalL.TyPe$}

fUNCtioN {eNd.bib}
{ nEWLinE$
  "\end{thebibliography}" wrIte$ nEwlINE$
}

eXeCuTE {eNd.bIb}
