import re
import string
from nltk import word_tokenize
from nltk.ccg import lexicon, chart
from predicatelexicon import PredicateLexicon
from composer import SemanticComposer

class SemanticParser(object):
    """
    Relies on a CCG parser and a semantic composition function.
    Here we use nltk.ccg.CCGChartParser and nltk.semparse.SemanticComposer
    """
    def __init__(self, ccglex_file, predlex_file, syntax=False, derivation=False):
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
        self.syntax = syntax
        self.derivation = derivation

    def _setupCCGParser(self, ccglex_file):
        """
        Sets up the CCG parser to use.

        :param ccglex_file: CCG lexicon filename to use.
        :type ccglex_file: str
        :rtype: nltk.ccg.chart.CCGChartParser
        """
        lexfile = open(ccglex_file).read()
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

        :param sentence: sentence to parse into logical form.
        :type sentence: str
        :rtype: list
        """
        sentence = self._preprocessSent(sentence)
        try:
            ccg_parse = self.ccg_parser.parse(sentence).next()
        except:
            raise Exception("No valid syntactic parse for input sentence.")

        if self.syntax:
            print "\n======== SYNTACTIC PARSE ========\n"
            chart.printCCGDerivation(ccg_parse)
            print ""

        expressions = self.composer.buildExpressions(ccg_parse)
        if self.derivation:
            print "========= DERIVATION ==========\n"
            for expr in expressions:
                for d in expr.derivation:
                    print d
                print ""

        return expressions
