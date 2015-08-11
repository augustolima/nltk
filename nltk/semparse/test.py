from __future__ import print_function, unicode_literals

import io
import sys
import unittest
import logging

from nltk import word_tokenize, pos_tag
from nltk.sem.logic import Expression
from nltk.ccg import lexicon
#from nltk.semparse.semanticcategory import SemanticCategory
#from nltk.semparse.semanticparser import SemanticParser
from syntacticcategory import SyntacticCategory
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
        syncat = SyntacticCategory(r'(S\N)/N')
        expression = SemanticCategory("won", "VBD", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\P Q e.exists z y.(P(z) & Q(y) & won:1(e,y) & won:2(e,z))'))

    # MOD
    def testMod(self):
        syncat = SyntacticCategory(r'N/N')
        expression = SemanticCategory("successful", "JJ", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & successful(y))')) 


        syncat = SyntacticCategory(r'(S\N)\(S\N)')
        expression = SemanticCategory("annually", "RB", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\P \Q \y. exists z. (P(\x.EQUAL(x,z))(y) & Q(z) & annually(y))'))

    # COUNT
    def testCount(self):
        syncat = SyntacticCategory(r'N/N')
        expression = SemanticCategory("four", "CD", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & COUNT(y,four))'))

    # NEGATE
    def testNegate(self):
        syncat = SyntacticCategory(r'(S\N)\(S\N)')
        expression = SemanticCategory("not", "RB", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\P Q y.exists z.(P(\x.EQUAL(x,z))(y) & Q(z) & NEGATION(y))'))

    # COMPLEMENT
    def testComplement(self):
        syncat = SyntacticCategory(r'N/N')
        expression = SemanticCategory("no", "DT", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & COMPLEMENT(y))'))

    # UNIQUE
    def testUnique(self):
        syncat = SyntacticCategory(r'N/N')
        expression = SemanticCategory("the", "DT", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & UNIQUE(y))'))

    # INDEFINITE ARTICLES
    def testIndef(self):
        syncat = SyntacticCategory(r'N/N')
        expression = SemanticCategory("an", "DT", syncat).getExpression()
        self.assertEqual(expression, lexpr("None"))

    # COPULA
    def testCopula1(self):
        # "is" as copula.
        syncat = SyntacticCategory(r'(S\N)/N')
        expression = SemanticCategory("is", "VBZ", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\P Q y. exists z.(\x.EQUAL(x,y)(z) & P(z) & Q(y))'))

    def testQuesCopula(self):
        # "is" in a question.
        syncat = SyntacticCategory(r'(S\N)/N')
        expression = SemanticCategory("is", "VBZ", syncat, question=True).getExpression() 
        self.assertEqual(expression, lexpr(r'\P x. (P(x))'))

    def testIsAsEvent(self):
        # "is" as a normal verb.
        syncat = SyntacticCategory(r'(S\N)/S')
        expression = SemanticCategory("is", "VBZ", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\P Q e.exists z y.(P(z) & Q(y) & is:1(e,y) & is:2(e,z))'))

    def testIsAsEvent(self):
        syncat = SyntacticCategory(r'(S\N)/(S\N)')
        expression = SemanticCategory("is", "VBZ", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\P Q e. exists y z.(P(\x.EQUAL(x,z),y) & Q(z) & is:1(e,z) & is:2(e,y))'))

    # TYPE
    def testType(self):
        syncat = SyntacticCategory('N')
        expression = SemanticCategory("actor", "NN", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\x.(actor(x))'))

    # ENTITY
    def testEntity(self):
        syncat = SyntacticCategory('N')
        expression = SemanticCategory("Reagan", "NNP", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\x.EQUAL(x, reagan)'))

    # CONJ
    def testConj(self):
        syncat = SyntacticCategory('conj')
        expression = SemanticCategory("and", "CC", syncat).getExpression()
        self.assertEqual(expression, lexpr(r'\P Q x.(P(x) & Q(x))'))

    # QUESTION
    def testQuestion(self):
        syncat = SyntacticCategory(r'S/(S/N)')
        expression = SemanticCategory("What", "WP", syncat, question=True).getExpression()
        self.assertEqual(expression, lexpr(r'\P x.(P(x) & TARGET(x))'))

    # DEGREE QUESTION
    def testDegQuestion(self):
        syncat = SyntacticCategory(r'S/S')
        expression = SemanticCategory("How", "WP", syncat, question=True).getExpression()
        self.assertEqual(expression, lexpr(r'\P Q x.(Q(x) & P(x) & degree(P(d)) & TARGET(d))'))

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
        filestr = open('data/lexica/reagan.ccg').read()
        ccglex = lexicon.parseLexicon(filestr)
        semParser = SemanticParser(ccglex)
        total = 0
        num_parsed = 0
        num_sem = 0
        with io.open('data/test/reagan.txt', 'rt', encoding='utf-8') as sentences:
            for sent in sentences:
                total += 1
                parsed = False
                sem_parsed = False
                tagged = pos_tag(word_tokenize(sent))
                error = None
                try:
                    derivations = semParser.parse(tagged, n=100)
                    for derivation in derivations:
                        if derivation.syntax is not None:
                            parsed = True
                        if derivation.semantics is not None:
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
        logging.info("STATEMENTS SYNPARSED: {0}/{1}".format(num_parsed, total))
        logging.info("STATEMENTS SEMPARSED: {0}/{1}".format(num_sem, total))

    def testQuestion(self):
        sys.stderr.write("\n" + bcolors.HEADER + bcolors.BOLD + "QUESTIONS" + bcolors.ENDC + "\n")
        filestr = open('data/lexica/geoquery.ccg').read()
        ccglex = lexicon.parseLexicon(filestr)
        semParser = SemanticParser(ccglex)
        total = 0
        num_parsed = 0
        num_sem = 0
        with io.open('data/test/geoquery.txt', 'rt', encoding='utf-8') as sentences:
            for sent in sentences:
                total += 1
                parsed = False
                sem_parsed = False
                tagged = pos_tag(word_tokenize(sent))
                error = None
                try:
                    derivations = semParser.parse(tagged, n=100)
                    for derivation in derivations:
                        if derivation.syntax is not None:
                            parsed = True
                        if derivation.getExpression() is not None:
                            sem_parsed = True
                            break
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
