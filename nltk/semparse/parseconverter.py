from __future__ import print_function, unicode_literals

import sys
import os
import re
import string
import traceback
from nltk import Tree
from nltk.ccg.lexicon import parseCategory
from nltk.ccg.api import PrimitiveCategory
from nltk.ccg.chart import TypeRaiseRuleSet, DefaultRuleSet

from nltk.semparse.config import _DATA_DIR


class CCGParseConverter(object):
    '''
    Class for converting AUTO string representations of CCG parses into
    nltk.Tree objects identical to the output of nltk.ccg.CCGChartParser.

    Usage: CCGParseConverter(parse_str, combinatory_rules) -> nltk.Tree
        where
            parse_str is of type str and has the format output by
            e.g. easyCCG
            combinatory_rules is e.g. nltk.ccg.chart.DefaultRuleSet
    '''
    def __init__(self):
        self.grammar = set()

    def fromstring(self, tree_str, combinatory_rules):
        parse = self._parse(tree_str)
        tree = self._to_tree(parse, combinatory_rules)
        return tree

    # TODO: _parse does not work. Does not convert to list.
    def _parse(self, tree_str):
        '''
        Parses the string representation of the CCG parse into
        a nested list representing the tree.

        :param tree_str: string representation of the CCG parse tree.
        :type tree_str: str
        :returns: nested list representing CCG parse tree.
        :rtype: list
        '''

        def levelappend(stack, level, arg):
            levelstack = stack
            for i in range(level):
                levelstack = levelstack[-1]
            levelstack.append(arg)

        level = 0
        stack = []
        arg = ""
        closing_brace_found = False
        for i in range(len(tree_str) - 2):
            if tree_str[i:i+2] == '(<':
                closing_brace_found = False
                levelappend(stack, level, [])
                level += 1
            elif tree_str[i] == '>':
                closing_brace_found = True
                arg += tree_str[i]
                levelappend(stack, level, arg.strip())
                arg = ""
            elif tree_str[i] == ')' and closing_brace_found:
                level -= 1
            else:
                arg += tree_str[i]
        return stack.pop()

    def _to_tree(self, parse, combinatory_rules):
        '''
        Converts parse into an nltk.Tree.

        :param parse: nested list representing the parse tree. Output
                      of CCGParseConverter._parse().
        :rtype: nltk.Tree
        '''
        if len(parse) == 0:
            # None tree
            return Tree('', [])
        # Leaf
        if len(parse) == 1:
            (_, cat, pos, _, word, _) = parse[0].split()
            if cat in string.punctuation:
                category = PrimitiveCategory(cat)
            else:
                category = self._make_category(cat, delete=r'[<>]')
            return Tree((category, 'Leaf'), [Tree(category, [(word, pos)])])

        # TODO: Make _to_tree correctly handle type raising.
        # Unary lexical rule.
        if len(parse) == 2:
            (_, new_category, _, _) = parse[0].split()
            new_category = self._make_category(new_category, delete=r'[<>]')
            child = self._to_tree(parse[-1], combinatory_rules)
            return Tree((new_category, 'Lex'), [child])

        # Binary combinatory rule.
        (_, target_category, _, _) = parse[0].split()
        target_category = self._make_category(target_category, delete=r'[<>]')
        lhs = self._to_tree(parse[1], combinatory_rules)
        left_cat = lhs.label()[0]
        rhs = self._to_tree(parse[2], combinatory_rules)
        right_cat = rhs.label()[0]
        # Consider all rules except type raise rules.
        ruleset = set(combinatory_rules).difference(set(TypeRaiseRuleSet))
        for rule in ruleset:
            if rule._combinator.can_combine(left_cat, right_cat):
                res = rule._combinator.combine(left_cat, right_cat).next()
                return Tree((res, str(rule)), [lhs, rhs])
        # No rule works -> grammar rule
        rule = "{0} | {1} | {2}".format(left_cat, right_cat, target_category)
        self.grammar.add(rule)
        return Tree((target_category, 'Grammar'), [lhs, rhs])

    def _make_category(self, category_str, delete=''):
        '''
        delete is a regular expression specifying which substrings
        should be deleted from category_str prior to making
        a category object.
        '''
        category_str = re.sub(delete, '', category_str)
        primitives = self._find_primitives(category_str)
        category = parseCategory(category_str, primitives, [])
        return category

    def _find_primitives(self, category_str):
        temp = re.sub(r'\[.+?\]', '', category_str)
        primitives = list(set(re.sub(r'[\\/\(\)]', ' ', temp).split()))
        return primitives


class CCGBankData(object):
    """
    A generator over the ccgbank data held in directory.
    """

    def __init__(self, directory):
        self.file_idx = 0
        self.content_idx = 0
        self.directory = directory
        self.filenames = self._get_filenames()

    def _get_filenames(self):
        filenames = []
        for root, _, files in os.walk(self.directory):
            for name in files:
                filenames.append(os.path.join(root, name))
        return filenames

    def _next_line(self):
        lines = open(self.filenames[self.file_idx]).readlines()
        line = lines[self.content_idx]
        if self.content_idx == len(lines) - 1:
            self.file_idx += 1
            self.content_idx = 0
        else:
            self.content_idx += 1
        if line.startswith('ID'):
            return self._next_line()
        return line

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        try:
            return self._next_line()
        except:
            raise StopIteration()


def evaluate():
    converter = CCGParseConverter()
    ccgbank_dir = os.path.join(_DATA_DIR, 'test/ccgbank')
    data = CCGBankData(ccgbank_dir)
    total = 0
    converted = 0
    for i, parse in enumerate(data):
        total += 1
        if i % 5 == 0:
            sys.stderr.write('{0}/48934\r'.format(i))
        try:
            tree = converter.fromstring(parse, DefaultRuleSet)
            converted += 1
        except:
            with open('bad_parses.txt', 'a') as out:
                out.write(parse + '\n--------\n')
                out.write(str(traceback.format_exc()))
                out.write('\n\n')
    with open('data/grammars/ccg_grammar.txt', 'w') as out:
        for rule in converter.grammar:
            out.write(rule + '\n')
    print("{0}/{1} parses converted".format(converted, total))

def test_sent(auto_str):
    converter = CCGParseConverter()
    tree = converter.fromstring(auto_str, DefaultRuleSet)
    return tree


if __name__ == '__main__':
    print("Converting CCGBank data")
    print("-----------------------")
    evaluate()
