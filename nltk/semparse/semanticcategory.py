from __future__ import print_function, unicode_literals

import os
import io
import re
from collections import OrderedDict

from nltk.compat import python_2_unicode_compatible
#from nltk.semparse import rules
import rules ##
from nltk.sem.logic import (Expression, Tokens, Variable,
                            ExistsExpression, LambdaExpression,
                            LogicalExpressionException)


lexpr = Expression.fromstring

# Find the proper data directory.
_DATA_DIR = ""
dirlist = ['nltk/semparse/data', 'data/']
for dir in dirlist:
    if os.path.exists(dir) & os.path.isdir(dir):
        _DATA_DIR = dir
if not _DATA_DIR:
    print("Data directory not found. Searched in {0}".format(dirlist))


@python_2_unicode_compatible
class reDict(dict):
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

    _CandC_MARKEDUP_FILE = os.path.join(_DATA_DIR, 'lib/markedup')

    TYPEMAP = reDict({r'NN$|NNS$': 'TYPE',
            r'NNP.?$|PRP.?$': 'ENTITY',
            r'CC$': 'CONJ',
            r'VB.?$|POS$|IN$|TO$': 'EVENT',
            r'RB.?$|JJ.?$': 'MOD',
            r'CD$': 'COUNT',
            r'WDT$|WP.?$|WRB$': 'ENTQUESTION'})

    TYPES = ['INDEF', 'UNIQUE', 'COMPLEMENT', 'NEGATE', 'TYPE', 'ENTITY',
             'CONJ', 'EVENT', 'COPULA', 'MOD', 'COUNT', 'ENTQUESTION']

    def __init__(self, word, pos, syntactic_category=None, question=False):
        # Special question handling.
        if question:
            self._SPECIAL_CASES_FILE = os.path.join(_DATA_DIR, 'lib/question_specialcases.txt')
            self.rules = rules.question_rules
            self.special_rules = rules.question_special_rules
        else:
            self._SPECIAL_CASES_FILE = os.path.join(_DATA_DIR, 'lib/specialcases.txt')
            self.rules = rules.rules
            self.special_rules = rules.special_rules
        if not os.path.isfile(self._SPECIAL_CASES_FILE):
            raise IOError("No such file or directory: '{0}'".format(self._SPECIAL_CASES_FILE))

        self.word = word
        self.pos = pos
        self.syncat = syntactic_category
        
        special_case = self.getSpecialCase()
        if special_case and special_case in self.TYPES:
            self.semantic_type = special_case
            self._expression = self.generateExpression()
        elif special_case and self.isExpression(special_case):
            self.semantic_type = 'SPECIAL_CASE'
            self._expression = special_case
        else:
            self.semantic_type = self.getSemanticType()
            self._expression = self.generateExpression()

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

    def getExpression(self):
        if len(self.word) == 1:
            word = "_{0}".format(self.word)
        else:
            word = self.word
        word = word.lower()
        expression = unicode(str(self._expression))
        return lexpr(expression.format(word))

    def getBaseExpression(self):
        return self._expression

    def isExpression(self, string):
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
        return

    def generateExpression(self):
        """
        Determines logical predicate for the word given its
        syntactic category and semantic type.

        :param syntactic_category: CCG category for self.word.
        :type syntactic_category: str
        """
        if self.semantic_type in self.special_rules:
            return self.special_rules[self.semantic_type]()
        # TODO: use quantifiers.
        quantifiers = Tokens.EXISTS_LIST + Tokens.ALL_LIST
        if self.word.lower() in quantifiers:
            return None
        if not self.syncat:
            return None

        syncat_parse = self.syncat.parse()
        (pred_vars, arg_var) = self._getVars(syncat_parse)
        stem_expression = self._getStem(pred_vars, arg_var)
        try:
            return self.rules[self.semantic_type](stem_expression)
        except KeyError:
            return None

    def getSemanticType(self):
        """
        Determines semantic type for the given word
        based on it's lemma or POS tag.
        """
        if self.pos in self.TYPEMAP:
            return self.TYPEMAP[self.pos]
        else:
            return None

    def getSpecialCase(self):
        """
        If the word, syntactic category, etc. indicates that
        this is a special case, return the corresponding semantic type
        or lambda expression. Otherwise, return None.
        
        :rtype: str
        """
        with io.open(self._SPECIAL_CASES_FILE, 'rt', encoding='utf-8') as fp:
            for line in fp:
                if line.startswith('\n') or line.startswith('#'):
                    continue
                line = line.strip().split('\t')
                (word_regex, pos_regex, syncat_str, sem) = line
                if re.match(word_regex, self.word) and \
                   re.match(pos_regex, self.pos) and \
                   syncat_str == self.syncat.index_syncat: ##
                    return sem
        return None

    def _getVars(self, syncat_parse):
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
                exprvar = str(SemanticCategory(first_arg, 'NNP', 'N'))
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

    def _getStem(self, predicate_variables, argument_variable):
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
        for (pred, args) in predicate_variables.items():
            lambda_vars.append(pred)
            for arg in reversed(args):
                pred += "({0})".format(arg)    
                if arg != argument_variable and arg not in exists_vars:
                    exists_vars.append(arg)
            sub_expressions.append(lexpr(pred))
        lambda_vars.append(argument_variable)
                
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
