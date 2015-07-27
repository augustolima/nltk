from __future__ import print_function, unicode_literals

import io
import sys
import unittest
import logging

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
        expression = SemanticCategory("won", "VBD", r'((S[dcl]{_}\NP{Y}<1>){_}/NP{Z}<2>){_}').getExpression()
        self.assertEqual(expression, lexpr(r'\P Q e.exists z y.(P(z) & Q(y) & won:1(e,y) & won:2(e,z))'))

    # MOD
    def testMod(self):
        expression = SemanticCategory("successful", "JJ", r'(N{Y}/N{Y}<1>){_}').getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & successful(y))')) 


        # TODO: figure out adverbs
        expression = SemanticCategory("annually", "RB",
                                       r'((S[X]{Y}\\NP{Z}){Y}\\(S[X]{Y}\\NP{Z}){Y}){_}').getExpression()
        self.assertEqual(expression, lexpr(r'\P \Q \y. exists z. (P(z)(y) & Q(z) & annually(y))'))

    # COUNT
    def testCount(self):
        expression = SemanticCategory("four", "CD", r'(N{Y}/N{Y}<1>){_}').getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & COUNT(y,four))'))

    # NEGATE
    def testNegate(self):
        expression = SemanticCategory("not", "RB",
                                      r'((S[X]{Y}\NP{Z}){Y}\(S[X]{Y}<1>\NP{Z}){Y}){_}').getExpression()
        self.assertEqual(expression, lexpr(r'\P Q y.exists z.(P(z)(y) & Q(z) & NEGATION(y))'))

    # COMPLEMENT
    def testComplement(self):
        expression = SemanticCategory("no", "DT", r'(NP[nb]{Y}/N{Y}<1>){_}').getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & COMPLEMENT(y))'))

    # UNIQUE
    def testUnique(self):
        expression = SemanticCategory("the", "DT", r'(NP[nb]{Y}/N{Y}<1>){_}').getExpression()
        self.assertEqual(expression, lexpr(r'\P y.(P(y) & UNIQUE(y))'))

    # INDEFINITE ARTICLES
    def testIndef(self):
        expression = SemanticCategory("an", "DT", r'(NP[nb]{Y}/N{Y}<1>){_}').getExpression()
        self.assertEqual(expression, lexpr("None"))

    # COPULA
    def testCopula(self):
        # "is" as copula.
        expression = SemanticCategory("is", "VBZ", 
                                      r'((S[dcl]{_}\NP{Y}<1>){_}/NP{Z}<2>){_}').getExpression()
        self.assertEqual(expression, lexpr(r'\P Q y.exists x.(Q(x) & P(x))'))

        expression = SemanticCategory("is", "VBZ",
                                      r'((S[dcl]{_}\NP{Y}<1>){_}/(S[adj]{Z}<2>\NP{Y*}){Z}){_}').getExpression()
        self.assertEqual(expression, lexpr(r'\P Q y.exists x.(Q(x) & P(x))'))

        # "is" as a normal verb.
        expression = SemanticCategory("is", "VBZ",
                                      r'((S[dcl]{_}\NP{Y}<1>){_}/S[qem]{Z}<2>){_}').getExpression()
        self.assertEqual(expression, lexpr(r'\P Q e.exists z y.(P(z) & Q(y) & is:1(e,y) & is:2(e,z))'))

        # "is" in a question.
        expression = SemanticCategory("is", "VBZ", r'((S[dcl]{_}\NP{Y}<1>){_}/NP{Z}<2>){_}',
                                      question = True).getExpression() 
        self.assertEqual(expression, lexpr(r'\P x. (P(x))'))

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
        expression = SemanticCategory("What", "WP", r'(S[wq]{_}/(S[q]{Y}<1>/NP{Z}){Y}){_}',
                                      question = True).getExpression()
        self.assertEqual(expression, lexpr(r'\P x.(P(x) & TARGET(x))'))


class SemanticParserTest(unittest.TestCase):

    def testStatement(self):
        sys.stdout.write("\nSTATEMENTS\n")
        semParser = SemanticParser('data/reagan/ccg.lex', 'data/reagan/predicates.lex')
        total = 0
        num_parsed = 0
        num_sem = 0
        with io.open('data/test/reagan.txt', 'rt', encoding='utf-8') as sentences:
            for sent in sentences:
                total += 1
                print('\n', sent)
                try:
                    derivation = semParser.parse(sent).next()
                    print(derivation.expression)
                    if derivation.syntax is not None:
                        num_parsed += 1
                    if derivation.expression is not None:
                        num_sem += 1
                except Exception as e:
                    print(e)
            print()
        print("STATEMENTS SYNPARSED: {0}/{1}".format(num_parsed, total))
        print("STATEMENTS SEMPARSED: {0}/{1}".format(num_sem, total))
        logging.info("STATEMENTS SYNPARSED: {0}/{1}".format(num_parsed, total))
        logging.info("STATEMENTS SEMPARSED: {0}/{1}".format(num_sem, total))

    def testQuestion(self):
        sys.stdout.write("\nQUESTIONS\n")
        semParser = SemanticParser('data/geoquery/ccg.lex', 'data/geoquery/predicates.lex')
        total = 0
        num_parsed = 0
        num_sem = 0
        with io.open('data/test/geoquery.txt', 'rt', encoding='utf-8') as sentences:
            for sent in sentences:
                total += 1
                print('\n', sent)
                try:
                    derivation = semParser.parse(sent).next()
                    print(derivation.expression)
                    if derivation.syntax is not None:
                        num_parsed += 1
                    if derivation.expression is not None:
                        num_sem += 1
                except Exception as e:
                    print(e)
            print()
        print("QUESTIONS SYNPARSED: {0}/{1}".format(num_parsed, total))
        print("QUESTIONS SEMPARSED: {0}/{1}".format(num_sem, total))
        logging.info("QUESTIONS SYNPARSED: {0}/{1}".format(num_parsed, total))
        logging.info("QUESTIONS SEMPARSED: {0}/{1}".format(num_sem, total))
        

if __name__ == '__main__':
    unittest.main()
