# vim:fileencoding=utf-8

from pybtex.database import Entry, Person
from pybtex.database import BibliographyData

reference_data = BibliographyData(
    entries=[
        ('ruckenstein-diffusion', Entry('article',
            fields={
                'language': 'english',
                'title': 'Predicting the Diffusion Coefficient in Supercritical Fluids',
                'journal': 'Ind. Eng. Chem. Res.',
                'volume': '36',
                'year': '1997',
                'pages': '888-895',
            },
            persons={'author': [Person('Liu, Hongquin'), Person('Ruckenstein, Eli')]},
        )),
        ('test-booklet', Entry('booklet',
            fields={
                'language': 'english',
                'title': 'Just a booklet',
                'year': '2006',
                'month': 'January',
                'address': 'Moscow',
                'howpublished': 'Published by Foo',
            },
            persons={'author': [Person('de Last, Jr., First Middle')]}
        )),
        ('test-inbook', Entry('inbook',
            fields={
                'publisher': 'Some Publisher',
                'language': 'english',
                'title': 'Some Title',
                'series': 'Some series',
                'booktitle': 'Some Good Book',
                'number': '3',
                'edition': 'Second',
                'year': '1933',
                'pages': '44--59',
            },
            persons={'author': [Person('Jackson, Peter')]}
        )),
        ('viktorov-metodoj', Entry('book',
            fields={
                'publisher': 'Л.: <<Химия>>',
                'year': '1977',
                'language': 'russian',
                'title': 'Методы вычисления физико-химических величин и прикладные расчёты',
            },
            persons={'author': [Person('Викторов, Михаил Маркович')]}
        )),
    ],
    preamble=['%%% pybtex example file']
)
