from __future__ import print_function, unicode_literals

import re
from nltk import Tree
from nltk.sem.logic import Variable, Expression, ApplicationExpression

from nltk.semparse import SyntacticCategory, get_semantic_categories

# ==============================
# The main semantic parsing algorithm
# build_expressions. Takes as input a CCG parse
# as an nltk.Tree and outputs a logic form.
# ==============================


lexpr = Expression.fromstring


class SemanticComposer(object):

    def __init__(self, syncat_dict):
        # syncat_dict is the parsed C&C markedup file. 
        self._syncat_dict = syncat_dict

    def build_expressions(self, tree, pos_tags, question=False):
        """
        The main semantic composition algorithm.

        :param tree: input CCG parse
        :type tree: nltk.Tree
        :param pos_tags: POS tags for words in input sentence.
        :type pos_tags: list(tuple(str, str))
        :rtype: list(nltk.sem.logic.Expression)
        """
        children = self.get_children(tree)

        # Leaf
        if len(children) == 0:
            word = tree[0]
            if isinstance(word, tuple):
                word = word[0]
            pos = dict(pos_tags)[word]
            syncat_str = str(tree.label())
            if '(' in syncat_str:  # Get rid of extra parentheses.
                syncat_str = re.findall(r'\((.*)\)', syncat_str)[0]
            syncat = SyntacticCategory(syncat_str, self._syncat_dict)
            semcats = get_semantic_categories(word, pos, syncat, question)
            expressions = [semcat.get_expression() for semcat in semcats]
            expressions = [Tree((expr, 'Leaf'), [word]) for expr in expressions]
            return expressions

        # Unary rule
        if len(children) == 1:
            derivations = self.build_expressions(children[0], pos_tags, question)
            return derivations

        derivations = []
        rule = tree.label()[1]
        left_exprs = self.build_expressions(children[0], pos_tags, question)
        right_exprs = self.build_expressions(children[1], pos_tags, question)
        for left in left_exprs:
            for right in right_exprs:
                if isinstance(left, Tree):
                    lexpr = left.label()[0]
                else:
                    lexpr = left
                if isinstance(right, Tree):
                    rexpr = right.label()[0]
                else:
                    rexpr = right
                expr = self.apply_rule(lexpr, rexpr, rule)
                derivation = Tree((expr, rule), [left, right])
                derivations.append(derivation)
        return derivations

    def get_children(self, tree):
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

    def apply_rule(self, left_ex, right_ex, rule):
        """
        Passes left_ex and right_ex to the correct rule application
        function.

        :param left_ex, right_ex: input expressions
        :type left_ex, right_ex: nltk.sem.logic.Expression
        :param rule: CCG combinatory rule as specified by the CCG parse.
        :type rule: str
        :rtype: nltk.sem.logic.Expression
        """
        if left_ex.__str__() == 'None':
            return right_ex
        if right_ex.__str__() == 'None':
            return left_ex

        if rule == '>':  # Forward application
            return ApplicationExpression(left_ex, right_ex).simplify()
        if rule == '<':  # Backward application
            return ApplicationExpression(right_ex, left_ex).simplify()
        if '>S' in rule:  # Forward substitution
            return self.substitute(left_ex, right_ex)
        if '<S' in rule:  # Backward substitution
            return self.substitute(right_ex, left_ex)
        if '>B' in rule:  # Forward composition
            return self.compose(left_ex, right_ex)
        if '<B' in rule:  # Backward composition
            return self.compose(right_ex, left_ex)
        raise Exception("Unknown rule: {0}".format(rule))

    # TODO: complete typeraise function.
    def typeraise(self, expression, ccg_op):
        """
        Typeraises expression.

        :param expression: expression to typeraise.
        :type expression: nltk.sem.logic.Expression
        :param ccg_op: ccg_op specifying the direction of the type-raise.
        :type ccg_op: str ('>T' or '<T')
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
        first = ApplicationExpression(expr2, lexpr('C')).simplify()
        sec = ApplicationExpression(expr1, first).simplify()
        string = sec.__str__()
        try:
            first_var = re.match(r'\\.*?([a-z])[a-z]*?\.', string).group(1)
            index = string.index(first_var)
            newstring = string[:index] + 'C ' + string[index:]
        # Regex did not match. No lambdas in expression.
        except AttributeError:
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
        first = ApplicationExpression(expr1, lexpr('S'))
        sec = ApplicationExpression(first, expr2).simplify()
        string = sec.__str__()
        try:
            first_var = re.match(r'\\.*?([a-z])[a-z]*?\.', string).group(1)
            index = string.index(first_var)
            newstring = string[:index] + 'S ' + string[index:]
        # Regex did not match. No lambdas in expression.
        except AttributeError:
            newstring = '\\S. ' + string
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
        >>> resolved_expr
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
