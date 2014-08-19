import os
import pkgutil
import posixpath
from contextlib import contextmanager
from shutil import rmtree
from tempfile import mkdtemp

from pybtex import io
from pybtex import errors
from pybtex.tests import diff


@contextmanager
def cd_tempdir():
    current_workdir = os.getcwd()
    tempdir = mkdtemp(prefix='pybtex_test_')
    os.chdir(tempdir)
    try:
        yield tempdir
    finally:
        os.chdir(current_workdir)
        rmtree(tempdir)


def copy_resource(package, resource):
    filename = posixpath.basename(resource)
    data = pkgutil.get_data(package, resource).decode(io.get_default_encoding())
    with io.open_unicode(filename, 'w') as data_file:
        data_file.write(data)


def copy_files(filenames):
    for filename in filenames:
        copy_resource('pybtex.tests.data', filename)


def write_aux(aux_name, bib_name, bst_name):
    with io.open_unicode(aux_name, 'w') as aux_file:
        aux_file.write('\\citation{*}\n')
        aux_file.write('\\bibstyle{{{0}}}\n'.format(bst_name))
        aux_file.write('\\bibdata{{{0}}}\n'.format(bib_name))


def check_make_bibliography(engine, filenames):
    allowed_exts = {'.bst', '.bib', '.aux'}
    filenames_by_ext = dict(
        (posixpath.splitext(filename)[1], filename) for filename in filenames
    )
    engine_name = engine.__name__.rsplit('.', 1)[-1]

    for ext in filenames_by_ext:
        if ext not in allowed_exts:
            raise ValueError(ext)

    with cd_tempdir() as tempdir:
        copy_files(filenames)
        bib_name = posixpath.splitext(filenames_by_ext['.bib'])[0]
        bst_name = posixpath.splitext(filenames_by_ext['.bst'])[0]
        if not '.aux' in filenames_by_ext:
            write_aux('test.aux', bib_name, bst_name)
            filenames_by_ext['.aux'] = 'test.aux'
        with errors.capture() as captured_errors:  # FIXME check error messages
            engine.make_bibliography(filenames_by_ext['.aux'])
        result_name = posixpath.splitext(filenames_by_ext['.aux'])[0] + '.bbl'
        with io.open_unicode(result_name) as result_file:
            result = result_file.read()
        correct_result_name = '{0}_{1}.{2}.bbl'.format(bib_name, bst_name, engine_name)
        correct_result = pkgutil.get_data('pybtex.tests.data', correct_result_name).decode(io.get_default_encoding())
        assert result == correct_result, diff(correct_result, result)


def test_bibtex_engine():
    from pybtex import bibtex
    for filenames in [
        ('xampl.bib', 'unsrt.bst'),
        ('xampl.bib', 'plain.bst'),
        ('xampl.bib', 'alpha.bst'),
        ('cyrillic.bib', 'unsrt.bst'),
        ('cyrillic.bib', 'alpha.bst'),
        ('xampl_mixed.bib', 'unsrt_mixed.bst', 'xampl_mixed_unsrt_mixed.aux'),
        ('IEEEtran.bib', 'IEEEtran.bst', 'IEEEtran.aux'),
    ]:
        yield check_make_bibliography, bibtex, filenames


def test_pybte_engine():
    import pybtex
    for filenames in [
        ('cyrillic.bib', 'unsrt.bst'),
        ('cyrillic.bib', 'plain.bst'),
        ('cyrillic.bib', 'alpha.bst'),
    ]:
        yield check_make_bibliography, pybtex, filenames
