from __future__ import unicode_literals

import re
from collections import OrderedDict

from nltk.sem.logic import (is_eventvar, is_indvar, Variable, Expression,
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
        if isinstance(expression, LambdaExpression) or \
           isinstance(expression, ExistsExpression): 
            return findVariables(expression.term)
        if isinstance(expression, AndExpression): 
            return findVariables(expression.second) + \
                   findVariables(expression.first)
        if isinstance(expression, ApplicationExpression): 
            return findVariables(expression.function) + [expression.argument]
        if isinstance(expression, IndividualVariableExpression): 
            return [expression.variable]
        if isinstance(expression, FunctionVariableExpression): 
            return []
    vars = helper(expression)
    # Removes duplicates while keeping order.
    vars = list(OrderedDict.fromkeys(vars))
    vars = [var for var in vars if isinstance(var, IndividualVariableExpression)]
    return vars

def getIndVar(stem):
    '''Returns individual or event variable, e.g. \\e or \\x'''
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
    reLambda = re.compile(re.escape(str(andexpr)))
    lambda_bit = reLambda.split(str(stem))[0]
    for (i,var) in enumerate(findVariables(andexpr)):
        string = "{0}:{1}({2})({3})".format('{0}', i+1, evar, var)
        andexpr = AndExpression(andexpr, lexpr(string))
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)

# RB*, JJ*
def mod(stem):
    ivar = getIndVar(stem)
    andexpr = getAndExpr(stem)
    reLambda = re.compile(re.escape(str(andexpr)))
    string = "{0}({1})".format('{0}', ivar)
    andexpr = AndExpression(andexpr, lexpr(string))
    lambda_bit = reLambda.split(str(stem))[0]
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)

# CD
def count(stem):
    ivar = getIndVar(stem)
    andexpr = getAndExpr(stem)
    reLambda = re.compile(re.escape(str(andexpr)))
    string = "COUNT({0}, {1})".format(ivar, '{0}')
    andexpr = AndExpression(andexpr, lexpr(string))
    lambda_bit = reLambda.split(str(stem))[0]
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)



# =========================
#        Word Rules       
# =========================

# not, n't
def negate(stem):
    ivar = getIndVar(stem)
    andexpr = getAndExpr(stem)
    reLambda = re.compile(re.escape(str(andexpr)))
    andexpr = AndExpression(andexpr, lexpr("NEGATION({0})".format(ivar)))
    lambda_bit = reLambda.split(str(stem))[0]
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)

# no
def complement(stem):
    ivar = getIndVar(stem)
    andexpr = getAndExpr(stem)
    reLambda = re.compile(re.escape(str(andexpr)))
    andexpr = AndExpression(andexpr, lexpr("COMPLEMENT({0})".format(ivar)))
    lambda_bit = reLambda.split(str(stem))[0]
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)

# definite articles
def unique(stem):
    ivar = getIndVar(stem)
    andexpr = getAndExpr(stem)
    reLambda = re.compile(re.escape(str(andexpr)))
    andexpr = AndExpression(andexpr, lexpr("UNIQUE({0})".format(ivar)))
    lambda_bit = reLambda.split(str(stem))[0]
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)

# TODO: should these go in the specialcases file?
# NN, NNS
def kind():
    return lexpr(r'\x.({0}(x))')

# NNP*, PRP*
def entity():
    return lexpr(r'\x.(EQUAL(x, {0}))')

# What, which
def entityQuestion():
    return lexpr(r'\P x. (P(x) & TARGET(x))')

# e.g. "How long ... ?"
def degreeQuestion():
    return lexpr(r'\P Q x.(Q(x) & P(x) & degree(P(d)) & TARGET(d))')


# =========================
#         Mappings        
# =========================

rules = {
        'NEGATE': negate,
        'COMPLEMENT': complement,
        'UNIQUE': unique,
        'EVENT': event,
        'MOD': mod,
        'COUNT': count
        }

special_rules = {
        'TYPE': kind,
        'ENTITY': entity,
        }

question_rules = {
        'NEGATE': negate,
        'COMPLEMENT': complement,
        'UNIQUE': unique,
        'EVENT': event,
        'MOD': mod,
        'COUNT': count
        }

question_special_rules = {
        'TYPE': kind,
        'ENTITY': entity,
        'ENTQUESTION': entityQuestion,
        'DEGQUESTION': degreeQuestion
        }
