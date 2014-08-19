# Copyright (c) 2007, 2008, 2009, 2010, 2011, 2012  Andrey Golovizin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Based on a similar script from Pygments.

"""Generate HTML documentation
"""

import os
import sys
import re
import shutil
from datetime import datetime
from cgi import escape
from glob import glob

from docutils import nodes
from docutils.parsers.rst import directives, Directive
from docutils.core import publish_parts
from docutils.writers import html4css1

from jinja2 import Environment, PackageLoader

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

from pybtex.__version__ import version
from .mystyle import MyHiglightStyle

e = Environment(loader=PackageLoader('pybtex', 'docgen'))

PYGMENTS_FORMATTER = HtmlFormatter(style=MyHiglightStyle, cssclass='sourcecode')

#CHANGELOG = file(os.path.join(os.path.dirname(__file__), os.pardir, 'CHANGES'))\
#            .read().decode('utf-8')

DATE_FORMAT = '%d %B %y (%a)'


def get_bzr_modification_date(filename):
    from bzrlib.osutils import format_date

    mtime, timezone = get_bzr_timestamp(filename)
    return format_date(mtime, timezone, 'utc', date_fmt=DATE_FORMAT, show_offset=False)


def get_bzr_timestamp(filename):
    from bzrlib import workingtree

    if os.path.basename(filename) == 'history.rst':
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(filename)))
        filename = os.path.join(root_dir, 'CHANGES')
    tree = workingtree.WorkingTree.open_containing(filename)[0]
    tree.lock_read()
    rel_path = tree.relpath(os.path.abspath(filename))
    file_id = tree.inventory.path2id(rel_path)
    last_revision = get_last_bzr_revision(tree.branch, file_id)
    tree.unlock()
    return last_revision.timestamp, last_revision.timezone
    

def get_last_bzr_revision(branch, file_id):
    history = branch.repository.iter_reverse_revision_history(branch.last_revision())
    last_revision_id = branch.last_revision()
    current_inventory = branch.repository.get_inventory(last_revision_id)
    current_sha1 = current_inventory[file_id].text_sha1
    for revision_id in history:
        inv = branch.repository.get_inventory(revision_id)
        if not file_id in inv or inv[file_id].text_sha1 != current_sha1:
            return branch.repository.get_revision(last_revision_id)
        last_revision_id = revision_id


def pygments_directive(name, arguments, options, content, lineno,
                      content_offset, block_text, state, state_machine):
    try:
        lexer = get_lexer_by_name(arguments[0])
    except ValueError:
        # no lexer found
        lexer = get_lexer_by_name('text')
    parsed = highlight('\n'.join(content), lexer, PYGMENTS_FORMATTER)
    return [nodes.raw('', parsed, format="html")]
pygments_directive.arguments = (1, 0, 1)
pygments_directive.content = 1


class DownloadLinks(Directive):
    has_content = False

    def run(self):
        tarball_uri = 'http://pypi.python.org/packages/source/p/pybtex/pybtex-%s.tar.bz2' % version

        current_version_is = nodes.Text('Current version is ')
        pybtex_xx = nodes.reference('', 'Pybtex %s' % version,
            name='Pybtex %s' % version,
            refuri=tarball_uri)
        download = nodes.reference('', 'download', name='download',
            refname='download')
        see_whats_new = nodes.reference('', "see what's new",
            name="see what's new", refuri='history.txt')
        content = (
            current_version_is,
            pybtex_xx,
            nodes.Text(' ('),
            download, nodes.Text(', '),
            see_whats_new,
            nodes.Text(')')
        )
        paragraph = nodes.paragraph('', '', *content)
        link_block = nodes.block_quote('', paragraph, classes=["pull-quote"])
        return [link_block]

class NoopDirective(Directive):
    has_content = False
    def run(self):
        return []


def register_directives(for_site=False):
    directives.register_directive('sourcecode', pygments_directive)
    directives.register_directive('download-links', DownloadLinks if for_site else NoopDirective)


def mark_tail(phrase, keyword, pattern = '%s<span class="tail"> %s</span>'):
    """Finds and highlights a 'tail' in the sentense.

    A tail consists of several lowercase words and a keyword.

    >>> print(mark_tail('The Manual of Pybtex', 'Pybtex'))
    The Manual<span class="tail"> of Pybtex</span>

    Look at the generated documentation for further explanation.
    """

    words = phrase.split()
    if words[-1] == keyword:
        pos = -[not word.islower() for word in reversed(words[:-1])].index(True) - 1
        return pattern % (' '.join(words[:pos]), ' '.join(words[pos:]))
    else:
        return phrase

e.filters['mark_tail'] = mark_tail

def create_translator(link_style):
    class Translator(html4css1.HTMLTranslator):
        def visit_reference(self, node):
            refuri = node.get('refuri')
            if refuri is not None and '/' not in refuri and refuri.endswith('.txt'):
                node['refuri'] = link_style(refuri[:-4])
            html4css1.HTMLTranslator.visit_reference(self, node)
    return Translator


class DocumentationWriter(html4css1.Writer):

    def __init__(self, link_style):
        html4css1.Writer.__init__(self)
        self.translator_class = create_translator(link_style)

    def translate(self):
        html4css1.Writer.translate(self)
        # generate table of contents
        contents = self.build_contents(self.document)
        contents_doc = self.document.copy()
        contents_doc.children = contents
        contents_visitor = self.translator_class(contents_doc)
        contents_doc.walkabout(contents_visitor)
        self.parts['toc'] = self._generated_toc

    def build_contents(self, node, level=0):
        sections = []
        i = len(node) - 1
        while i >= 0 and isinstance(node[i], nodes.section):
            sections.append(node[i])
            i -= 1
        sections.reverse()
        toc = []
        for section in sections:
            try:
                reference = nodes.reference('', '', refid=section['ids'][0], *section[0])
            except IndexError:
                continue
            ref_id = reference['refid']
            text = escape(reference.astext().encode('utf-8'))
            toc.append((ref_id, text))

        self._generated_toc = [('#%s' % href, caption) for href, caption in toc]
        # no further processing
        return []


def generate_documentation(data, link_style):
    writer = DocumentationWriter(link_style)
    parts = publish_parts(
        data,
        writer=writer,
        settings_overrides={
            'initial_header_level': 2,
            'field_name_limit': 50,
        }
    )
    return {
        'title':        parts['title'],
        'body':         parts['body'],
        'toc':          parts['toc'],
    }


def handle_file(filename, fp, dst, for_site):
    title = os.path.splitext(os.path.basename(filename))[0]
    content = fp.read()

    cwd = os.getcwd()
    os.chdir(os.path.dirname(filename))
    parts = generate_documentation(content, (lambda x: './%s.html' % x))
    os.chdir(cwd)

    c = dict(parts)
    if for_site:
        c['modification_date'] = get_bzr_modification_date(filename) 
    c['file_id'] = title
    c['for_site'] = for_site
    tmpl = e.get_template('template.html')
    result = file(os.path.join(dst, title + '.html'), 'w')
    result.write(tmpl.render(c).encode('utf-8'))
    result.close()


def run(src_dir, dst_dir, for_site, sources=(), handle_file=handle_file):
    if not sources:
        sources = glob(os.path.join(src_dir, '*.rst'))
    
    try:
        shutil.rmtree(dst_dir)
    except OSError:
        pass
    os.mkdir(dst_dir)
    for filename in glob(os.path.join(src_dir, '*.css')):
        shutil.copy(filename, dst_dir)

    pygments_css = PYGMENTS_FORMATTER.get_style_defs('.sourcecode')
    file(os.path.join(dst_dir, 'pygments.css'), 'w').write(pygments_css)

    for fn in sources:
        if not os.path.isfile(fn):
            continue
        print('Processing %s' % fn)
        f = open(fn)
        try:
            handle_file(fn, f, dst_dir, for_site)
        finally:
            f.close()


def generate_html(doc_dir, for_site=False, *sources):
    register_directives(for_site)
    src_dir = os.path.realpath(os.path.join(doc_dir, 'rst'))
    dst_dir = os.path.realpath(os.path.join(doc_dir, 'site' if for_site else 'html'))
    run(src_dir, dst_dir, for_site, sources)


def generate_site(doc_dir):
    generate_html(doc_dir, for_site=True)
    os.system('rsync -rv --delete --exclude hg/ %s ero-sennin,pybtex@web.sourceforge.net:/home/groups/p/py/pybtex/htdocs'
            % os.path.join(doc_dir, 'site/'))

