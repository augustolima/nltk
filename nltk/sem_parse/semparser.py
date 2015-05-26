# Natural Language Toolkit: Semantic Parser
#
# Copyright (C) 2001-2015 NLTK Project
# Author: Jake Vasilakes <s1420849@sms.ed.ac.uk>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

"""
Semantic parser built on top of CCG and Dependency, respectively.

Data:
    CCGSemParser relies on lex.ccg (grammar)
    DependencySemParser relies on en-ud-train.conllu (training)
                                  en-ud-dev.conllu (evaluation)
    All files in the data folder.
"""
from __future__ import print_function, division, unicode_literals

import sys
from collections import Counter

from nltk import Tree
from nltk.data import load
from nltk.ccg import lexicon, chart
from nltk.parse import (dependencygraph as dg,
                        projectivedependencyparser as dp)

# For timeout wrapper
from functools import wraps
import errno
import os
import signal


class TimeoutError(Exception):
	pass

def timeout(seconds=0.1, error_message=os.strerror(errno.ETIME)):
	def decorator(func):
		def _handle_timeout(signum, frame):
			sys.stderr.write("timedout query\n")
			raise TimeoutError("timeout")
			# exit()

		def wrapper(*args, **kwargs):
			signal.signal(signal.SIGALRM, _handle_timeout)
			signal.setitimer(signal.ITIMER_REAL, seconds)
			# signal.alarm(seconds)
			try:
				result = func(*args, **kwargs)
			finally:
				signal.alarm(0)
			return result

		return wraps(func)(wrapper)

	return decorator


class CCGSemParser(object):
    """
    A semantic parser that builds first-order logic meaning
    representations (MRs) using the lambda-calculus from
    CCG parses.

    Current status:
        Syntactically parse a NL sentence using the nltk.ccg
        module and a custom lexicon, lex.ccg.

    Usage example:
        from nltk.sem_parse.semparser import CCGSemParser
        from nltk.ccg import chart
        SemParser = CCGSemParser("grammars/ccg_grammars/lex.ccg")
        parses = SemParser.parse("I went home")
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
        89/2002 sentences in the development set are parsed correctly.

    Usage example:
        The parser can be trained and tested simply using the DepDemo()
        function. Output parses are NLTK Trees.

        from nltk.sem_parse.semparser import DependencySemParser
        SemParser = DependencySemParser(train='path/to/training_data',
                                        test='path/to/test_data')
        SemParser.train()
        parses = SemParser.parse(['I', 'went', 'home', '.'])
        for parse in parses:
            print parse
    """

    def __init__(self, train=None, test=None):
        """
        param str train: path to training data file.
        param str test: path to test data file.
        """
        self._parser = dp.ProbabilisticProjectiveDependencyParser()
        if train:
            self._training_data = self._get_train_data(train)
        if test:
            self._testing_data = self._get_test_data(test)

    def _get_train_data(self, data_file):
        """
        Read in the training data and create DependencyGraphs from
        each sentence. These are used by the self._parser.train() method.

        param str data_file: path to training data file.
        """
        data = open(data_file).read().split('\n\n')
        data = [dg.DependencyGraph(entry) for entry in data]
        return data

    def _get_test_data(self, data_file):
        """
        Read in the test/dev data. Create tuples of (sentence, gold_parse).

        param str data_file: path to test data file.
        """
        data = open(data_file).read().split('\n\n')
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
        if len(sentence) <= 1:
            return []
        sentence = [field.split('\t') for field in sentence]
        # index 1 is the word
        sentence = [field[1] for field in sentence]
        return sentence

    def _get_head_for_tokens(self, tree):
        """
        Retrieves list of (head, token) pairs for the input tree.

        param nltk.tree.Tree tree: input tree
        rtype: list(tuple(str,str))
        """
        pairs = []
        for subtree in tree.subtrees():
            head = subtree.label()
            tokens = []
            for child in subtree:
                if type(child) == Tree:
                    tokens.append(child.label())
                else:  # subtree is a leaf
                    tokens.append(child)
            for token in tokens:
                pairs.append((head, token))
        return pairs

    def attachment_score(self, gold_parse, hypotheses):
        """
        Computes unlabeled attachment score for a set of
        hypothesis parses.
        Unlabeled attachment score: % of tokens with the correct head.

        param nltk.Tree gold_parse: the gold standard parse.
        param list(nltk.Tree) hypotheses: list of hypothesis parses.
        returns: number of correct arcs and number of tokens.
        rtype: tuple(int, int)
        """
        gold_pairs = self._get_head_for_tokens(gold_parse)
        max_correct = 0
        for hyp in hypotheses:
            hyp_pairs = self._get_head_for_tokens(hyp)
            num_correct = len(set(gold_pairs) & set(hyp_pairs))
            if num_correct > max_correct:
                max_correct = num_correct
        return (max_correct, len(gold_pairs))

    @timeout(20)
    def parse(self, sentence):
        """
        Parse the sentence using the trained parser.
        Returns a generator.

        param list sentence: input sentence as a list of words.
        """
        return self._parser.parse(sentence, nltk_tree=True)

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
        import multiprocessing

        def print_results(results_dict):
            """
            param dict results_dict: dictionary of results data with keys:
                                     exact_match, test_data_size,
                                     num_correct_arcs, num_tokens
            """
            print("\n## Results ##")
            # Accuracy
            accuracy_percentage = float(results_dict['exact_match'])/results_dict['test_data_size']
            print("Accuracy: {0}/{1} = {2}"
                  .format(results_dict['exact_match'],
                          results_dict['test_data_size'],
                          accuracy_percentage))
            # Unlabeled Attachment Score (UAS)
            UAS_percentage = float(results_dict['num_correct_arcs'])/results_dict['num_tokens']
            print("UAS: {0}/{1} = {2}"
                  .format(results_dict['num_correct_arcs'],
                          results_dict['num_tokens'],
                          UAS_percentage))

        def write_results(gold_parse, hyps, filename):
            """
            Write gold parse and all hypothesis parses
            out to filename.

            param nltk.Tree gold_parse: the gold standard parse
            param list(nltk.Tree) hyps: list of hypothesis parses
            param str filename: name of out file.
            """
            with open(filename, 'a') as out:
                out.write("GOLD\n{0}\n" .format(gold_parse))
                for parse in hyps:
                    out.write("HYP\n{0}\n" .format(parse))

        def compute_results_data(test_data, results_list, job_num):
            """
            Computes dictionary of results data. Test data can be split
            to parallelize the testing process.

            param list test_data: list of sentence,gold_parse pairs as
                                  returned by _get_test_data.
            param multiprocess.Manager.list results_list: output list 
                                  used for multithreading.
            """
            results = {}
            # Accuracy data
            results['exact_match'] = 0
            results['test_data_size'] = len(test_data)
            # Unlabeled attachment score (UAS) data
            results['num_correct_arcs'] = 0
            results['num_tokens'] = 0
            for (i, (sent, gold_parse)) in enumerate(test_data):
                with open('status{0}.out'.format(job_num), 'a') as out:
                    out.write("{0}/{1}\n" .format(i, len(test_data)))
                hyps = []
                try:
                    hyps = list(self.parse(sent))
                except TimeoutError:
                    pass
                except:
                    print_results(results)
                    return
                # Accuracy calculation
                if gold_parse in hyps:
                    results['exact_match'] += 1
                # UAS calculation
                num_correct_arcs, num_tokens = self.attachment_score(gold_parse, hyps)
                results['num_correct_arcs'] += num_correct_arcs
                results['num_tokens'] += num_tokens
                if hyps:
                    outfile = 'results{0}.out' .format(job_num)
                    write_results(gold_parse, hyps, outfile)
            results_list.append(Counter(results))

        # Multithreaded testing
        data_size = len(self._testing_data)
        arg_list = [self._testing_data[:data_size//3],
                    self._testing_data[data_size//3:(data_size//3)*2],
                    self._testing_data[(data_size//3)*2:]]

        manager = multiprocessing.Manager()
        results_list = manager.list()
        jobs = []
        for i,arg in enumerate(arg_list):
            p = multiprocessing.Process(target=compute_results_data,
                                        args=(arg, results_list, i))
            jobs.append(p)
            p.start()
        for job in jobs:
            job.join()

        results = Counter()
        for result in results_list:
            results += result
        print_results(results)


def CCGDemo():
    print("Building parser...")
    semparser = CCGSemParser("grammars/ccg_grammars/lex.ccg")
    sentence = "I went home"
    print("\nParsing '{0}'...\n" .format(sentence))
    parses = semparser.parse(sentence)
    chart.printCCGDerivation(next(parses))


def DepDemo():
    print("Building parser...")
    semparser = DependencySemParser(train='data/en-ud-train.conllu',
                                    test='data/en-ud-dev.conllu')
    print("Training...")
    semparser.train()
    print("Testing...")
    semparser.test()


if __name__ == '__main__':
    DepDemo()
