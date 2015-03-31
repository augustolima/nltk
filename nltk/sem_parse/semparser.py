# Natural Language Toolkit: Semantic Parser
#
# Copyright (C) 2001-2015 NLTK Project
# Author: Jake Vasilakes <s1420849@sms.ed.ac.uk>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

'''
Semantic parser which builds MRs using nltk.ccg

Data:
Relies on nltk:grammars/ccg_grammars/lex.ccg
Get it from <homepages.inf.ed.ac.uk/s1420849/lex.ccg>
and put it in, e.g. $HOME/nltk_data/grammars/ccg_grammars/lex.ccg
'''
from __future__ import print_function, division, unicode_literals

from nltk.data import load
from nltk.ccg import lexicon, chart


class SemParser(object):
    """
    A semantic parser that builds first-order logic meaning
    representations (MRs) using the lambda-calculus from
    CCG parses.

    Current status:
        Syntactically parse a NL sentence using the nltk.ccg 
        module and a custom lexicon, lex.ccg.

    Usage example:
        from nltk.sem_parse import semparser
        from nltk.ccg import chart
        SP = semparser.SemParser("grammars/ccg_grammars/lex.ccg")
        parses = SP.parse("I went home")
        chart.printCCGDerivation(parses.next())
    """

    def __init__(self, lex=None):
        """
        :param lex: str nltk path to ccg lexicon file
        """
        if lex:
            self._parser = self.buildParser(lex)

    def buildParser(self, lex):
        """
        Create a CCG parser from the provided lexicon.

        :param lex: str nltk path to ccg lexicon file
        """
        rules = load(lex, 'text')
        lex = lexicon.parseLexicon(str(rules))
        parser = chart.CCGChartParser(lex, chart.DefaultRuleSet)
        return parser

    def parse(self, sentence):
        """
        Parse the sentence.

        :param sentence: str for the input to be parsed
        """
        p = self._parser.parse(sentence.split())
        return p


def demo():
    print("Building parser...")
    semparser = SemParser("grammars/ccg_grammars/lex.ccg")
    sentence = "I went home"
    print("\nParsing '{0}'...\n" .format(sentence))
    parses = semparser.parse(sentence)
    chart.printCCGDerivation(parses.next())


if __name__ == '__main__':
    demo()
