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

    def __init__(self, syntax, semantics, sentence_type):
        self.syntax = syntax
        self.semantics = semantics
        self.sentence_type = sentence_type

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
    def __init__(self, ccg_lexicon):
        """
        :param ccglex_file: CCG lexicon filename.
        :type ccglex_file: str
        """
        self.ccg_parser = chart.CCGChartParser(ccg_lexicon, chart.DefaultRuleSet)
        self.composer = SemanticComposer()

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

    def parse(self, tagged_sentence, n=0):
        """
        Parses sentences first into a CCG syntactic parse.
        Then uses this parse to compose a semantics.
        Yields a list of Derivation instances for each syntactic
        parse of the sentence.

        :param tagged_sentence: tokenized and POS tagged sentence.
        :type tagged_sentence: list(tuple(str, str))
        :returns: yields a derivation for each syntactic parse.
        :rtype: Derivation
        """
        if tagged_sentence[-1][0] == '?':
            question = True
            sent_type = 'QUESTION'
        else:
            question = False
            sent_type = 'STATEMENT'

        tokens = self._getTokens(tagged_sentence)
        ccg_parses = self.ccg_parser.parse(tokens)

        for (i,parse) in enumerate(ccg_parses):
            if i+1 == n:
                break
            try:
                derivation = self.composer.buildExpressions(parse, tagged_sentence, question)
                yield Derivation(parse, derivation, sent_type)
                continue
            # Yield just syntactic parse if semantics fail.
            except LogicalExpressionException:
                yield Derivation(parse, None, sent_type)
                continue
            else:
                yield Derivation(parse, None, sent_type)
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
