from __future__ import print_function

import unittest
import time
import sys
import chart, lexicon
from nltk.data import load


# /////////////////////////////////////////////
# ///            Lexicon Tests              ///
# /////////////////////////////////////////////
class SimpleLexiconTestCase(unittest.TestCase):
    def setUp(self):
        self.startTime = time.time()
        self.lexicon_string = load('grammars/ccg_grammars/lex.ccg', 'text')
        self.lexicon_object = lexicon.parseLexicon(self.lexicon_string)

    def tearDown(self):
        totalTime = time.time() - self.startTime
        print("{0:.3f}" .format(totalTime))


class LexiconExistsTestCase(SimpleLexiconTestCase):
    def runTest(self):
        self.assertTrue(self.lexicon_object)


class LexiconNotEmptyTestCase(SimpleLexiconTestCase):
    def runTest(self):
        self.assertTrue(self.lexicon_object.start())


# /////////////////////////////////////////////
# ///             Parser Tests              ///
# /////////////////////////////////////////////
class SimpleParserTestCase(unittest.TestCase):
    def setUp(self):
        self.startTime = time.time()
        self.lexicon = lexicon.parseLexicon( load( \
                        'grammars/ccg_grammars/lex.ccg', 'text'))
        self.parser = chart.CCGChartParser(self.lexicon, chart.DefaultRuleSet)

    def tearDown(self):
        totalTime = time.time() - self.startTime
        print("{0:.3f}" .format(totalTime))


class ParserExistsTestCase(SimpleParserTestCase):
    def runTest(self):
        self.assertTrue(self.parser)


class ParserLexiconExistsTestCase(SimpleParserTestCase):
    def runTest(self):
        self.assertTrue(self.parser.lexicon())


class ParserAcceptsGoodInputSentences(SimpleParserTestCase):
    def runTest(self):
        P = self.parser
        ps = P.parse("I went home".split())
        self.assertNotEqual(sum(1 for _ in ps), 0)

        ps = P.parse("cars go fast".split())
        self.assertNotEqual(sum(1 for _ in ps), 0)
                
        ps = P.parse("people do not see things the same way".split())
        self.assertNotEqual(sum(1 for _ in ps), 0)


class ParserRejectsBadInputSentences(SimpleParserTestCase):
    def runTest(self):
        P = self.parser
        ps = P.parse("pale blue eyes".split())
        self.assertEqual(sum(1 for _ in ps), 0)

        ps = P.parse("I window guy".split())
        self.assertEqual(sum(1 for _ in ps), 0)

        # 'thou' is not in the lexicon.
        ps = P.parse("thou said to me".split())
        self.assertEqual(sum(1 for _ in ps), 0)


if __name__ == '__main__':
    unittest.main()
