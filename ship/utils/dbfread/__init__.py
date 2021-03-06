"""
Read DBF files with Python.

Example:

    >>> from dbfread import DBF
    >>> for record in DBF('people.dbf'):
    ...     print(record)
    OrderedDict([('NAME', 'Alice'), ('BIRTHDATE', datetime.date(1987, 3, 1))])
    OrderedDict([('NAME', 'Bob'), ('BIRTHDATE', datetime.date(1980, 11, 12))])

Full documentation at http://dbfread.readthedocs.org/

"""
__author__ = 'Ole Martin Bjorndalen'
__email__ = 'ombdalen@gmail.com'
__url__ = 'http://nerdly.info/ole/'
__license__ = 'MIT'
__version__ = '2.0.5'

from .dbf import DBF
from .deprecated_dbf import open, read
from .exceptions import *
from .field_parser import FieldParser, InvalidValue

# Prevent splat import.
__all__ = []
