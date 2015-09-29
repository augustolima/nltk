from __future__ import print_function, unicode_literals

import re
from collections import OrderedDict

from nltk.sem.logic import (is_eventvar, is_indvar, Expression,
                            LambdaExpression, ExistsExpression,
                            AndExpression, ApplicationExpression,
                            IndividualVariableExpression,
                            FunctionVariableExpression)

# ////////////////////////////////////////////
# Rules for translating words/phrases into  //
# Neo-Davidsonian logic forms as described  //
# in Reddy et. al. 2014.                    //
# ////////////////////////////////////////////


# //////////////////////////////////
#         Error handling          //
# //////////////////////////////////

class StemException(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def input_checker(func):
    '''Decorator for checking input to rule functions'''
    def wrapper(stem):
        if not stem:
            raise StemException("In function <{0}>. stem == None"
                                 .format(func.__name__))
        return func(stem)
    return wrapper


# //////////////////////////////////
#         Helper functions        //
# //////////////////////////////////

lexpr = Expression.fromstring


def find_variables(expression):
    ''' Returns all bound variables.'''
    def helper(expression):
        if isinstance(expression, LambdaExpression) or \
           isinstance(expression, ExistsExpression):
            return find_variables(expression.term)
        if isinstance(expression, AndExpression):
            return find_variables(expression.second) + \
                   find_variables(expression.first)
        if isinstance(expression, ApplicationExpression):
            return find_variables(expression.function) + [expression.argument]
        if isinstance(expression, IndividualVariableExpression):
            return [expression.variable]
        if isinstance(expression, FunctionVariableExpression):
            return []
    vs = helper(expression)
    # Removes duplicates while keeping order.
    vs = list(OrderedDict.fromkeys(vs))
    vs = [v for v in vs if isinstance(v, IndividualVariableExpression)]
    return vs


def get_indvar(stem):
    '''Returns individual or event variable, e.g. \\e or \\x'''
    ivar = None
    while not ivar:
        v = str(stem.variable)
        if is_eventvar(v) or is_indvar(v):
            ivar = stem.variable
        stem = stem.term
    return ivar


def get_andexpr(stem):
    '''Returns just the AND expression of stem.
       e.g. \P Q x.(P(x) & Q(x) => (P(x) & Q(x))'''
    while type(stem) == LambdaExpression or type(stem) == ExistsExpression:
        stem = stem.term
    return stem


# /////////////////////////
#        POS Rules       //
# /////////////////////////

# VB*, IN, TO, POS
@input_checker
def event(stem):
    evar = get_indvar(stem)  # Event variable.
    andexpr = get_andexpr(stem)
    reLambda = re.compile(re.escape(str(andexpr)))
    lambda_bit = reLambda.split(str(stem))[0]
    for i, var in enumerate(find_variables(andexpr)):
        string = "{0}:{1}({2})({3})".format('{0}', i+1, evar, var)
        andexpr = AndExpression(andexpr, lexpr(string))
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)


# RB*, JJ*
@input_checker
def mod(stem):
    ivar = get_indvar(stem)
    andexpr = get_andexpr(stem)
    reLambda = re.compile(re.escape(str(andexpr)))
    string = "{0}({1})".format('{0}', ivar)
    andexpr = AndExpression(andexpr, lexpr(string))
    lambda_bit = reLambda.split(str(stem))[0]
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)


# CD
@input_checker
def count(stem):
    ivar = get_indvar(stem)
    andexpr = get_andexpr(stem)
    reLambda = re.compile(re.escape(str(andexpr)))
    string = "COUNT({0}, {1})".format(ivar, '{0}')
    andexpr = AndExpression(andexpr, lexpr(string))
    lambda_bit = reLambda.split(str(stem))[0]
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)


# /////////////////////////
#       Word Rules       //
# /////////////////////////

# not, n't
@input_checker
def negate(stem):
    ivar = get_indvar(stem)
    andexpr = get_andexpr(stem)
    reLambda = re.compile(re.escape(str(andexpr)))
    andexpr = AndExpression(andexpr, lexpr("NEGATION({0})".format(ivar)))
    lambda_bit = reLambda.split(str(stem))[0]
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)


# no
@input_checker
def complement(stem):
    ivar = get_indvar(stem)
    andexpr = get_andexpr(stem)
    reLambda = re.compile(re.escape(str(andexpr)))
    andexpr = AndExpression(andexpr, lexpr("COMPLEMENT({0})".format(ivar)))
    lambda_bit = reLambda.split(str(stem))[0]
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)


# definite articles
@input_checker
def unique(stem):
    ivar = get_indvar(stem)
    andexpr = get_andexpr(stem)
    reLambda = re.compile(re.escape(str(andexpr)))
    andexpr = AndExpression(andexpr, lexpr("UNIQUE({0})".format(ivar)))
    lambda_bit = reLambda.split(str(stem))[0]
    expression = lambda_bit + str(andexpr)
    return lexpr(expression)


# What, which
def entity_question():
    return lexpr(r'\P. exists x.(P(x) & TARGET(x))')


# TODO: should these go in the specialcases file?
# NN, NNS
def kind():
    return lexpr(r'\x.({0}(x))')


# NNP*, PRP*
def entity():
    return lexpr(r'\x.(EQUAL(x, {0}))')


# /////////////////////////
#        Mappings        //
# /////////////////////////

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
    'COUNT': count,
    }

question_special_rules = {
    'TYPE': kind,
    'ENTITY': entity,
    'ENTQUESTION': entity_question
    }
