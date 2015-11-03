from __future__ import print_function, unicode_literals

import io
import sys
import os
import re

from collections import OrderedDict

from nltk.compat import python_2_unicode_compatible
from nltk.sem.logic import (Expression, Tokens, Variable,
                            ExistsExpression, LambdaExpression,
                            LogicalExpressionException)

from nltk.semparse import rules
from nltk.semparse.syntacticcategory import SyntacticCategory
from nltk.semparse.config import (_DATA_DIR, _LANGUAGE_FILE)


lexpr = Expression.fromstring

TYPES = ['INDEF', 'UNIQUE', 'COMPLEMENT', 'NEGATE', 'TYPE', 'ENTITY',
         'CONJ', 'EVENT', 'COPULA', 'MOD', 'COUNT', 'ENTQUESTION']


@python_2_unicode_compatible
class redict(dict):
    """
    Dictionary keyed by regular expressions. Cuts down
    on redundancy when matching e.g. multiple POS tags
    to one semantic type.
    """
    def __init__(self, arg):
        dict.__init__(self, arg)

    def __getitem__(self, key):
        try:
            rekey = [k for k in self.keys() if re.match(k, key)][0]
        except:
            raise KeyError
        return dict.__getitem__(self, rekey)

    def __contains__(self, key):
        if [k for k in self.keys() if re.match(k, key)]:
            return True
        return False


class SemanticCategory(object):

    posmap_cache = None

    @classmethod
    def read_pos_map(cls):
        """
        Reads _DATA_DIR/lib/<language>_pos.txt into an redict
        object.
        """
        if cls.posmap_cache:
            return cls.posmap_cache

        # TODO: make language variable.
        pos_file = os.path.join(_DATA_DIR, 'lib/english_pos.txt')
        pos_map = []
        with open(pos_file, 'r') as fp:
            for line in fp:
                if line.startswith('#'):
                    continue
                if line == '\n':
                    continue
                (pos_regex, semtype) = line.split()
                pos_regex = pos_regex.strip()
                semtype = semtype.strip()
                pos_map.append((pos_regex, semtype))
        cls.posmap_cache = redict(pos_map)
        return redict(pos_map)

    def __init__(self, word, pos, syntactic_category, question=False):
        self.POSMAP = self.read_pos_map()
        self.word = word
        self.pos = pos
        self.syncat = syntactic_category

        # Special question handling.
        if question:
            self.rules = rules.question_rules
            self.special_rules = rules.question_special_rules
        else:
            self.rules = rules.rules
            self.special_rules = rules.special_rules

    # TODO: figure out unicode() for Python3 compatibility.
    def __str__(self):
        if len(self.word) == 1:
            word = "_{0}".format(self.word)
        else:
            word = self.word
        word = word.lower()
        expression = unicode(str(self._expression))
        return expression.format(word)

    def __repr__(self):
        if len(self.word) == 1:
            word = "_{0}".format(self.word)
        else:
            word = self.word
        word = word.lower()
        expression = unicode(str(self._expression))
        return expression.format(word)

    def get_expression(self):
        if len(self.word) == 1:
            word = "_{0}".format(self.word)
        else:
            word = self.word
        word = word.lower()
        expression = unicode(str(self._expression))
        return lexpr(expression.format(word))

    def get_base_expression(self):
        return self._expression

    # TODO: clean up generate_expression
    def generate_expression(self):
        """
        Determines logical predicate for the word given its
        syntactic category and semantic type.
        """
        quantifiers = Tokens.EXISTS_LIST + Tokens.ALL_LIST
        if self.semantic_type in self.special_rules:
            self._expression = self.special_rules[self.semantic_type]()
        # TODO: use quantifiers.
        elif self.word.lower() in quantifiers:
            self._expression = None
        # TODO: generate indexed syncat when markedup fails
        elif not self.syncat.index_syncat:
            self._expression = None

        else:
            syncat_parse = self.syncat.parse()
            (pred_vars, arg_var) = self._get_vars(syncat_parse)
            if not pred_vars:
                self._expression = None
            stem = self._get_stem(pred_vars, arg_var)
            try:
                self._expression = self.rules[self.semantic_type](stem)
            except KeyError:
                self._expression = None

    def set_semantic_type(self):
        """
        Determines semantic type for the given word
        based on it's lemma or POS tag.
        """
        if self.pos in self.POSMAP:
            self.semantic_type = self.POSMAP[self.pos]
        else:
            self.semantic_type = None

    def _get_vars(self, syncat_parse):
        """
        Finds and pairs up the predicate and argument variables
        for the logical expression from the syntactic category.
        Operates by first parsing the category according to it's
        parentheses, and then recursively pairing predicate variables
        with their arguments.

        Returns an OrderedDict of predicate variables with their
        argument variables, and the individual variable.

        :param index_syncat: indexed syntactic category
        :type index_syncat: str
        :rtype: tuple(OrderedDict, char)
        """
        variable_store = ['P', 'Q', 'R', 'S']
        predicate_variables = OrderedDict()
        individual_variable = []

        def getArgs(tree):
            if isinstance(tree, list):
                first_arg = getArgs(tree[1])[0]
                sc = SyntacticCategory('N')
                semcat = SemanticCategory(first_arg, 'NNP', sc)
                semcat.set_semantic_type()
                semcat.generate_expression()
                exprvar = str(semcat)
                exprvar = exprvar.replace('_'+first_arg, first_arg)
                return getArgs(tree[0]) + [exprvar]
            else:
                var = re.findall(r'\{([A-Ze])\}', tree)[0]
                return [var.lower()]

        def getVars(tree):
            if isinstance(tree, list):
                var = variable_store.pop(0)
                predicate_variables[var] = getArgs(tree[1])
                getVars(tree[0])
            else:
                var = re.findall(r'\{([A-Ze])\}', tree)[0]
                individual_variable.append(var.lower())

        getVars(syncat_parse[0])
        return (predicate_variables, individual_variable[0])

    def _get_stem(self, predicate_variables, argument_variable):
        """
        Builds the stem expression. i.e. the expression without
        semantic type specific information.

        :param predicate_variables: lambda predicate variables paired with
            their argument variables.
        :type predicate_variables: dict(str: list(str))
        :param argument_variable: lambda argument variable.
        :type argument_variable: str
        """
        sub_expressions = []
        exists_vars = []
        lambda_vars = []

        if self.semantic_type == 'EVENT' and argument_variable != 'e':
            argument_variable = 'e'

        for (pred, args) in predicate_variables.items():
            lambda_vars.append(pred)
            for arg in reversed(args):
                pred += "({0})".format(arg)
                if arg != argument_variable and arg not in exists_vars:
                    exists_vars.append(arg)
            sub_expressions.append(lexpr(pred))
        lambda_vars.append(argument_variable)

        if not sub_expressions:
            return None
        # Just the expression without lambdas or quantifiers.
        andexpr = sub_expressions[0]
        for i in range(1, len(sub_expressions)):
            andexpr = andexpr & sub_expressions[i]

        # Add the exists part.
        existsexpr = andexpr
        for var in reversed(exists_vars):
            # This is the case in which Q(\x.EQUAL(x,z))(y).
            if len(var) > 1:
                continue
            existsexpr = ExistsExpression(Variable(var), existsexpr)

        # Add the lambda part.
        lambdaexpr = existsexpr
        for var in reversed(lambda_vars):
            lambdaexpr = LambdaExpression(Variable(var), lambdaexpr)

        return lambdaexpr


# ////////////////////////////////////////////
# //           Helper functions             //
# ////////////////////////////////////////////

def get_special_cases(word, pos, syncat):
    """
    Returns all possible semantic types/logical expressions for input
    word, POS tag, and syntactic category. Returns an empty list if
    no special cases found.

    :param word: input word
    :param pos: POS tag for input word
    :param syncat: syntactic category
    :rtype: list
    """
    lines = io.open(_LANGUAGE_FILE, 'rt', encoding='utf-8').readlines()
    lines = [line for line in lines
             if line != '\n' and not line.startswith('#')]
    # Sort lines by priority field.
    lines = sorted(lines, key=lambda l: int(l.split()[0]))

    cases = []
    for line in lines:
        line = line.strip().split('\t')
        (_, word_regex, pos_regex, syncat_str, sem) = line
        if syncat_str == '.*$':
            syncat_match = True
        else:
            syncat_match = syncat_str == syncat.index_syncat
        if re.match(word_regex, word) and \
           re.match(pos_regex, pos) and \
           syncat_match:
            cases.append(sem)
    return cases


def get_semantic_categories(word, pos, syncat, question=False):
    """
    Returns a list of SemanticCategory objects, one for each
    possible semantics for the input word, POS tag and syntactic
    category.

    :param word: input word
    :type word: str
    :param pos: POS tag for word
    :type pos: str
    :param syncat: syntactic category for word and POS tag
    :type syncat: nltk.semparse.SyntacticCategory
    :param question: whether the word appears in a question
                     sentence or not.
    :type question: bool
    :returns: all possible semantic categories for the input
    :rtype: list(SemanticCategory)
    """
    expressions = []

    # Add any special cases.
    special_cases = get_special_cases(word, pos, syncat)
    if special_cases:
        for case in special_cases:
            semcat = SemanticCategory(word, pos, syncat, question)
            if case in TYPES:
                semcat.semantic_type = case
                semcat.generate_expression()
            elif is_expression(case):
                semcat.semantic_type = 'SPECIAL_CASE'
                semcat._expression = case
            else:
                raise Exception("Invalid specification '{0}' in file '{1}'"
                                .format(case, _LANGUAGE_FILE))
            expressions.append(semcat)

    # Add normal cases.
    semcat = SemanticCategory(word, pos, syncat, question)
    semcat.set_semantic_type()
    semcat.generate_expression()
    expressions.append(semcat)
    return expressions


def is_expression(string):
    """
    Determines if string is a valid Expression.
    :param string: expression string, e.g. '\\x.cool(x)'
    :type string: str
    :rtype: bool
    """
    try:
        lexpr(string)
        return True
    except LogicalExpressionException:
        return False
