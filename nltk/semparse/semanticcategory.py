from __future__ import unicode_literals

import re
from collections import OrderedDict
from pyparsing import nestedExpr
from nltk.sem.logic import (Expression, Tokens, Variable,
                            ExistsExpression, LambdaExpression)

import rules


lexpr = Expression.fromstring


class reDict(dict):
    """
    Dictionary keyed by regular expressions. Cuts down
    on redundancy when matching e.g. multiple POS tags
    to one function.
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

    TYPEMAP = reDict({r'an?$': 'INDEF',
            r'not$|n\'t$': 'NEGATE',
            r'no$': 'COMPLEMENT',
            r'the$': 'UNIQUE',
            r'NN$|NNS$': 'TYPE',
            r'NNP.?$|PRP.?$': 'ENTITY',
            r'CC$': 'CONJ',
            r'VB.?$|POS$|IN$|TO$': 'EVENT',
            r'RB.?$|JJ.?$': 'MOD',
            r'CD$': 'COUNT',
            r'WDT$|WP.?$|WRB$': 'QUESTION'})

    def __init__(self, word, pos, syntactic_category=None, question=False):
        # Special question handling.
        if question:
            self.rules = rules.question_rules
            self.special_rules = rules.question_special_rules
        else:
            self.rules = rules.rules
            self.special_rules = rules.special_rules

        # Reformat 1-length words so that they don't become VariableExpressions.
        if len(word) == 1:
            self.word = "_{0}".format(word)
        else:
            self.word = word
        self.pos = pos
        self.syntactic_category = syntactic_category
        self.semantic_type = self.getSemanticType()
        self._expression = self.generateExpression()
        if not self._expression:
            raise Exception("No valid expression possible.")

    def __str__(self):
        expression = unicode(str(self._expression))
        word = self.word.lower()
        return expression.format(word)

    def __repr__(self):
        expression = unicode(str(self._expression))
        word = self.word.lower()
        return str(self._expression).format(word)

    def getExpression(self):
        expression = unicode(str(self._expression))
        word = self.word.lower()
        return lexpr(expression.format(word))

    def getBaseExpression(self):
        return self._expression

    def generateExpression(self):
        """
        Determines logical predicate for the word given its
        syntactic category and semantic type.

        :param syntactic_category: CCG category for self.word.
        :type syntactic_category: str
        """
        quantifiers = Tokens.EXISTS_LIST + Tokens.ALL_LIST
        if self.word.lower() in quantifiers:
            return None
        if self.semantic_type in self.special_rules:
            return self.special_rules[self.semantic_type]()
        if not self.syntactic_category:
            print "No syntactic category specified."
            return None

        processed_category = self._preprocessCategory()
        (pred_vars, arg_var) = self._getVars(processed_category)
        stem_expression = self._getStem(pred_vars, arg_var)
        try:
            return self.rules[self.semantic_type](stem_expression)
        except KeyError:
            print "No rule for {0}.".format(self.semantic_type)
            return None

    def getSemanticType(self):
        """
        Determines semantic type for the given word
        based on it's lemma or POS tag.
        """
        special_type = self.isSpecialCase()
        if special_type:
            return special_type
        if self.word in self.TYPEMAP:
            return self.TYPEMAP[self.word]
        elif self.pos in self.TYPEMAP:
            return self.TYPEMAP[self.pos]
        else:
            return None

    def isSpecialCase(self):
        """
        If the word, syntactic category, etc. indicates that
        this is a special case, return the corresponding type.
        Otherwise, return None.
        """
        with open('data/lib/specialcases.txt', 'r') as file:
            for line in file:
                if line.startswith('\n') or line.startswith('#'):
                    continue
                (word_regex, pos_regex, syncat, type) = line.strip().split('\t')
                if re.match(word_regex, self.word) and \
                   re.match(pos_regex, self.pos) and \
                   syncat == self.syntactic_category:
                    return type 
        return None

    def _preprocessCategory(self):
        """
        For self.syntactic_category
        Removes astericks in (it specifies unneeded information). 
        Changes underscore to event variable 'e'.
        Removes bracketed syntactic specifiers, e.g. 'S[dcl]' => 'S'
        """
        processed_category = self.syntactic_category.replace('*', '')
        processed_category = processed_category.replace('_', 'e')
        reBrack = re.compile(r'(?<=\))\{[A-Ze]\}.*?(?=[\\/\)])')
        processed_category = reBrack.sub('', processed_category)
        return processed_category
        
    def _getVars(self, syntactic_category):
        """
        Finds and pairs up the predicate and argument variables
        for the logical expression from the syntactic category.
        Operates by first parsing the category according to it's
        parentheses, and then recursing.

        :param syntactic_category: CCG category for self.word.
        :type syntactic_category: str
        """
        variable_store = ['P', 'Q', 'R', 'S']
        predicate_variables = OrderedDict()
        argument_variable = [] 

        def rhsVars(rhs):
            if type(rhs) == str or type(rhs) == unicode:
                p_var = variable_store.pop(0)
                avars = re.findall(r'\{([A-Ze])\}(?=<\d>)', rhs)
                avars = [var.lower() for var in avars]
                predicate_variables[p_var] = avars
                return
            rhsVars(rhs[0])

        def getVariables(parsed_category):
            if type(parsed_category) == str or type(parsed_category) == unicode:
                p_var = variable_store.pop(0)
                a_vars = re.findall(r'\{([A-Ze])\}', parsed_category)
                if len(a_vars) > 1:
                    a_vars = [var.lower() for var in a_vars]
                    predicate_variables[p_var] = a_vars[1:]
                argument_variable.append(a_vars[0])
                return
            if len(parsed_category) >1:
                rhsVars(parsed_category[-1])
                getVariables(parsed_category[0])
            else:
                getVariables(parsed_category[0])

        bracketParser = nestedExpr('(', ')')
        try:
            parsed_category = bracketParser.parseString(syntactic_category).asList()
        except:
            parsed_category = [syntactic_category]
        getVariables(parsed_category)  # Gets predicate and argument variables.
        return (predicate_variables, argument_variable[0])

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
            for arg in args:
                pred += "({0})".format(arg)    
                if arg != argument_variable:
                    exists_vars.append(arg)
            sub_expressions.append(lexpr(pred))
        lambda_vars.append(argument_variable)
                
        andexpr = reduce(lambda x,y: x & y, sub_expressions)
       
        # Add the exists part.
        existsexpr = andexpr
        for var in reversed(exists_vars):
            existsexpr = ExistsExpression(Variable(var), existsexpr)
                 
        # Add the lambda part.
        lambdaexpr = existsexpr
        for var in reversed(lambda_vars):
            lambdaexpr = LambdaExpression(Variable(var), lambdaexpr)
        
        return lambdaexpr
