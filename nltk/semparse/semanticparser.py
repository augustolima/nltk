from __future__ import print_function, unicode_literals

import string
import re

from nltk.ccg import chart
from nltk.sem.logic import Expression, LogicalExpressionException

from config import parse_markedup_file ##
from composer import SemanticComposer ##
from parseconverter import CCGParseConverter ##
#from nltk.semparse.config import parse_markedup_file
#from nltk.semparse.composer import SemanticComposer
#from nltk.semparse.parseconverter import CCGParseConverter


lexpr = Expression.fromstring


class CCGParseException(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class Derivation(object):

    def __init__(self, syntax, semantics, sentence_type):
        self.syntax = syntax
        self.semantics = semantics
        self.sentence_type = sentence_type

    def check(self):
        """
        Checks if expression is valid.

        :param expression: logical expression to check.
        :type expression: nltk.sem.logic.Expression
        :rtype: bool
        """
        expression = self.get_expression()
        if not expression:
            return False
        # Check for misplaced lambda expressions.
        if re.findall(r'[a-zA-Z]+?(?::[0-9])?\([^a-z]', str(expression)):
            return False
        try:
            lexpr(str(expression))
            return True
        except Exception:
            return False

    def print_syntactic_derivation(self):
        chart.printCCGDerivation(self.syntax)

    def print_semantic_derivation(self):
        if not self.semantics:
            print("None")
            return

        def derivation_print(tree):
            if len(tree) < 2:
                return tree
            rule = tree.label()[-1]
            lhs = derivation_print(tree[0])
            rhs = derivation_print(tree[1])
            print("{0} {1} {2}\n\t==> {3}\n"
                   .format(lhs, rule, rhs, tree.label()[0]))
            return tree.label()[0]

        derivation_print(self.semantics)

    def get_expression(self):
        if self.semantics:
            return self.semantics.label()[0]
        else:
            return None


class SemanticParser(object):
    """
    Relies on a CCG parser and a semantic composition function.
    Here use nltk.ccg.CCGChartParser and nltk.semparse.SemanticComposer
    """
    def __init__(self, ccg_lexicon=None):
        """
        :param ccglex_file: CCG lexicon filename.
        :type ccglex_file: str
        """
        self.rules = chart.DefaultRuleSet
        if ccg_lexicon:
            self.ccg_parser = chart.CCGChartParser(ccg_lexicon, self.rules)
            families = ccg_lexicon._families.items()
            replacements = [(r[0], str(r[1][0])) for r in families]
        else:
            self.ccg_parser = None
            replacements = []
        syncat_dict = parse_markedup_file(replacements)
        self.composer = SemanticComposer(syncat_dict)

    def _get_tokens(self, tagged_sentence):
        """
        Gets the words of the sentence and removes punctuation.

        :param tagged_sentence: POS tagged input sentence.
        :type tagged_sentence: list(tuple(str, str))
        :rtype: list
        """
        tokens = [tagtok[0] for tagtok in tagged_sentence]
        tokens = [tok for tok in tokens if tok not in string.punctuation]
        return tokens

    def parse(self, tagged_sentence, ccg_parse_str=None, n=0):
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
        if not self.ccg_parser and not ccg_parse_str:
            raise CCGParseException("No CCG parser or CCG parse specified.")

        # Determine if input is a question or a statement.
        if tagged_sentence[-1][0] == '?':
            question = True
            sent_type = 'QUESTION'
        else:
            question = False
            sent_type = 'STATEMENT'

        # Get just the tokens from the POS tagged sentence.
        tokens = self._get_tokens(tagged_sentence)

        # Get the CCG parse(s).
        if ccg_parse_str:
            converter = CCGParseConverter()
            ccg_parse = converter.fromstring(ccg_parse_str, self.rules)
            ccg_parses = [ccg_parse]
        else:
            ccg_parses = self.ccg_parser.parse(tokens)

        # Build semantic expression for input sentence.
        for i, parse in enumerate(ccg_parses):
            if i+1 == n:
                break
            try:
                derivations = self.composer.build_expressions(parse,
                                                              tagged_sentence,
                                                              question)
                for derivation in derivations:
                    yield Derivation(parse, derivation, sent_type)
                continue
            # Yield just syntactic parse if semantics fail.
            # TODO: make sure this exception works with new SemanticComposer
            except LogicalExpressionException:
                yield Derivation(parse, None, sent_type)
                continue


def demo():
    from nltk import word_tokenize, pos_tag
    from nltk.ccg import lexicon

    # The semantic parser can either parse the input sentence
    # using nltk.ccg.
    ccglex = lexicon.parseLexicon(r'''
        :- S, N, NP
        NP :: N
        I => NP
        eat => (S\NP)/NP
        peaches => N
    ''')
    semparser = SemanticParser(ccglex)

    sent = "I eat peaches."
    tagged_sent = pos_tag(word_tokenize(sent))
    for parse in semparser.parse(tagged_sent):
        parse.semantics.draw()
        print(parse.get_expression())
        break

    # Or you can provide a parse in the auto format.
    parse_str = r'''
    (<T S[dcl] 1 2> (<L NP POS POS I NP>)
    (<T S[dcl]\NP 0 2> (<L (S[dcl]\NP)/NP POS POS eat
    (S[dcl]\NP)/NP>) (<T NP 0 1> (<L N POS POS peaches N>) ) ) )
    '''
    semparser2 = SemanticParser()
    for parse in semparser2.parse(tagged_sent, parse_str):
        parse.semantics.draw()
        print(parse.get_expression())
        break

if __name__ == '__main__':
    demo()
