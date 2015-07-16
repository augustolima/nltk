import re
from collections import OrderedDict
from pyparsing import nestedExpr

import rules

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
        self.semantic_type = self.getSemanticType()
        self._expression = self.generateExpression(syntactic_category)
        if not self._expression:
            raise Exception("No valid expression possible. {0} {1} {2}"
                            .format(word, syntactic_category, self.semantic_type))

    def __str__(self):
        return self._expression.format(self.word)

    def __repr__(self):
        return self._expression.format(self.word)

    def getExpression(self):
        return self._expression.format(self.word)

    def getBaseExpression(self):
        return self._expression

    def generateExpression(self, syntactic_category):
        """
        Determines logical predicate for the word given its
        syntactic category and semantic type.

        :param syntactic_category: CCG category for self.word.
        :type syntactic_category: str
        """
        if self.semantic_type in self.special_rules:
            return self.special_rules[self.semantic_type]()
        if not syntactic_category:
            return None

        processed_category = self._preprocessCategory(syntactic_category)
        (pred_vars, arg_var) = self._getVars(processed_category)
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
        MAP = reDict({r'an?$': 'INDEF',
                r'be$|is$|was$|am$|are$': 'COPULA',
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

        if self.word in MAP:
            return MAP[self.word]
        elif self.pos in MAP:
            return MAP[self.pos]
        else:
            return None

    def _preprocessCategory(self, syntactic_category):
        """
        Removes astericks in category (it specifies unneeded information). 
        Changes underscore to event variable 'e'.
        Removes bracketed syntactic specifiers, e.g. 'S[dcl]' => 'S'

        :param syntactic_category: CCG category for self.word.
        :type syntactic_category: str
        """
        processed_category = syntactic_category.replace('*', '')
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
        predicate_variables = {}
        argument_variable = [] 

        def rhsVars(rhs):
            if type(rhs) == str or type(rhs) == unicode:
                p_var = variable_store.pop(0)
                a_var = re.findall(r'\{([A-Ze])\}', rhs)[-1].lower()
                predicate_variables[p_var] = a_var
                return
            rhsVars(rhs[0])

        def getVariables(parsed_category):
            if type(parsed_category) == str or type(parsed_category) == unicode:
                p_var = variable_store.pop(0)
                a_vars = re.findall(r'\{([A-Ze])\}', parsed_category)
                if len(a_vars) > 1:
                    a_vars = [var.lower() for var in a_vars]
                    predicate_variables[p_var] = a_vars[-1]
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
        # Add the lambdas.
        stem = r''
        for var in predicate_variables.keys():
            stem += "\\{0} ".format(var)
        stem += "\\{0}. ".format(argument_variable)

        # Add the exists variables, if they exist.
        exists = ""
        args = list(OrderedDict.fromkeys(predicate_variables.values()))
        for arg in args:
            if arg != argument_variable:
                if not exists:
                    exists += "exists {0}".format(arg)
                else:
                    exists += " {0}".format(arg)
        if exists:
            stem += exists + '.'
        stem += '('

        # Add the predicate variables and their arguments.
        for (i, (pred,args)) in enumerate(predicate_variables.items()):
            for arg in args:
                stem += "{0}({1})".format(pred, arg)
                if i+1 != len(predicate_variables):
                    stem += " & "
        return stem
