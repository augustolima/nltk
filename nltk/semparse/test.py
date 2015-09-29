from __future__ import print_function, unicode_literals

import io
import sys
import unittest
import logging
import pickle

from nltk import word_tokenize, pos_tag
from nltk.sem.logic import Expression
from nltk.ccg import chart, lexicon
#from nltk.semparse.semanticcategory import SemanticCategory
#from nltk.semparse.semanticparser import SemanticParser
from syntacticcategory import SyntacticCategory
from semanticcategory import get_semantic_categories
from semanticparser import SemanticParser
from parseconverter import CCGParseConverter

'''
Unit tests for SemanticCategory.
'''

lexpr = Expression.fromstring
logging.basicConfig(filename=".unittest.log", level=logging.DEBUG)


class ParseConverterTest(unittest.TestCase):
    
    def test(self):
        gold_tree_file = "data/test/parse_converter_data/gold_tree.p"
        gold_tree = pickle.load(open(gold_tree_file, "rb"))
        converter = CCGParseConverter()
        ruleset = chart.DefaultRuleSet
        auto_string = r'''
        (<T S[dcl] 1 2> (<T NP 0 1> (<L N POS POS Reagan N>) ) (<T S[dcl]\NP 0 2> (<L (S[dcl]\NP)/NP POS POS had (S[dcl]\NP)/NP>) (<T NP 0 2> (<T NP 0 1> (<T N 1 2> (<L N/N POS POS four N/N>) (<L N POS POS children N>) ) ) (<L . POS POS . .>) ) ) )
        '''
        tree = converter.fromstring(auto_string, ruleset)
        self.assertEqual(tree, gold_tree)


class SemanticCategoryTest(unittest.TestCase):

    # EVENT
    def test_event(self):
        syncat = SyntacticCategory(r'(S\N)/N')
        semcats = get_semantic_categories("won", "VBD", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q e.exists z y.(P(z) & Q(y) & won:1(e,y) & won:2(e,z))') in expressions)

    # MOD
    def test_mod(self):
        syncat = SyntacticCategory(r'N/N')
        semcats = get_semantic_categories("successful", "JJ", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P y.(P(y) & successful(y))') in expressions) 


        syncat = SyntacticCategory(r'(S\N)\(S\N)')
        semcats = get_semantic_categories("annually", "RB", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P \Q \y. exists z. (P(\x.EQUAL(x,z))(y) & Q(z) & annually(y))') in expressions)

    # COUNT
    def test_count(self):
        syncat = SyntacticCategory(r'N/N')
        semcats = get_semantic_categories("four", "CD", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P y.(P(y) & COUNT(y,four))') in expressions)

    # NEGATE
    def test_negate(self):
        syncat = SyntacticCategory(r'(S\N)\(S\N)')
        semcats = get_semantic_categories("not", "RB", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q y.exists z.(P(\x.EQUAL(x,z))(y) & Q(z) & NEGATION(y))') in expressions)

    # COMPLEMENT
    def test_complement(self):
        syncat = SyntacticCategory(r'N/N')
        semcats = get_semantic_categories("no", "DT", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P y.(P(y) & COMPLEMENT(y))') in expressions)

    # UNIQUE
    def test_unique(self):
        syncat = SyntacticCategory(r'N/N')
        semcats = get_semantic_categories("the", "DT", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P y.(P(y) & UNIQUE(y))') in expressions)

    # INDEFINITE ARTICLES
    def test_indef(self):
        syncat = SyntacticCategory(r'N/N')
        semcats = get_semantic_categories("an", "DT", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr("None") in expressions)

    # COPULA
    def test_copula1(self):
        # "is" as copula.
        syncat = SyntacticCategory(r'(S\N)/N')
        semcats = get_semantic_categories("is", "VBZ", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q y. exists z.(\x.EQUAL(x,y)(z) & P(z) & Q(y))') in expressions)

    def test_ques_copula(self):
        # "is" in a question.
        syncat = SyntacticCategory(r'(S\N)/N')
        semcats = get_semantic_categories("is", "VBZ", syncat, question=True)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P x. (P(x))') in expressions)

    def test_is_event1(self):
        # "is" as a normal verb.
        syncat = SyntacticCategory(r'(S\N)/S')
        semcats = get_semantic_categories("is", "VBZ", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q e.exists z y.(P(z) & Q(y) & is:1(e,y) & is:2(e,z))') in expressions)

    def test_is_as_event2(self):
        syncat = SyntacticCategory(r'(S\N)/(S\N)')
        semcats = get_semantic_categories("is", "VBZ", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q e. exists y z.(P(\x.EQUAL(x,z),y) & Q(z) & is:1(e,z) & is:2(e,y))') in expressions)

    # TYPE
    def test_type(self):
        syncat = SyntacticCategory('N')
        semcats = get_semantic_categories("actor", "NN", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\x.(actor(x))') in expressions)

    # ENTITY
    def test_entity(self):
        syncat = SyntacticCategory('N')
        semcats = get_semantic_categories("Reagan", "NNP", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\x.EQUAL(x, reagan)') in expressions)

    # CONJ
    def test_conj(self):
        syncat = SyntacticCategory('conj')
        semcats = get_semantic_categories("and", "CC", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q x.(P(x) & Q(x))') in expressions)

    # QUESTION
    def test_question(self):
        syncat = SyntacticCategory(r'S/(S/N)')
        semcats = get_semantic_categories("What", "WP", syncat, question=True)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P. exists x.(P(x) & TARGET(x))') in expressions)

    # DEGREE QUESTION
#    def testDegQuestion(self):
#        syncat = SyntacticCategory(r'S/S')
#        semcats = get_semantic_categories("How", "WP", syncat, question=True)
#        expressions = [s.get_expression() for s in semcats]
#        self.assertTrue(lexpr(r'\P Q x.(Q(x) & P(x) & degree(P(d)) & TARGET(d))') in expressions)

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

    def test_statement(self):
        sys.stderr.write("\n" + bcolors.HEADER + bcolors.BOLD + "STATEMENTS" + bcolors.ENDC + "\n")
        filestr = open('data/lexica/reagan.ccg').read()
        ccglex = lexicon.parseLexicon(filestr)
        semParser = SemanticParser(ccglex)
        total = 0
        num_parsed = 0
        num_sem = 0
        with io.open('data/test/reagan.txt', 'rt', encoding='utf-8') as sentences:
            for sent in sentences:
                if sent.startswith('#'):
                    continue
                total += 1
                parsed = False
                sem_parsed = False
                tagged = pos_tag(word_tokenize(sent))
                error = None
                derivations = semParser.parse(tagged, n=100)
                try:
                    for derivation in derivations:
                        if derivation.syntax is not None:
                            parsed = True
                        if derivation.get_expression() is not None:
                            if len(derivation.semantics.leaves()) == len(tagged)-1:
                                sem_parsed = True
                                break
                except:
                    error = str(sys.exc_info()[1])
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

    def test_question(self):
        sys.stderr.write("\n" + bcolors.HEADER + bcolors.BOLD + "QUESTIONS" + bcolors.ENDC + "\n")
        filestr = open('data/lexica/geoquery.ccg').read()
        ccglex = lexicon.parseLexicon(filestr)
        semParser = SemanticParser(ccglex)
        total = 0
        num_parsed = 0
        num_sem = 0
        with io.open('data/test/geoquery.txt', 'rt', encoding='utf-8') as sentences:
            for sent in sentences:
                if sent.startswith('#'):
                    continue
                total += 1
                parsed = False
                sem_parsed = False
                tagged = pos_tag(word_tokenize(sent))
                error = None
                derivations = semParser.parse(tagged, n=100)
                try:
                    for derivation in derivations:
                        if derivation.syntax is not None:
                            parsed = True
                        if derivation.get_expression() is not None:
                            if len(derivation.semantics.leaves()) == len(tagged)-1:
                                sem_parsed = True
                                break
                except:
                    error = str(sys.exc_info()[1])

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
