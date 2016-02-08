from __future__ import print_function, unicode_literals

import io
import sys
import os
import unittest
import logging
import pickle
import traceback
import string

from nltk import word_tokenize, pos_tag
from nltk.sem.logic import Expression
from nltk.ccg import chart, lexicon

from nltk.semparse import get_semantic_categories, build_ccglex
from nltk.semparse.config import parse_markedup_file
from nltk.semparse.semanticparser import SemanticParser
from nltk.semparse.syntacticcategory import SyntacticCategory
from nltk.semparse.parseconverter import CCGParseConverter

'''
Unit tests for SemanticCategory.
'''


lexpr = Expression.fromstring
logging.basicConfig(filename=".unittest.log", level=logging.DEBUG)

# /////////////
# Unit Tests //
# /////////////

class ParseConverterTest(unittest.TestCase):

    def test(self):
        gold_tree_file = "data/test/parse_converter_data/gold_tree.p"
        gold_tree = pickle.load(open(gold_tree_file, "rb"))
        converter = CCGParseConverter()
        ruleset = chart.DefaultRuleSet
        auto_string = r'''
        (<T S[dcl] 1 2> (<T NP 0 1> (<L N NNP NNP Reagan N>) )
        (<T S[dcl]\NP 0 2> (<L (S[dcl]\NP)/NP VBD VBD had (S[dcl]\NP)/NP>)
        (<T NP 0 2> (<T NP 0 1> (<T N 1 2> (<L N/N CD CD four N/N>)
        (<L N NNS NNS children N>) ) ) (<L . . . . .>) ) ) )
        '''
        tree = converter.fromstring(auto_string, ruleset)
        self.assertEqual(tree, gold_tree)


class BuildCCGLexiconTest(unittest.TestCase):

    def setUp(self):
        self.reagan_ccg_file = 'test_reagan.ccg'
        self.geoquery_ccg_file = 'test_geoquery.ccg'
        build_ccglex.main('data/lexica/reagan_supertags.txt',
                           self.reagan_ccg_file)
        build_ccglex.main('data/lexica/geoquery_supertags.txt',
                           self.geoquery_ccg_file)

    def tearDown(self):
        os.remove(self.reagan_ccg_file)
        os.remove(self.geoquery_ccg_file)

    def test_reagan_ccg_valid(self):
        ccglex = lexicon.fromstring(open(self.reagan_ccg_file).read())
        self.assertTrue(ccglex)

    def test_geoquery_ccg_valid(self):
        ccglex = lexicon.fromstring(open(self.geoquery_ccg_file).read())
        self.assertTrue(ccglex)

    def test_reagan_ccg_parse(self):
        ccglex = lexicon.fromstring(open(self.reagan_ccg_file).read())
        semparser = SemanticParser(ccglex)
        sent = "They had four children."
        tagged_sent = pos_tag(word_tokenize(sent))
        parses = list(semparser.parse(tagged_sent, n=10))
        self.assertTrue(parses)

    def test_geoquery_ccg_parse(self):
        ccglex = lexicon.fromstring(open(self.geoquery_ccg_file).read())
        semparser = SemanticParser(ccglex)
        sent = "What is the capital?"
        tagged_sent = pos_tag(word_tokenize(sent))
        parses = list(semparser.parse(tagged_sent, n=10))
        self.assertTrue(parses)


class SemanticCategoryTest(unittest.TestCase):

    def setUp(self):
        self.syncat_dict = parse_markedup_file()

    # EVENT
    def test_event(self):
        # TODO: add test for gerunds which act like verbs,
        #       e.g. "running man" NP/N
        syncat = SyntacticCategory(r'(S[dcl]\NP)/NP', self.syncat_dict)
        semcats = get_semantic_categories("won", "VBD", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q e.exists z y.(P(z) & Q(y) & won:1(e,y) & won:2(e,z))') in expressions)

    # MOD
    def test_mod(self):
        # TODO: add test for athletic "S\NP" JJ
        syncat = SyntacticCategory(r'N/N', self.syncat_dict)
        semcats = get_semantic_categories("successful", "JJ", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P y.(P(y) & successful(y))') in expressions)

        syncat = SyntacticCategory(r'(S\NP)\(S\NP)', self.syncat_dict)
        semcats = get_semantic_categories("annually", "RB", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P \Q \y. exists z. (P(\x.EQUAL(x,z))(y) & Q(z) & annually(y))') in expressions)

    # COUNT
    def test_count(self):
        syncat = SyntacticCategory(r'N/N', self.syncat_dict)
        semcats = get_semantic_categories("four", "CD", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P y.(P(y) & COUNT(y,four))') in expressions)

    # NEGATE
    def test_negate(self):
        syncat = SyntacticCategory(r'(S\NP)\(S\NP)', self.syncat_dict)
        semcats = get_semantic_categories("not", "RB", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q y.exists z.(P(\x.EQUAL(x,z))(y) & Q(z) & NEGATION(y))') in expressions)

    # COMPLEMENT
    def test_complement(self):
        syncat = SyntacticCategory(r'NP[nb]/N', self.syncat_dict)
        semcats = get_semantic_categories("no", "DT", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P y.(P(y) & COMPLEMENT(y))') in expressions)

    # UNIQUE
    def test_unique(self):
        syncat = SyntacticCategory(r'NP/N', self.syncat_dict)
        semcats = get_semantic_categories("the", "DT", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P y.(P(y) & UNIQUE(y))') in expressions)

    # INDEFINITE ARTICLES
    def test_indef(self):
        syncat = SyntacticCategory(r'NP[nb]/N', self.syncat_dict)
        semcats = get_semantic_categories("an", "DT", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr("None") in expressions)

    # COPULA
    def test_copula1(self):
        # "is" as copula.
        syncat = SyntacticCategory(r'(S[dcl]\NP)/NP', self.syncat_dict)
        semcats = get_semantic_categories("is", "VBZ", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q y. exists z.(\x.EQUAL(x,y)(z) & P(z) & Q(y))') in expressions)

    def test_ques_copula(self):
        # "is" in a question.
        syncat = SyntacticCategory(r'(S\NP)/NP', self.syncat_dict)
        semcats = get_semantic_categories("is", "VBZ", syncat, question=True)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P x. (P(x))') in expressions)

    def test_is_as_event1(self):
        # "is" as a normal verb.
        syncat = SyntacticCategory(r'(S[dcl]\NP)/S[qem]', self.syncat_dict)
        semcats = get_semantic_categories("is", "VBZ", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q e.exists z y.(P(z) & Q(y) & is:1(e,y) & is:2(e,z))') in expressions)

    def test_is_as_event2(self):
        syncat = SyntacticCategory(r'(S\NP)/(S\NP)', self.syncat_dict)
        semcats = get_semantic_categories("is", "VBZ", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q e. exists y z.(P(\x.EQUAL(x,z),y) & Q(z) & is:1(e,z) & is:2(e,y))') in expressions)

    # TYPE
    def test_type(self):
        syncat = SyntacticCategory('N', self.syncat_dict)
        semcats = get_semantic_categories("actor", "NN", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\x.(actor(x))') in expressions)

    # ENTITY
    def test_entity(self):
        syncat = SyntacticCategory('NP', self.syncat_dict)
        semcats = get_semantic_categories("Reagan", "NNP", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\x.EQUAL(x, reagan)') in expressions)

    # CONJ
    def test_conj(self):
        syncat = SyntacticCategory('conj', self.syncat_dict)
        semcats = get_semantic_categories("and", "CC", syncat)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P Q x.(P(x) & Q(x))') in expressions)

    # QUESTION
    def test_question(self):
        syncat = SyntacticCategory(r'S[wq]/(S[q]/NP)', self.syncat_dict)
        semcats = get_semantic_categories("What", "WP", syncat, question=True)
        expressions = [s.get_expression() for s in semcats]
        self.assertTrue(lexpr(r'\P. exists x.(P(x) & TARGET(x))') in expressions)

    # DEGREE QUESTION
#    def testDegQuestion(self):
#        syncat = SyntacticCategory(r'S/S')
#        semcats = get_semantic_categories("How", "WP", syncat, question=True)
#        expressions = [s.get_expression() for s in semcats]
#        self.assertTrue(lexpr(r'\P Q x.(Q(x) & P(x) & degree(P(d)) & TARGET(d))') in expressions)


# ///////////////////
# Functional Tests //
# ///////////////////


class bcolors(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class SemanticParserTest(unittest.TestCase):

    def setUp(self):
        self.none_words = ['a', 'an'] + list(string.punctuation)

    def test_auto(self):
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
            ccg_expr = parse.get_expression()
            break

        # Or you can provide a parse in the auto format.
        parse_str = r'''
        (<T S[dcl] 1 2> (<L NP PRP PRP I NP>)
        (<T S[dcl]\NP 0 2> (<L (S[dcl]\NP)/NP VBP VBP eat
        (S[dcl]\NP)/NP>) (<T NP 0 1> (<L N NNS NNS peaches N>) ) ) )
        '''
        semparser2 = SemanticParser()
        for parse in semparser2.parse(parse_str):
            auto_expr = parse.get_expression()
            break

        self.assertEqual(ccg_expr, auto_expr)

#    @unittest.skip("skipping NLTK CCG tests")
    def test_statement_nltk(self):
        sys.stderr.write("\n" + bcolors.HEADER + bcolors.BOLD +
                         "STATEMENTS (NLTK CCG)" + bcolors.ENDC + "\n")
        filestr = open('data/lexica/reagan_new.ccg').read()
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
                tagged_sent = pos_tag(word_tokenize(sent))
                error = None
                derivations = semParser.parse(tagged_sent, n=100)
                try:
                    for deriv in derivations:
                        if deriv.syntax is not None:
                            parsed = True
                        if deriv.check():
                            words = deriv.semantics.leaves()
                            num_none_words = sum([1 for w in words
                                              if w in self.none_words])
                            exprs = [p[1][0] for p in deriv.semantics.pos()]
                            num_none_exprs = sum([1 for e in exprs if e is None])
                            if num_none_words == num_none_exprs:
                                sem_parsed = True
                                break
                except:
                    _, err, tb = sys.exc_info()
                    err_str = str(err)
                    error = traceback.extract_tb(tb)[-1]
                    filename = os.path.basename(error[0])
                    err_lineno = error[1]
                    err_string = "In {0}:{1} {2}" \
                                 .format(filename, err_lineno, err_str)

                if parsed:
                    num_parsed += 1
                if sem_parsed:
                    num_sem += 1

                if parsed:
                    sys.stderr.write('[' + bcolors.OKGREEN + 'SYN' +
                                     bcolors.ENDC + ']')
                else:
                    sys.stderr.write('[' + bcolors.FAIL + 'SYN' +
                                     bcolors.ENDC + ']')
                if sem_parsed:
                    sys.stderr.write('[' + bcolors.OKGREEN + 'SEM' +
                                     bcolors.ENDC + ']')
                else:
                    sys.stderr.write('[' + bcolors.FAIL + 'SEM' +
                                     bcolors.ENDC + ']')
                if error:
                    sys.stderr.write('[' + bcolors.WARNING +
                                     err_string +
                                     bcolors.ENDC + ']')
                sys.stderr.write(sent + '\r')

        sys.stderr.write(bcolors.HEADER + "STATEMENTS (NLTK CCG) SYNPARSED: " +
                         bcolors.ENDC + bcolors.BOLD +
                         "{0}/{1}".format(num_parsed, total) +
                         bcolors.ENDC + "\n")
        sys.stderr.write(bcolors.HEADER + "STATEMENTS (NLTK CCG) SEMPARSED: " +
                         bcolors.ENDC + bcolors.BOLD +
                         "{0}/{1}".format(num_sem, total) +
                         bcolors.ENDC + "\n")
        logging.info("STATEMENTS (NLTK CCG) SYNPARSED: {0}/{1}"
                      .format(num_parsed, total))
        logging.info("STATEMENTS (NLTK CCG) SEMPARSED: {0}/{1}"
                      .format(num_sem, total))

#    @unittest.skip("skipping NLTK CCG tests")
    def test_question_nltk(self):
        sys.stderr.write("\n" + bcolors.HEADER + bcolors.BOLD +
                         "QUESTIONS (NLTK CCG)" + bcolors.ENDC + "\n")
        filestr = open('data/lexica/geoquery_new.ccg').read()
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
                tagged_sent = pos_tag(word_tokenize(sent))
                error = None
                derivations = semParser.parse(tagged_sent, n=100)
                try:
                    for deriv in derivations:
                        if deriv.syntax is not None:
                            parsed = True
                        if deriv.check():
                            words = deriv.semantics.leaves()
                            num_none_words = sum([1 for w in words
                                              if w in self.none_words])
                            exprs = [p[1][0] for p in deriv.semantics.pos()]
                            num_none_exprs = sum([1 for e in exprs if e is None])
                            if num_none_words == num_none_exprs:
                                sem_parsed = True
                                break
                except:
                    _, err, tb = sys.exc_info()
                    err_str = str(err)
                    error = traceback.extract_tb(tb)[-1]
                    filename = os.path.basename(error[0])
                    err_lineno = error[1]
                    err_string = "In {0}:{1} {2}" \
                                 .format(filename, err_lineno, err_str)

                if parsed:
                    num_parsed += 1
                if sem_parsed:
                    num_sem += 1

                if parsed:
                    sys.stderr.write('[' + bcolors.OKGREEN + 'SYN' +
                                     bcolors.ENDC + ']')
                else:
                    sys.stderr.write('[' + bcolors.FAIL + 'SYN' +
                                     bcolors.ENDC + ']')
                if sem_parsed:
                    sys.stderr.write('[' + bcolors.OKGREEN + 'SEM' +
                                     bcolors.ENDC + ']')
                else:
                    sys.stderr.write('[' + bcolors.FAIL + 'SEM' +
                                     bcolors.ENDC + ']')
                if error:
                    sys.stderr.write('[' + bcolors.WARNING +
                                     err_string +
                                     bcolors.ENDC + ']')
                sys.stderr.write(sent + '\r')

        sys.stderr.write(bcolors.HEADER + "QUESTIONS (NLTK CCG) SYNPARSED: " +
                         bcolors.ENDC + bcolors.BOLD +
                         "{0}/{1}".format(num_parsed, total) +
                         bcolors.ENDC + "\n")
        sys.stderr.write(bcolors.HEADER + "QUESTIONS (NLTK CCG) SEMPARSED: " +
                         bcolors.ENDC + bcolors.BOLD +
                         "{0}/{1}".format(num_sem, total) +
                         bcolors.ENDC + "\n")
        logging.info("QUESTIONS (NTLK CCG) SYNPARSED: {0}/{1}"
                      .format(num_parsed, total))
        logging.info("QUESTIONS (NLTK CCG) SEMPARSED: {0}/{1}"
                      .format(num_sem, total))

    @unittest.skip("skipping NLTK CCG tests")
    def test_question_auto(self):
        sys.stderr.write("\n" + bcolors.HEADER + bcolors.BOLD +
                         "QUESTIONS (AUTO)" + bcolors.ENDC + "\n")
        semParser = SemanticParser()
        total = 0
        num_sem = 0
        parse_file = 'data/test/geoquery_parses.txt'
        with io.open(parse_file, 'rt', encoding='utf-8') as parses:
            for line in parses:
                if line.startswith('#'):
                    continue
                (sent, parse) = line.split(' || ')
                total += 1
                sem_parsed = False
                tagged_sent = pos_tag(word_tokenize(sent))
                error = None
                derivations = semParser.parse(parse, n=100)
                try:
                    for deriv in derivations:
                        if deriv.check():
                            words = deriv.semantics.leaves()
                            num_none_words = sum([1 for w in words
                                              if w in self.none_words])
                            exprs = [p[1][0] for p in deriv.semantics.pos()]
                            num_none_exprs = sum([1 for e in exprs if e is None])
                            if num_none_words == num_none_exprs:
                                sem_parsed = True
                                break
                except:
                    _, err, tb = sys.exc_info()
                    err_str = str(err)
                    error = traceback.extract_tb(tb)[-1]
                    filename = os.path.basename(error[0])
                    err_lineno = error[1]
                    err_string = "In {0}:{1} {2}" \
                                 .format(filename, err_lineno, err_str)

                if sem_parsed:
                    num_sem += 1

                if sem_parsed:
                    sys.stderr.write('[' + bcolors.OKGREEN + 'SEM' +
                                     bcolors.ENDC + ']')
                else:
                    sys.stderr.write('[' + bcolors.FAIL + 'SEM' +
                                     bcolors.ENDC + ']')
                if error:
                    sys.stderr.write('[' + bcolors.WARNING +
                                     err_string +
                                     bcolors.ENDC + ']')
                sys.stderr.write(sent + '\n')

        sys.stderr.write(bcolors.HEADER + "QUESTIONS (AUTO) SEMPARSED: " +
                         bcolors.ENDC + bcolors.BOLD +
                         "{0}/{1}".format(num_sem, total) +
                         bcolors.ENDC + "\n")
        logging.info("QUESTIONS (AUTO) SEMPARSED: {0}/{1}".format(num_sem, total))

    @unittest.skip("skipping NLTK CCG tests")
    def test_statement_auto(self):
        sys.stderr.write("\n" + bcolors.HEADER + bcolors.BOLD +
                         "STATEMENTS (AUTO)" + bcolors.ENDC + "\n")
        semParser = SemanticParser()
        total = 0
        num_sem = 0
        parse_file = 'data/test/reagan_parses.txt'
        with io.open(parse_file, 'rt', encoding='utf-8') as parses:
            for line in parses:
                if line.startswith('#'):
                    continue
                (sent, parse) = line.split(' || ')
                total += 1
                sem_parsed = False
                tagged_sent = pos_tag(word_tokenize(sent))
                error = None
                derivations = semParser.parse(parse, n=100)
                try:
                    for deriv in derivations:
                        if deriv.check():
                            words = deriv.semantics.leaves()
                            num_none_words = sum([1 for w in words
                                              if w in self.none_words])
                            exprs = [p[1][0] for p in deriv.semantics.pos()]
                            num_none_exprs = sum([1 for e in exprs if e is None])
                            if num_none_words == num_none_exprs:
                                sem_parsed = True
                                break
                except:
                    _, err, tb = sys.exc_info()
                    err_str = str(err)
                    error = traceback.extract_tb(tb)[-1]
                    filename = os.path.basename(error[0])
                    err_lineno = error[1]
                    err_string = "In {0}:{1} {2}" \
                                 .format(filename, err_lineno, err_str)

                if sem_parsed:
                    num_sem += 1

                if sem_parsed:
                    sys.stderr.write('[' + bcolors.OKGREEN + 'SEM' +
                                     bcolors.ENDC + ']')
                else:
                    sys.stderr.write('[' + bcolors.FAIL + 'SEM' +
                                     bcolors.ENDC + ']')
                if error:
                    sys.stderr.write('[' + bcolors.WARNING +
                                     err_string +
                                     bcolors.ENDC + ']')
                sys.stderr.write(sent + '\n')

        sys.stderr.write(bcolors.HEADER + "STATEMENTS (AUTO) SEMPARSED: " +
                         bcolors.ENDC + bcolors.BOLD +
                         "{0}/{1}".format(num_sem, total) +
                         bcolors.ENDC + "\n")
        logging.info("STATEMENTS (AUTO) SEMPARSED: {0}/{1}"
                      .format(num_sem, total))

if __name__ == '__main__':
    unittest.main()
