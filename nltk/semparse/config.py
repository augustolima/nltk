from __future__ import print_function

import sys
import os

"""
Defines parse_markedup_file(), _CandC_MARKEDUP_FILE, _DATA_DIR, _LANGUAGE_FILE
"""


def parse_markedup_file(replacements=[]):
    """
    Parses the C&C markedup file into a dictionary of the form
    {syntactic_category: indexed_syntactic_category}. E.g.
    {'S\\NP': '(S{_}\\NP{Y}<1>){_}'}
    :rtype: dict
    """
    filestr = open(_CandC_MARKEDUP_FILE, 'r').read()
    marks = filestr.split('\n\n')
    marks = [line.strip() for line in marks
             if not line.startswith('#') and not line.startswith('=')]
    pairs = [line.split('\n')[:2] for line in marks]
    pairs = [(syncat.strip(), idxsyncat.strip())
             for (syncat, idxsyncat) in pairs]
    pairs = [(syncat, idxsyncat.split()[1])
             for (syncat, idxsyncat) in pairs]
    # This changes, e.g. 'NP' to 'N' if 'NP :: N' is in the ccg lexicon.
    if replacements:
        temppairs = []
        for (oldsyn, newsyn) in replacements:
            for syncat, _ in pairs:
                temppairs.append((syncat.replace(oldsyn, newsyn), _))
        pairs = temppairs
    pairsdict = dict(pairs)
    return pairsdict

def find_data_dir():
    dirlist = ['nltk/semparse/data', 'data']
    pypath = sys.path
    found = False
    for folder in pypath:
        if found:
            break
        for base in dirlist:
            d = os.path.join(folder, base)
            if os.path.exists(d) and os.path.isdir(d):
                data_dir = d
                found = True
                break
    return data_dir

_DATA_DIR = find_data_dir()
if _DATA_DIR:
    _CandC_MARKEDUP_FILE = os.path.join(_DATA_DIR, 'lib/markedup')
    _LANGUAGE_FILE = os.path.join(_DATA_DIR, 'lib/english.txt')
    if not os.path.isfile(_CandC_MARKEDUP_FILE):
        raise IOError("C&C markedup file not found: '{0}'"
                       .format(_CandC_MARKEDUP_FILE))
    if not os.path.isfile(_LANGUAGE_FILE):
        raise IOError("Language file not found: '{0}'"
                       .format(_LANGUAGE_FILE))
else:
    print("Data directory not found. Check your python path.")
    _CandC_MARKEDUP_FILE = None
    _LANGUAGE_FILE = None
