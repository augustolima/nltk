from __future__ import print_function, unicode_literals

import io
import re
import string

from nltk import word_tokenize
from nltk.ccg import lexicon, chart
from nltk.sem.logic import LogicalExpressionException

#from nltk.semparse.composer import SemanticComposer
from composer import SemanticComposer ##


class Derivation(object):

    def __init__(self, syntax, semantics):
        self.syntax = syntax
        self.semantics = semantics

    def printSyntacticDerivation(self):
        chart.printCCGDerivation(self.syntax)

    def printSemanticDerivation(self):
        if not self.semantics:
            print("None")
            return
        def derivation_print(tree):
            children = list(tree.subtrees())
            if len(children) == 1:
                return tree.label()
            rule = tree.label()[1]
            lhs = derivation_print(children[1])
            rhs = derivation_print(children[2])
            print("{0} {1} {2}\n\t==> {3}"
                   .format(lhs[0], rule, rhs[0], tree.label()[0]))
            return tree.label()

        derivation_print(self.semantics)

    def getExpression(self):
        if self.semantics:
            return self.semantics.label()[0]
        else:
            return None


class SemanticParser(object):
    """
    Relies on a CCG parser and a semantic composition function.
    Here use nltk.ccg.CCGChartParser and nltk.semparse.SemanticComposer
    """
    def __init__(self, ccglex_file):
        """
        :param ccglex_file: CCG lexicon filename.
        :type ccglex_file: str
        """
        self.ccg_parser = self._setupCCGParser(ccglex_file)
        self.composer = SemanticComposer()

    def _setupCCGParser(self, ccglex_file):
        """
        Sets up the CCG parser.

        :param ccglex_file: CCG lexicon filename to use.
        :type ccglex_file: str
        :rtype: nltk.ccg.chart.CCGChartParser
        """
        lexfile = io.open(ccglex_file, 'rt', encoding='utf-8').read()
        lex = lexicon.parseLexicon(lexfile)
        parser = chart.CCGChartParser(lex, chart.DefaultRuleSet)
        return parser

    def _getTokens(self, tagged_sentence):
        """
        Gets the words of the sentence and removes punctuation.
        
        :param tagged_sentence: POS tagged input sentence.
        :type tagged_sentence: list(tuple(str, str))
        :rtype: list
        """
        tokens = [tagtok[0] for tagtok in tagged_sentence]
        tokens = [tok for tok in tokens if tok not in string.punctuation]
        return tokens

    def parse(self, tagged_sentence, n=100):
        """
        Parses sentences first into a CCG syntactic parse.
        Then uses this parse to compose a semantics.
        Yields a list of Derivation instances for each syntactic
        parse of the sentence.

        :param sentence: sentence to parse into logical form.
        :type sentence: str
        :rtype: list(Derivation)
        """
        if tagged_sentence[-1][0] == '?':
            question = True
        else:
            question = False

        tokens = self._getTokens(tagged_sentence)
        ccg_parses = self.ccg_parser.parse(tokens)

        for (i,parse) in enumerate(ccg_parses):
            if i > n:
                break
            try:
                derivation = self.composer.buildExpressions(parse, tagged_sentence, question)
                yield Derivation(parse, derivation)
            # Yield just syntactic parse if semantics fail.
            except LogicalExpressionException:
                yield Derivation(parse, None)
                continue
            else:
                yield Derivation(parse, None)
                continue


def demo():
    from nltk import word_tokenize, pos_tag

    # Statement data.
    semParser = SemanticParser('data/lexica/reagan.ccg')
    sent = "Reagan had four children."
    print('\n', sent)
    tagged_sent = pos_tag(word_tokenize(sent))
    derivation = semParser.parse(tagged_sent).next()
    print("+", derivation.expression)

    # Question data.
    semParser = SemanticParser('data/lexica/geoquery.ccg')
    sent = "What is the longest river?"
    print('\n', sent)
    tagged_sent = pos_tag(word_tokenize(sent))
    derivation = semParser.parse(tagged_sent).next()
    print("+", derivation.expression)


if __name__ == '__main__':
    demo()
