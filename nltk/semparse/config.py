import sys
import os

def find_data_dir():
    data_dir = ""
    dirlist = ['nltk/semparse/data']
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
    if not data_dir:
        print("Data directory not found. Check your python path.")
        return None
    else:
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
    _CandC_MARKEDUP_FILE = None
    _LANGUAGE_FILE = None
