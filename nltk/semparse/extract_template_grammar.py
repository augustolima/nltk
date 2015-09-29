from __future__ import print_function, unicode_literals

import sys
import string
from collections import OrderedDict


if len(sys.argv) == 2:
    grammarfile = sys.argv[1]
else:
    print("Wrong number of arguments!")
    sys.exit(1)

rules = open(grammarfile, 'r')
template_rules = []

for rule in rules:
    var_store = ['X', 'Y', 'Z']
    categories = rule.strip().split(' | ')
    unique_cats = list(OrderedDict.fromkeys(categories))
    varmap = []
    for cat in unique_cats:
        if cat in string.punctuation:
            varmap.append((cat, 'PUNCT'))
        else:
            varmap.append((cat, var_store.pop(0)))
    varmap = OrderedDict(varmap)
    template = [varmap[cat] for cat in categories]
    if template not in template_rules:
        template_rules.append(template)

with open('data/grammars/template_grammar.txt', 'w') as out:
    for (left, right, result) in template_rules:
        out.write('{0} + {1} => {2}\n'.format(left, right, result))
