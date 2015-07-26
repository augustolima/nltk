from __future__ import unicode_literals

import re
from collections import OrderedDict

from nltk.sem.logic import (is_eventvar, is_indvar, Expression,
                            LambdaExpression, ExistsExpression,
                            AndExpression, ApplicationExpression,
                            IndividualVariableExpression,
                            FunctionVariableExpression)

# =========================================
# Rules for translating words/phrases into
# Neo-Davidsonian logic forms as described
# in Reddy et. al. 2014.
# =========================================

lexpr = Expression.fromstring

def findVariables(expression):
    ''' Returns all bound variables.'''
    def helper(expression):
        if isinstance(expression, LambdaExpression) or isinstance(expression, ExistsExpression): 
            return findVariables(expression.term)
        if isinstance(expression, AndExpression): 
            return findVariables(expression.second) + findVariables(expression.first)
        if isinstance(expression, ApplicationExpression): 
            return findVariables(expression.function) + [expression.argument] 
        if isinstance(expression, IndividualVariableExpression): 
            return [expression.variable]
        if isinstance(expression, FunctionVariableExpression): 
            return []
    vars = helper(expression)
    # Removes duplicates while keeping order.
    return list(OrderedDict.fromkeys(vars))

def getIndVar(stem):
    '''Returns independent variable, e.g. \\e or \\x'''
    ivar = None
    while not ivar:
        v = str(stem.variable)
        if is_eventvar(v) or is_indvar(v):
            ivar = stem.variable
        stem = stem.term 
    return ivar

def getAndExpr(stem):
    '''Returns just the AND expression of stem.
       e.g. \P Q x.(P(x) & Q(x) => (P(x) & Q(x))'''
    while type(stem) == LambdaExpression or type(stem) == ExistsExpression:
        stem = stem.term 
    return stem


# =========================
#        POS Rules        
# =========================

# VB*, IN, TO, POS
def event(stem):
    evar = getIndVar(stem)  # Event variable.
    andexpr = getAndExpr(stem)
    for (i,var) in enumerate(findVariables(andexpr)):
        string = "{0}:{1}({2})({3})".format('{0}', i+1, evar, var)
        andexpr = AndExpression(andexpr, lexpr(string))
    lambda_bit = re.split(r'\.(?!.*\..*)', str(stem))[0] + '.'
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)

# RB*, JJ*
def mod(stem):
    arg = getIndVar(stem)
    andexpr = getAndExpr(stem)
    string = "{0}({1})".format('{0}', arg)
    andexpr = AndExpression(andexpr, lexpr(string))
    lambda_bit = re.split(r'\.(?!.*\..*)', str(stem))[0] + '.'
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)

# CD
def count(stem):
    arg = getIndVar(stem)
    andexpr = getAndExpr(stem)
    string = "COUNT({0}, {1})".format(arg, '{0}')
    andexpr = AndExpression(andexpr, lexpr(string))
    lambda_bit = re.split(r'\.(?!.*\..*)', str(stem))[0] + '.'
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)



# =========================
#        Word Rules       
# =========================

# not, n't
def negate(stem):
    arg = getIndVar(stem)
    andexpr = getAndExpr(stem)
    andexpr = AndExpression(andexpr, lexpr("NEGATION({0})".format(arg)))
    lambda_bit = re.split(r'\.(?!.*\..*)', str(stem))[0] + '.'
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)

# no
def complement(stem):
    arg = getIndVar(stem)
    andexpr = getAndExpr(stem)
    andexpr = AndExpression(andexpr, lexpr("COMPLEMENT({0})".format(arg)))
    lambda_bit = re.split(r'\.(?!.*\..*)', str(stem))[0] + '.'
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)

# definite articles
def unique(stem):
    arg = getIndVar(stem)
    andexpr = getAndExpr(stem)
    andexpr = AndExpression(andexpr, lexpr("UNIQUE({0})".format(arg)))
    lambda_bit = re.split(r'\.(?!.*\..*)', str(stem))[0] + '.'
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)


# =========================
#      Special Cases      
# =========================

# indefinite articles
def indef():
    return lexpr("None")

# copula
def copula():
    return lexpr(r'\P Q y.exists x.(Q(x) & P(x))')

# NN, NNS
def kind():
    return lexpr(r'\x.({0}(x))')

# NNP*, PRP*
def entity():
    return lexpr(r'\x.(EQUAL(x, {0}))')

# CC
def conj():
    return lexpr(r'\P Q x.(P(x) & Q(x))')


# =========================
#        Questions        
# =========================

# copula
def qcopula():
    return lexpr(r'\P \x.(P(x))')

# WDT, WP*, WRB
# Want the TARGET to be the subject. If we're asked a questions like,
# "What river runs through Texas?"
def oldquestion(stem):
    andexpr = getAndExpr(stem)
    subjarg = findVariables(stem)[0]
    andexpr = AndExpression(andexpr, lexpr("TARGET({0})".format(subjarg)))
    lambda_bit = re.split(r'\.(?!.*\..*)', str(stem))[0] + '.'
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)

def question():
    return lexpr(r'\P x. (P(x) & TARGET(x))')


# =========================
#         Mappings        
# =========================

# TODO: implement CLOSED type.
rules = {
        'NEGATE': negate,
        'COMPLEMENT': complement,
        'UNIQUE': unique,
        'EVENT': event,
        'MOD': mod,
        'COUNT': count,
#        'CLOSED': closed  not implemented.
        }

special_rules = {
        'INDEF': indef,
        'COPULA': copula,
        'TYPE': kind,
        'ENTITY': entity,
        'CONJ': conj
      }

question_rules = {
        'NEGATE': negate,
        'COMPLEMENT': complement,
        'UNIQUE': unique,
        'EVENT': event,
        'MOD': mod,
        'COUNT': count,
        }

question_special_rules = {
        'INDEF': indef,
        'COPULA': qcopula,
        'TYPE': kind,
        'ENTITY': entity,
        'CONJ': conj,
        'QUESTION': question
      }
