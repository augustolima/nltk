# Natural Language Toolkit: Semantic Parser
#
# Copyright (C) 2001-2015 NLTK Project
# Author: Jake Vasilakes <s1420849@sms.ed.ac.uk>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

# TODO: make all code Python 3 compatible.

'''
Semantic parser which builds Neo-Davidsonian MRs using nltk.ccg
'''

from nltk.semparse.semanticparser import SemanticParser
from nltk.semparse.semanticparser import Derivation
from nltk.semparse.composer import SemanticComposer
from nltk.semparse.syntacticcategory import SyntacticCategory
from nltk.semparse.semanticcategory import SemanticCategory
from nltk.semparse.config import (_DATA_DIR, _CandC_MARKEDUP_FILE, _LANGUAGE_FILE)
