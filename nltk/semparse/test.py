from __future__ import print_function, unicode_literals

import io
import sys
import unittest
import logging

from nltk import word_tokenize, pos_tag
from nltk.sem.logic import Expression
#from nltk.semparse.semanticcategory import SemanticCategory
#from nltk.semparse.semanticparser import SemanticParser
from semanticcategory import SemanticCategory ##
from semanticparser import SemanticParser ##

'''
Unit tests for SemanticCategory.
'''

lexpr = Expression.fromstring
logging.basicConfig(filename=".unittest.log", level=logging.DEBUG)


class SemanticCategoryTest(unittest.TestCase):

    # EVENT
    def testEvent(self):
        expression = SemanticCategory("won", "VBD", r'(S\N)/N').getExpression()
        self.assertEqual(expression, lexpr(r'\P Q e.exists z y.(P(z) & Q(y) & won:1(e,y) & won:2(e,z))'))

    # MOD
    def testMod(self):
        expression = SemanticCategory("successful", "JJ", r'N/N').getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & successful(y))')) 


        expression = SemanticCategory("annually", "RB", r'(S\N)\(S\N)').getExpression()
        self.assertEqual(expression, lexpr(r'\P \Q \y. exists z. (P(\x.EQUAL(x,z))(y) & Q(z) & annually(y))'))

    # COUNT
    def testCount(self):
        expression = SemanticCategory("four", "CD", r'N/N').getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & COUNT(y,four))'))

    # NEGATE
    def testNegate(self):
        expression = SemanticCategory("not", "RB", r'(S\N)\(S\N)').getExpression()
        self.assertEqual(expression, lexpr(r'\P Q y.exists z.(P(\x.EQUAL(x,z))(y) & Q(z) & NEGATION(y))'))

    # COMPLEMENT
    def testComplement(self):
        expression = SemanticCategory("no", "DT", r'N/N').getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & COMPLEMENT(y))'))

    # UNIQUE
    def testUnique(self):
        expression = SemanticCategory("the", "DT", r'N/N').getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & UNIQUE(y))'))

    # INDEFINITE ARTICLES
    def testIndef(self):
        expression = SemanticCategory("an", "DT", r'N/N').getExpression()
        self.assertEqual(expression, lexpr("None"))

    # COPULA
    def testCopula1(self):
        # "is" as copula.
        expression = SemanticCategory("is", "VBZ", r'(S\N)/N').getExpression()
        self.assertEqual(expression, lexpr(r'\P Q y. exists z.(\x.EQUAL(x,y)(z) & P(z) & Q(y))'))

    def testQuesCopula(self):
        # "is" in a question.
        expression = SemanticCategory("is", "VBZ", r'(S\N)/N', question=True).getExpression() 
        self.assertEqual(expression, lexpr(r'\P x. (P(x))'))

    def testIsAsEvent(self):
        # "is" as a normal verb.
        expression = SemanticCategory("is", "VBZ", r'(S\N)/S').getExpression()
        self.assertEqual(expression, lexpr(r'\P Q e.exists z y.(P(z) & Q(y) & is:1(e,y) & is:2(e,z))'))

    def testIsAsEvent(self):
        expression = SemanticCategory("is", "VBZ", r'(S\N)/(S\N)').getExpression()
        self.assertEqual(expression, lexpr(r'\P Q e. exists z y.(P(z) & Q(y) & is:1(e,y) & is:2(e,z))'))

    # TYPE
    def testType(self):
        expression = SemanticCategory("actor", "NN", "N").getExpression()
        self.assertEqual(expression, lexpr(r'\x.(actor(x))'))

    # ENTITY
    def testEntity(self):
        expression = SemanticCategory("Reagan", "NNP", None).getExpression()
        self.assertEqual(expression, lexpr(r'\x.EQUAL(x, reagan)'))

    # CONJ
    def testConj(self):
        expression = SemanticCategory("and", "CC", "conj").getExpression()
        self.assertEqual(expression, lexpr(r'\P Q x.(P(x) & Q(x))'))

    # QUESTION
    def testQuestion(self):
        expression = SemanticCategory("What", "WP", r'S/(S/N)', question=True).getExpression()
        self.assertEqual(expression, lexpr(r'\P x.(P(x) & TARGET(x))'))

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class SemanticParserTest(unittest.TestCase):

    def testStatement(self):
        sys.stderr.write("\n" + bcolors.HEADER + bcolors.BOLD + "STATEMENTS" + bcolors.ENDC + "\n")
        semParser = SemanticParser('data/lexica/reagan.ccg')
        total = 0
        num_parsed = 0
        num_sem = 0
        with io.open('data/test/reagan.txt', 'rt', encoding='utf-8') as sentences:
            for sent in sentences:
                total += 1
                parsed = False
                sem_parsed = False
                tokens = word_tokenize(sent)
                tagged = pos_tag(tokens)
                error = None
                try:
                    derivations = semParser.parse(tagged)
                    for derivation in derivations:
                        if derivation.syntax is not None:
                            parsed = True
                        if derivation.expression is not None:
                            sem_parsed = True
#                            print(derivation.expression)
                except Exception as e:
                    error = str(e)
                if parsed: num_parsed += 1
                if sem_parsed: num_sem += 1

                if parsed:
                    sys.stderr.write('[' + bcolors.OKGREEN + 'SYN' + bcolors.ENDC + ']')
                else:
                    sys.stderr.write('[' + bcolors.FAIL + 'SYN' + bcolors.ENDC + ']')
                if sem_parsed:
                    sys.stderr.write('[' + bcolors.OKGREEN + 'SEM' + bcolors.ENDC + ']')
                else:
                    sys.stderr.write('[' + bcolors.FAIL + 'SEM' + bcolors.ENDC + ']')
                if error:
                    sys.stderr.write('[' + bcolors.WARNING + error + bcolors.ENDC + ']')
                sys.stderr.write(sent + '\r')

        sys.stderr.write(bcolors.HEADER + "STATEMENTS SYNPARSED: " + bcolors.ENDC + bcolors.BOLD + "{0}/{1}".format(num_parsed, total) + bcolors.ENDC + "\n")
        sys.stderr.write(bcolors.HEADER + "STATEMENTS SEMPARSED: " + bcolors.ENDC + bcolors.BOLD + "{0}/{1}".format(num_sem, total) + bcolors.ENDC + "\n")
        logging.info("STATEMENTS SYNPARSED: {0}/{1}".format(num_parsed, total))
        logging.info("STATEMENTS SEMPARSED: {0}/{1}".format(num_sem, total))

    def testQuestion(self):
        sys.stderr.write("\n" + bcolors.HEADER + bcolors.BOLD + "QUESTIONS" + bcolors.ENDC + "\n")
        semParser = SemanticParser('data/lexica/geoquery.ccg')
        total = 0
        num_parsed = 0
        num_sem = 0
        with io.open('data/test/geoquery.txt', 'rt', encoding='utf-8') as sentences:
            for sent in sentences:
                total += 1
                parsed = False
                sem_parsed = False
                tokens = word_tokenize(sent)
                tagged = pos_tag(tokens)
                error = None
                try:
                    derivations = semParser.parse(tagged)
                    for derivation in derivations:
                        if derivation.syntax is not None:
                            parsed = True
                        if derivation.expression is not None:
#                            print(derivation.expression)
                            sem_parsed = True
                except Exception as e:
                    error = str(e)
                if parsed: num_parsed += 1
                if sem_parsed: num_sem += 1

                if parsed:
                    sys.stderr.write('[' + bcolors.OKGREEN + 'SYN' + bcolors.ENDC + ']')
                else:
                    sys.stderr.write('[' + bcolors.FAIL + 'SYN' + bcolors.ENDC + ']')
                if sem_parsed:
                    sys.stderr.write('[' + bcolors.OKGREEN + 'SEM' + bcolors.ENDC + ']')
                else:
                    sys.stderr.write('[' + bcolors.FAIL + 'SEM' + bcolors.ENDC + ']')
                if error:
                    sys.stderr.write('[' + bcolors.WARNING + error + bcolors.ENDC + ']')
                sys.stderr.write(sent + '\r')

        sys.stderr.write(bcolors.HEADER + "STATEMENTS SYNPARSED: " + bcolors.ENDC + bcolors.BOLD + "{0}/{1}".format(num_parsed, total) + bcolors.ENDC + "\n")
        sys.stderr.write(bcolors.HEADER + "STATEMENTS SEMPARSED: " + bcolors.ENDC + bcolors.BOLD + "{0}/{1}".format(num_sem, total) + bcolors.ENDC + "\n")
        logging.info("QUESTIONS SYNPARSED: {0}/{1}".format(num_parsed, total))
        logging.info("QUESTIONS SEMPARSED: {0}/{1}".format(num_sem, total))


if __name__ == '__main__':
    unittest.main()
