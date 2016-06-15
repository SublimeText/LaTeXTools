from __future__ import print_function

import sublime
import sublime_plugin

try:
    from latextools_utils import is_bib_buffer, is_biblatex_buffer
except ImportError:
    from .latextools_utils import is_bib_buffer, is_biblatex_buffer

bibtex_fields = [
    ('address', 'address = {${1:Address}},'),
    ('annote', 'annote = {${1:Annote}},'),
    ('author', 'author = {${1:Author}},'),
    ('booktitle', 'booktitle = {${1:Booktitle}},'),
    ('chapter', 'chapter = {${1:Chapter}},'),
    ('crossref', 'crossref = {${1:Crossref}},'),
    ('edition', 'edition = {${1:Edition}},'),
    ('editor', 'editor = {${1:Editor}},'),
    ('howpublished', 'howpublished = {${1:Howpublished}},'),
    ('instituion', 'instituion = {${1:Instituion}},'),
    ('journal', 'journal = {${1:Journal}},'),
    ('key', 'key = {${1:Key}},'),
    ('month', 'month = {${1:Month}},'),
    ('note', 'note = {${1:Note}},'),
    ('number', 'number = {${1:Number}},'),
    ('organization', 'organization = {${1:Organization}},'),
    ('pages', 'pages = {${1:Pages}},'),
    ('publisher', 'publisher = {${1:Publisher}},'),
    ('school', 'school = {${1:School}},'),
    ('series', 'series = {${1:Series}},'),
    ('title', 'title = {${1:Title}},'),
    ('type', 'type = {${1:Type}},'),
    ('volume', 'volume = {${1:Volume}},'),
    ('year', 'year = {${1:Year}},')
]

biblatex_fields = [
    ('abstract', 'abstract = {${1:Abstract}},'),
    ('addendum', 'addendum = {${1:Addendum}},'),
    ('address', 'address = {${1:Address}},'),
    ('afterword', 'afterword = {${1:Afterword}},'),
    ('annotation', 'annotation = {${1:Annotation}},'),
    ('annotator', 'annotator = {${1:Annotator}},'),
    ('annote', 'annote = {${1:Annote}},'),
    ('archiveprefix', 'archiveprefix = {${1:Archiveprefix}},'),
    ('author', 'author = {${1:Author}},'),
    ('authortype', 'authortype = {${1:Authortype}},'),
    ('bookauthor', 'bookauthor = {${1:Bookauthor}},'),
    ('bookpagination', 'bookpagination = {${1:Bookpagination}},'),
    ('booksubtitle', 'booksubtitle = {${1:Booksubtitle}},'),
    ('booktitle', 'booktitle = {${1:Booktitle}},'),
    ('booktitleaddon', 'booktitleaddon = {${1:Booktitleaddon}},'),
    ('chapter', 'chapter = {${1:Chapter}},'),
    ('commentator', 'commentator = {${1:Commentator}},'),
    ('crossref', 'crossref = {${1:Crossref}},'),
    ('date', 'date = {${1:Date}},'),
    ('doi', 'doi = {${1:Doi}},'),
    ('edition', 'edition = {${1:Edition}},'),
    ('editor', 'editor = {${1:Editor}},'),
    ('editora', 'editora = {${1:Editora}},'),
    ('editoratype', 'editoratype = {${1:Editoratype}},'),
    ('editorb', 'editorb = {${1:Editorb}},'),
    ('editorbtype', 'editorbtype = {${1:Editorbtype}},'),
    ('editorc', 'editorc = {${1:Editorc}},'),
    ('editorctype', 'editorctype = {${1:Editorctype}},'),
    ('editortype', 'editortype = {${1:Editortype}},'),
    ('eid', 'eid = {${1:Eid}},'),
    ('entryset', 'entryset = {${1:Entryset}},'),
    ('entrysubtype', 'entrysubtype = {${1:Entrysubtype}},'),
    ('eprint', 'eprint = {${1:Eprint}},'),
    ('eprintclass', 'eprintclass = {${1:Eprintclass}},'),
    ('eprinttype', 'eprinttype = {${1:Eprinttype}},'),
    ('eventdate', 'eventdate = {${1:Eventdate}},'),
    ('eventtitle', 'eventtitle = {${1:Eventtitle}},'),
    ('eventtitleaddon', 'eventtitleaddon = {${1:Eventtitleaddon}},'),
    ('execute', 'execute = {${1:Execute}},'),
    ('file', 'file = {${1:File}},'),
    ('foreward', 'foreward = {${1:Foreward}},'),
    ('gender', 'gender = {${1:Gender}},'),
    ('holder', 'holder = {${1:Holder}},'),
    ('howpublished', 'howpublished = {${1:Howpublished}},'),
    ('ids', 'ids = {${1:Ids}},'),
    ('indexsorttitle', 'indexsorttitle = {${1:Indexsorttitle}},'),
    ('indextitle', 'indextitle = {${1:Indextitle}},'),
    ('instituion', 'instituion = {${1:Instituion}},'),
    ('introduction', 'introduction = {${1:Introduction}},'),
    ('isan', 'isan = {${1:Isan}},'),
    ('isbn', 'isbn = {${1:Isbn}},'),
    ('ismn', 'ismn = {${1:Ismn}},'),
    ('isrn', 'isrn = {${1:Isrn}},'),
    ('issn', 'issn = {${1:Issn}},'),
    ('issue', 'issue = {${1:Issue}},'),
    ('issuesubtitle', 'issuesubtitle = {${1:Issuesubtitle}},'),
    ('issuetitle', 'issuetitle = {${1:Issuetitle}},'),
    ('iswc', 'iswc = {${1:Iswc}},'),
    ('journal', 'journal = {${1:Journal}},'),
    ('journalsubtitle', 'journalsubtitle = {${1:Journalsubtitle}},'),
    ('journaltitle', 'journaltitle = {${1:Journaltitle}},'),
    ('key', 'key = {${1:Key}},'),
    ('keywords', 'keywords = {${1:Keywords}},'),
    ('label', 'label = {${1:Label}},'),
    ('langid', 'langid = {${1:Langid}},'),
    ('langidopts', 'langidopts = {${1:Langidopts}},'),
    ('language', 'language = {${1:Language}},'),
    ('library', 'library = {${1:Library}},'),
    ('lista', 'lista = {${1:Lista}},'),
    ('listb', 'listb = {${1:Listb}},'),
    ('listc', 'listc = {${1:Listc}},'),
    ('listd', 'listd = {${1:Listd}},'),
    ('liste', 'liste = {${1:Liste}},'),
    ('listf', 'listf = {${1:Listf}},'),
    ('location', 'location = {${1:Location}},'),
    ('mainsubtitle', 'mainsubtitle = {${1:Mainsubtitle}},'),
    ('maintitle', 'maintitle = {${1:Maintitle}},'),
    ('maintitleaddon', 'maintitleaddon = {${1:Maintitleaddon}},'),
    ('month', 'month = {${1:Month}},'),
    ('namea', 'namea = {${1:Namea}},'),
    ('nameaddon', 'nameaddon = {${1:Nameaddon}},'),
    ('nameatype', 'nameatype = {${1:Nameatype}},'),
    ('nameb', 'nameb = {${1:Nameb}},'),
    ('namebtype', 'namebtype = {${1:Namebtype}},'),
    ('namec', 'namec = {${1:Namec}},'),
    ('namectype', 'namectype = {${1:Namectype}},'),
    ('note', 'note = {${1:Note}},'),
    ('number', 'number = {${1:Number}},'),
    ('options', 'options = {${1:Options}},'),
    ('organization', 'organization = {${1:Organization}},'),
    ('origdate', 'origdate = {${1:Origdate}},'),
    ('origlanguage', 'origlanguage = {${1:Origlanguage}},'),
    ('origlocation', 'origlocation = {${1:Origlocation}},'),
    ('origpublisher', 'origpublisher = {${1:Origpublisher}},'),
    ('origtitle', 'origtitle = {${1:Origtitle}},'),
    ('pages', 'pages = {${1:Pages}},'),
    ('pagetotal', 'pagetotal = {${1:Pagetotal}},'),
    ('pagination', 'pagination = {${1:Pagination}},'),
    ('part', 'part = {${1:Part}},'),
    ('pdf', 'pdf = {${1:Pdf}},'),
    ('presort', 'presort = {${1:Presort}},'),
    ('primaryclass', 'primaryclass = {${1:Primaryclass}},'),
    ('publisher', 'publisher = {${1:Publisher}},'),
    ('pubstate', 'pubstate = {${1:Pubstate}},'),
    ('related', 'related = {${1:Related}},'),
    ('relatedoptions', 'relatedoptions = {${1:Relatedoptions}},'),
    ('relatedstring', 'relatedstring = {${1:Relatedstring}},'),
    ('relatedtype', 'relatedtype = {${1:Relatedtype}},'),
    ('reprinttitle', 'reprinttitle = {${1:Reprinttitle}},'),
    ('school', 'school = {${1:School}},'),
    ('series', 'series = {${1:Series}},'),
    ('shortauthor', 'shortauthor = {${1:Shortauthor}},'),
    ('shorteditor', 'shorteditor = {${1:Shorteditor}},'),
    ('shorthand', 'shorthand = {${1:Shorthand}},'),
    ('shorthandintro', 'shorthandintro = {${1:Shorthandintro}},'),
    ('shortjournal', 'shortjournal = {${1:Shortjournal}},'),
    ('shortseries', 'shortseries = {${1:Shortseries}},'),
    ('shorttitle', 'shorttitle = {${1:Shorttitle}},'),
    ('sortkey', 'sortkey = {${1:Sortkey}},'),
    ('sortname', 'sortname = {${1:Sortname}},'),
    ('sortshorthand', 'sortshorthand = {${1:Sortshorthand}},'),
    ('sorttitle', 'sorttitle = {${1:Sorttitle}},'),
    ('sortyear', 'sortyear = {${1:Sortyear}},'),
    ('subtitle', 'subtitle = {${1:Subtitle}},'),
    ('title', 'title = {${1:Title}},'),
    ('titleaddon', 'titleaddon = {${1:Titleaddon}},'),
    ('translator', 'translator = {${1:Translator}},'),
    ('type', 'type = {${1:Type}},'),
    ('url', 'url = {${1:Url}},'),
    ('urldate', 'urldate = {${1:Urldate}},'),
    ('usera', 'usera = {${1:Usera}},'),
    ('userb', 'userb = {${1:Userb}},'),
    ('userc', 'userc = {${1:Userc}},'),
    ('userd', 'userd = {${1:Userd}},'),
    ('usere', 'usere = {${1:Usere}},'),
    ('userf', 'userf = {${1:Userf}},'),
    ('venue', 'venue = {${1:Venue}},'),
    ('verba', 'verba = {${1:Verba}},'),
    ('verbb', 'verbb = {${1:Verbb}},'),
    ('verbc', 'verbc = {${1:Verbc}},'),
    ('version', 'version = {${1:Version}},'),
    ('volume', 'volume = {${1:Volume}},'),
    ('volumes', 'volumes = {${1:Volumes}},'),
    ('xdata', 'xdata = {${1:Xdata}},'),
    ('xref', 'xref = {${1:Xref}},'),
    ('year', 'year = {${1:Year}},')
]

class FieldNameCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if not is_bib_buffer(view):
            return []

        cursor_point = view.sel()[0].b

        # do not autocomplete if the cursor is outside an entry
        if view.score_selector(cursor_point, 'meta.entry.braces.bibtex') == 0:
            return []

        # do not autocomplete when cursor is in the citekey field
        if view.score_selector(cursor_point, 'entity.name.type.entry-key.bibtex') > 0:
            return []

        # do not autocomplete if we are already inside a field
        if view.score_selector(cursor_point, 'meta.key-assignment.bibtex') > 0:
            return []

        if is_biblatex_buffer(view):
            return (biblatex_fields, sublime.INHIBIT_WORD_COMPLETIONS)

        else:
            return (bibtex_fields, sublime.INHIBIT_WORD_COMPLETIONS)