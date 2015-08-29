from __future__ import print_function, unicode_literals

import re
from nltk import Tree
from nltk.ccg.lexicon import parseCategory

class CCGParseConverter(object):
    '''
    Class for converting string representations of CCG parses into 
    nltk.Tree objects identical to the output of nltk.ccg.CCGChartParser.

    Usage: CCGParseConverter(parse_str, combinatory_rules) -> nltk.Tree
        where
            parse_str is of type str and has the format output by
            e.g. easyCCG
            combinatory_rules is e.g. nltk.ccg.chart.DefaultRuleSet
    '''
    def __init__(self):
        pass

    def fromstring(self, tree_str, combinatory_rules):
        parse = self._parse(tree_str)[0]
        tree = self._toTree(parse, combinatory_rules)
        return tree

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
        for i in range(len(tree_str) - 2):
            if tree_str[i:i+2] == '(<':
                levelappend(stack, level, [])
                level += 1
            elif tree_str[i] == '>':
                arg += tree_str[i]
                levelappend(stack, level, arg.strip())
                arg = ""
            elif tree_str[i] == ')' and tree_str[i-1] == '>':
                level -= 1
            else:
                arg += tree_str[i]
        return stack

    def _toTree(self, parse, combinatory_rules):
        '''
        Converts parse into an nltk.Tree.

        :param parse: nested list representing the parse tree. Output
                      of CCGParseConverter._parse().
        :rtype: nltk.Tree
        '''
        # Leaf
        if len(parse) == 1:
            (_,_,_,_, word, cat) = parse[0].split()
            category = self._makeCategory(cat)
            return Tree((category, 'Leaf'), [Tree(category, [word])])

        # Unary lexical rule.
        if len(parse) == 2:
            (_, new_category, _, _) = parse[0].split()
            new_category = self._makeCategory(new_category)
            child = self._toTree(parse[-1], combinatory_rules)
            return Tree((new_category, 'Lex'), [child])

        # Binary combinatory rule.
        (_, target_category, _, _) = parse[0].split()
        target_category = self._makeCategory(target_category)
        lhs = self._toTree(parse[1], combinatory_rules)
        left_cat = lhs.label()[0]
        rhs = self._toTree(parse[2], combinatory_rules)
        right_cat = rhs.label()[0]
        for rule in combinatory_rules:
            if rule._combinator.can_combine(left_cat, right_cat):
                res = rule._combinator.combine(left_cat, right_cat).next()
                if res == target_category:
                    return Tree((res, rule.__str__()), [lhs, rhs])

    def _makeCategory(self, category_str):
        category_str = re.sub(r'[<>]', '', category_str)
        primitives = self._findPrimitives(category_str)
        category = parseCategory(category_str, primitives, [])
        return category

    def _findPrimitives(self, category_str):
        temp = re.sub(r'\[.+?\]', '', category_str)
        primitives = list(set(re.sub(r'[\\/\(\)]', ' ', temp).split()))
        return primitives
