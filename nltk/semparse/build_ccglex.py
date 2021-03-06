# ==========================
# This script builds a CCG lexicon
# from the file output by the
# parse_sents script.
# ==========================

from __future__ import print_function, unicode_literals

import io
import sys
import optparse
import re
import string
from collections import defaultdict


optparser = optparse.OptionParser()
optparser.add_option("-i", "--infile", dest="infile", default="", help="Input file")
optparser.add_option("-o", "--outfile", dest="outfile", default="", help="Output file")
(opts, _) = optparser.parse_args()


def main(infile, outfile):
    primitives = []
    lex = defaultdict(list)

    # Find the supertags in the parse file.
    # Match words to categories.
    fp = io.open(infile, 'rt', encoding='utf-8')
    for line in fp:
        for entry in line.strip().split():
            (word, _, category) = entry.split('|')
            prob = False
            for p in string.punctuation:
                word = word.replace(p, '')
            # NTLK CCG Lexicon only allows alphabetic characters and underscore.
            if re.findall(r'[^a-zA-Z_]+', word):
                continue
            if not word:
                continue

            if re.findall(r'\[.+?\]', category):
                category = re.sub(r'(\[.+?\])', '', category)
            # NLTK CCG form for conj
            if category == 'conj':
                category = 'var\\.,var/.,var'
                if 'conj' not in primitives:
                    primitives.append('conj')
            if category not in lex[word]:
                lex[word].append(category)
            for prim in re.findall(r'S\[.+?\]|[A-Z]+', category):
                if prim not in primitives:
                    primitives.append(prim)
    fp.close()
    # Make sure 'S' is first so it is treated as the goal when parsing.
    primitives.remove('S')
    primitives.insert(0, 'S')

    with io.open(outfile, 'wt', encoding='utf-8') as out:
        out.write(":- ")
        for i, prim in enumerate(primitives):
            out.write(prim)
            if i+1 < len(primitives):
                out.write(', ')
        out.write('\n')
        out.write("NP :: N\n")

        for (word, cats) in sorted(lex.items(), key=lambda e: e[0]):
            for cat in cats:
                out.write("{0} => {1}\n".format(word, cat))

if __name__ == '__main__':
    if not opts.infile or not opts.outfile:
        print("Usage: build_ccg_lex [-i <path/to/inputfile>] [-o <path/to/outputfile>]")
        sys.exit(1)
    main(opts.infile, opts.outfile)
