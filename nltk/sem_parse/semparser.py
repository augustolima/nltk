# Natural Language Toolkit: Semantic Parser
#
# Copyright (C) 2001-2015 NLTK Project
# Author: Jake Vasilakes <s1420849@sms.ed.ac.uk>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

'''
Semantic parser which builds MRs using nltk.ccg

Data:
Relies on nltk:grammars/ccg_grammars/lex.ccg
Get it from <homepages.inf.ed.ac.uk/s1420849/lex.ccg>
and put it in, e.g. $HOME/nltk_data/grammars/ccg_grammars/lex.ccg
'''
from __future__ import print_function, division, unicode_literals

import sys
import random

from nltk.data import load
from nltk.ccg import lexicon, chart

from nltk.corpus import dependency_treebank
from nltk.parse import dependencygraph as dg
from nltk.parse import projectivedependencyparser as dp


class CCGSemParser(object):
    """
    A semantic parser that builds first-order logic meaning
    representations (MRs) using the lambda-calculus from
    CCG parses.

    Current status:
        Syntactically parse a NL sentence using the nltk.ccg
        module and a custom lexicon, lex.ccg.

    Usage example:
        from nltk.sem_parse import semparser
        from nltk.ccg import chart
        SP = semparser.CCGSemParser("grammars/ccg_grammars/lex.ccg")
        parses = SP.parse("I went home")
        chart.printCCGDerivation(next(parses))
    """

    def __init__(self, lex):
        """
        :param str lex: nltk path to ccg lexicon file
        """
        self._parser = self.buildParser(lex)

    def buildParser(self, lex):
        """
        Create a CCG parser from the provided lexicon.

        :param str lex: nltk path to ccg lexicon file
        """
        rules = load(lex, 'text')
        lex = lexicon.parseLexicon(str(rules))
        parser = chart.CCGChartParser(lex, chart.DefaultRuleSet)
        return parser

    def parse(self, sentence):
        """
        Parse the sentence.

        :param str sentence: input sentence to be parsed
        """
        return self._parser.parse(sentence.split())


class DependencySemParser(object):
    """
    Semantic parser which (will) build meaning representations recursively
    bottom-up guided from the dependency parse of the sentence.

    Current Status:
        Trained and tested using freely available CONLL-U data.
        None or very few sentences in the training data are actually
        able to be parsed.
        Additionally, a ZeroDivisionError is raised when parsing some
        sentences during the probability computation.

    Usage example:
        The parser can be trained and tested simply using the DepDemo()
        function. Output parses are NLTK Trees.

        from nltk.sem_parse.semparser import DependencySemParser
        SemParser = DependencySemParser(train='path/to/training_data', test='path/to/test_data')
        SemParser.train()
        parses = SemParser.parse(['I', 'went', 'home', '.'])
        for parse in parses:
            print parse
    """

    def __init__(self, train='data/en-ud-train.conllu', test='data/en-ud-dev.conllu'):
        """
        param str train: path to training data file.
        param str test: path to test data file.
        """
        self._training_data = self._get_train_data(train)
        self._testing_data = self._get_test_data(test)
        self._parser = dp.ProbabilisticProjectiveDependencyParser()

    def _get_train_data(self, data_file):
        """
        Read in the training data and create DependencyGraphs from 
        each sentence. These are used by the self._parser.train() method.

        param str data_file: path to training data file.
        """
        #data = dependency_treebank.raw().split('\n\n')  #data1
        data = open(data_file).read().split('\n\n')  #data2
        data = [dg.DependencyGraph(entry) for entry in data]
        return data

    def _get_test_data(self, data_file):
        """
        Read in the test/dev data. Create tuples of (sentence, gold_parse).

        param str data_file: path to test data file.
        """
        data = open(data_file).read().split('\n\n')
        #data = open('data/en-ud-train.conllu').read().split('\n\n')  #data2
        data = [entry for entry in data if entry]
        gold_pairs = []
        for entry in data:
            sentence = self._extract_sentence_from_entry(entry)
            parse = dg.DependencyGraph(entry).tree()
            gold_pairs.append((sentence, parse))
        return gold_pairs

    def _extract_sentence_from_entry(self, entry):
        """
        Gets the sentence as a list of words from the entry in the data.

        :param str entry: a sentence and it's associated annotations.
        """
        sentence = entry.split('\n')
        if len(sentence) <= 1: return []
        sentence = [field.split('\t') for field in sentence]
        # 0 index is the word for data1, 1 index is the word for data2.
        sentence = [field[1] for field in sentence]
        return sentence

    def parse(self, sentence):
        """
        Parse the sentence using the trained parser.
        Returns a generator.

        param list sentence: input sentence as a list of words.
        """
        return self._parser.parse(sentence)

    def train(self):
        """
        Create dependency graphs from the training
        data and train the parser.
        """
        self._parser.train(self._training_data)
        
    def test(self):
        """
        Using the trained projective dependency parser,
        parse the test data and compute accuracy.
        """
        correct = 0
        for (i,(sent,gold_parse)) in enumerate(self._testing_data):
            sys.stderr.write("{0}/{1}\r" .format(i, len(self._testing_data)))

            try:
                hyp = list(self.parse(sent))
            except ZeroDivisionError:
                print("ZeroDivisionError raised parsing: {0}" .format(sent))
            except:
                print("\n## Results ##")
                print("{0}/{1} sentences parsed correctly" 
                       .format(correct, len(self._testing_data)))
                print("Accuracy: {0}" 
                       .format((float(correct)/len(self._testing_data))))
                return

            if hyp:
                print("GOLD\n{0}" .format(gold_parse))
                for parse in hyp:
                    print("HYP\n{0}\n" .format(parse))
                raw_input()

            if gold_parse in hyp:
                correct += 1

        print("\n## Results ##")
        print("{0}/{1} sentences parsed correctly" 
               .format(correct, len(self._testing_data)))
        print("Accuracy: {0}" 
               .format((float(correct)/len(self._testing_data))))


def CCGDemo():
    print("Building parser...")
    semparser = CCGSemParser("grammars/ccg_grammars/lex.ccg")
    sentence = "I went home"
    print("\nParsing '{0}'...\n" .format(sentence))
    parses = semparser.parse(sentence)
    chart.printCCGDerivation(next(parses))


def DepDemo():
    print("Building parser...")
    semparser = DependencySemParser()
    print("Training...")
    semparser.train()
    print("Testing...")
    semparser.test()


if __name__ == '__main__':
    DepDemo()
