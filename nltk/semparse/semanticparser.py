from __future__ import unicode_literals

import io
import re
import string

from nltk import word_tokenize
from nltk.ccg import lexicon, chart

#from nltk.semparse.predicatelexicon import PredicateLexicon
#from nltk.semparse.composer import SemanticComposer
from predicatelexicon import PredicateLexicon ##
from composer import SemanticComposer ##


class Derivation(object):

    def __init__(self, syntactic, semantic, expression):
        self.syntax = syntactic
        self.semantics = semantic
        self.expression = expression

    def printSyntacticDerivation(self):
        chart.printCCGDerivation(self.syntax)

    def printSemanticDerivation(self):
        if not self.semantics:
            print("None")
            return
        for step in self.semantics:
            print(step)
        print()
        

class SemanticParser(object):
    """
    Relies on a CCG parser and a semantic composition function.
    Here we use nltk.ccg.CCGChartParser and nltk.semparse.SemanticComposer
    """
    def __init__(self, ccglex_file, predlex_file):
        """
        :param ccglex_file: CCG lexicon filename.
        :type ccglex_file: str

        :param predlex_file: Predicate lexicon filename.
        :type predlex_file: str

        :param trace: Set trace level. 0: no trace. 2: max trace.
        :type trace: int
        """
        self.ccg_parser = self._setupCCGParser(ccglex_file)
        self.composer = self._setupSemanticComposer(predlex_file)

    def _setupCCGParser(self, ccglex_file):
        """
        Sets up the CCG parser to use.

        :param ccglex_file: CCG lexicon filename to use.
        :type ccglex_file: str
        :rtype: nltk.ccg.chart.CCGChartParser
        """
        lexfile = io.open(ccglex_file, 'rt', encoding='utf-8').read()
        lex = lexicon.parseLexicon(lexfile)
        parser = chart.CCGChartParser(lex, chart.DefaultRuleSet)
        return parser

    def _setupSemanticComposer(self, predlex_file):
        """
        Sets up the semantic composer.

        :param predlex_file: Predicate lexicon filename to use.
        :type predlex_file: str
        :rtype: nltk.semparse.SemanticComposer
        """
        predLex = PredicateLexicon.fromfile(predlex_file)
        composer = SemanticComposer(predLex)
        return composer

    def _preprocessSent(self, sentence):
        """
        Removes punctuation and tokenizes sentence.

        :param sentence: sentence to process
        :type sentence: str
        :rtype: list
        """
        sentence = word_tokenize(sentence)
        sentence = [tok for tok in sentence if tok not in string.punctuation]
        return sentence

    def parse(self, sentence):
        """
        Parses sentences first into a CCG syntactic parse.
        Then uses this parse to compose a semantics.
        Yields a list of Derivation instances for each syntactic
        parse of the sentence.

        :param sentence: sentence to parse into logical form.
        :type sentence: str
        :rtype: list(Derivation)
        """
        sentence = self._preprocessSent(sentence)
        ccg_parses = self.ccg_parser.parse(sentence)

        for parse in ccg_parses:
            try:
                expressions = self.composer.buildExpressions(parse)
            # Yield just syntactic parse if semantics fail.
            except:
                yield Derivation(parse, None, None)
                continue
            if not expressions:
                yield Derivation(parse, None, None)
                continue
            for (expression, derivation) in expressions:
                yield Derivation(parse, derivation, expression)


def demo():
    # Statement data.
    semParser = SemanticParser('data/reagan/ccg.lex', 'data/reagan/predicates.lex')
    sent = "Reagan had four children."
    print('\n', sent)
    derivation = semParser.parse(sent).next()
    print("+", derivation.expression)

    # Question data.
    semParser = SemanticParser('data/geoquery/ccg.lex', 'data/geoquery/predicates.lex')
    sent = "What is the longest river?"
    print('\n', sent)
    derivation = semParser.parse(sent).next()
    print("+", derivation.expression)


if __name__ == '__main__':
    demo()
