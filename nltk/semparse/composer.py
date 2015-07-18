from __future__ import unicode_literals

import re
from collections import namedtuple
from nltk.sem.logic import Variable, Expression, ApplicationExpression

# ==============================
# The main semantic parsing algorithm
# buildExpressions. Takes as input a CCG parse
# as an nltk.Tree and outputs a logic form.
# ==============================


lexpr = Expression.fromstring
MR = namedtuple('MR', 'expression, derivation') 

class SemanticComposer(object):

    def __init__(self, predicateLexicon):
        """
        :param predicateLexicon: predicate lexicon to use.
        :type predicateLexicon: nltk.semparse.PredicateLexicon
        """
        self.predLex = predicateLexicon

    def buildExpressions(self, tree):
        """
        The main semantic composition algorithm.

        :param tree: input CCG parse
        :type tree: nltk.Tree
        :rtype: list(nltk.sem.logic.Expression)
        """
        expressions = []
        children = self.getChildren(tree)

        # Leaf
        if len(children) == 0:
            cat = str(tree.label())
            if '(' in cat:  # Get rid of extra parentheses.
                cat = re.findall(r'\((.*)\)', cat)[0]
            preds = self.predLex.get((tree[0], cat)) 
            return [MR(pred, []) for pred in preds]

        # Unary rule
        if len(children) == 1:
            return self.buildExpressions(children[0])

        # Binary rule
        rule = tree.label()[1]
        for left_ex in self.buildExpressions(children[0]):
            for right_ex in self.buildExpressions(children[1]):
                expr = self.applyRule(left_ex.expression, right_ex.expression, rule)
                if self.check(expr):
                    string = "* {0} {1} {2}\n\t==> {3}" \
                              .format(left_ex.expression, rule, right_ex.expression, expr)
                    derivation = left_ex.derivation + right_ex.derivation
                    derivation.append(string)
                    expressions.append( MR(expr, derivation) )

        return expressions

    def getChildren(self, tree):
        """
        Gets all child nodes from tree.

        :param tree: tree for which to find children.
        :type tree: nltk.Tree
        """
        subtrees = list(tree.subtrees())
        children = []
        i = 1
        while i < len(subtrees):
                children.append(subtrees[i])
                subsubtrees = list(subtrees[i].subtrees())
                i = i + len(subsubtrees)
        return children

    def check(self, expression):
        """
        Checks if expression is valid.

        :param expression: logical expression to check.
        :type expression: nltk.sem.logic.Expression
        :rtype: bool
        """
        if not expression:
            return False
        # Check for misplaced lambda expressions.
        if re.findall(r'[a-zA-Z]+?(?::[0-9])?\([^a-z]', expression.__str__()):
            return False
        try:
            lexpr(expression.__str__())
            return True
        except:
            return False

    def applyRule(self, left_ex, right_ex, rule):
        """
        Passes left_ex and right_ex to the correct rule application
        function.

        :param left_ex, right_ex: input expressions
        :type left_ex, right_ex: nltk.sem.logic.Expression
        :param rule: CCG combinatory rule as specified by the CCG parse.
        :type rule: str
        :rtype: nltk.sem.logic.Expression
        """
        if left_ex.__str__() == 'None': return right_ex
        if right_ex.__str__() == 'None': return left_ex

        if rule == '>':  # Forward application
            return ApplicationExpression(left_ex, right_ex).simplify() 
        if rule == '<':  # Backward application
            return ApplicationExpression(right_ex, left_ex).simplify()
        if rule == '>Sx':  # Forward substitution
            return self.substitute(left_ex, right_ex)
        if rule == '<Sx':  # Backward substitution
            return self.substitute(right_ex, left_ex)
        if rule == '>B':  # Forward composition
            return self.compose(left_ex, right_ex)
        if rule == '<B':  # Backward composition
            return self.compose(right_ex, left_ex)
        raise Exception("Bad rule: {0}".format(rule))

    # TODO: complete typeraise function.
    def typeraise(self, expression):
        """
        Typeraises expression.

        :param expression: expression to typeraise.
        :type expression: nltk.sem.logic.Expression
        :rtype: nltk.sem.logic.Expression
        """
        pass

    def compose(self, expr1, expr2):
        """
        Performs the functional composition of 
        expr1 and expr2.

        :param expr1 expr2: input expressions
        :type expr1, expr2: nltk.sem.logic.Expression 
        :rtype: nltk.sem.logic.Expression
        """
        first = ApplicationExpression(expr1, lexpr('C')).simplify()
        sec = ApplicationExpression(first, expr2).simplify()
        string = sec.__str__() 
        try:
            first_var = re.match(r'\\.*?([a-z])[a-z]*?\.', string).group(1)
            index = string.index(first_var)
            newstring = string[:index] + 'C ' + string[index:]
        except AttributeError:  # Regex did not match. No lambdas in expression.
            newstring = '\\C. ' + string
        return lexpr(newstring)

    # TODO: check/fix substitute function.
    def substitute(self, expr1, expr2):
        """
        Performs the substitute operation of expr1 and expr2

        :param expr1 expr2: input expressions
        :type expr1, expr2: nltk.sem.logic.Expression 
        :rtype: nltk.sem.logic.Expression
        """
        first = ApplicationExpression(expr2, lexpr('S'))
        sec = ApplicationExpression(expr1, first).simplify()
        newstring = '\\S ' + sec.__str__()
        return lexpr(newstring)

    # TODO: fix resolve function.
    def resolve(expression):
        """
        Does not currently work for all expressions.
        Resovles all subexpressions of the form \\x. EQUAL(x, 'Word')
        into constant expressions and substitutes them for the variable
        assigned to them.

        >>> expr = lexpr('\\e.exists y z.(ran1(e,y) & ran2(e,z) \
                          & EQUAL(y,reagan) & UNIQUE(z) & EQUAL(z,us))')
        >>> resolved_expr = resolve_equalities(expr)
        >>> print resolved_expr
        \\e.(ran1(e,reagan) & ran2(e,us) & UNIQUE(us))
        """
        mr_string = expression.__str__()
        if 'EQUAL' not in mr_string:
            return expression

        reEqual = re.compile(r'(?<=EQUAL\()_?[a-z],_?[a-z]+(?=\))')
        reDel = re.compile(r'EQUAL\(.*?\)(?: &)? | (?:& )?EQUAL\(.*?\)')
        reExists = re.compile(r'.*\.?exists (?:([a-z])\s)*([a-z])\.')

        # Find the variables to replace.
        replacements = reEqual.findall(mr_string)
        replacements = set([tuple(r.split(',')) for r in replacements])

        # Delete the EQUAL subexpression.
        mr_string = reDel.sub('', mr_string)

        # Find all variables x s.t. exists x
        exist_vars = reExists.match(mr_string).groups()
        exist_vars = [var for var in exist_vars if var]  # Filter out None's
        
        # If we're replacing every variable x s.t. exists x,
        # delete the whole exists part of the expression.
        if len(exist_vars) == len(replacements):
            mr_string = re.sub(r'exists.*?\.', '', mr_string)
            expr = lexpr(mr_string)
            for (var, word) in replacements:
                expr = expr.replace(Variable(var), lexpr(word))
        else:
            for (var, word) in replacements:
                mr_string = mr_string.replace(var, '', 1)
                temp = lexpr(mr_string).replace(Variable(var), lexpr(word))
                mr_string = temp.__str__()
            expr = lexpr(mr_string)

        return expr
