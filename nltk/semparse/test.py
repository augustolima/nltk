import unittest

from semanticcategory import SemanticCategory

'''
Unit tests for SemanticCategory.
'''

class SemanticCategoryTest(unittest.TestCase):

    # TYPES
    def testType(self):
        expression = SemanticCategory("actor", "NN", "N").expression
        self.assertEqual(expression, r'\x.(actor(x))')

        expression = SemanticCategory("actors", "NNS", "N").expression
        self.assertEqual(expression, r'\x.(actors(x))')

    # MOD
    def testMod(self):
        expression = SemanticCategory("successful", "JJ", r'(N{Y}/N{Y}<1>){_}').expression
        self.assertEqual(expression, r'\P \y. (P(y) & successful(y))') 


        # TODO: figure out adverbs
#        expression = SemanticCategory("annually", "RB", r'((S[X]{Y}\\NP{Z}){Y}\\(S[X]{Y}\\NP{Z}){Y}){_}').expression
#        self.assertEqual(expression, r'\P \Q \y. exists z y. (P(z)(y) & Q(z) & annually(y))')

    # EVENT
    def testEvent(self):
        expression = SemanticCategory("won", "VBD", r'((S[dcl]{_}\NP{Y}<1>){_}/NP{Z}<2>){_}').expression
        self.assertEqual(expression, r'\Q \P \e. exists y z.(Q(y) & P(z) & won:1(e, z) & won:2(e, y))')


class SemanticParserTest(unittest.TestCase):
    # TODO: Make a list of test sentences and write test case.
    def test(self):
        pass

if __name__ == '__main__':
    unittest.main()
