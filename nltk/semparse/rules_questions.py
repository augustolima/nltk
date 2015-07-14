from __future__ import unicode_literals
import re

# ============================
# Rules for translating words/phrases
# into Neo-Davidsonian logic forms 
# as described in Reddy et. al. 2014.
# ===========================


# =========================
#        POS Rules        =
# =========================

# VB*, IN, TO, POS
def event(stem):
    exist_args = re.findall(r'exists ((?:[a-z]\s)*?)\.', stem)[0].split()
    lambda_args = [arg.strip('\\') for arg in re.findall(r'\\[a-z]', stem)]
    for larg in lambda_args:
        for (i,earg) in enumerate(reversed(exist_args)):
            stem += " & {0}:{1}({2}, {3})".format('{0}', i+1, larg, earg)
    stem += ')'
    return stem

# RB*, JJ*
def mod(stem):
    args = [arg.strip('\\') for arg in re.findall(r'\\[a-z]', stem)]
    for arg in args:
        stem += " & {0}({1})".format('{0}', arg)
    stem += ')'
    return stem

# CD
def count(stem):
    args = [arg.strip('\\') for arg in re.findall(r'\\[a-z]', stem)]
    for arg in args:
        stem += " & COUNT({0}, {1})".format(arg, '{0}')
    stem += ')'
    return stem

# WDT, WP*, WRB
def question(stem):
    exist_args = re.findall(r'exists ((?:[a-z]\s)*?)\.', stem)[0].split()
    for earg in exist_args:
        stem += " & TARGET({0})".format(earg)
    stem += ')'
    return stem


# =========================
#        Word Rules       =
# =========================

# not, n't
def negate(stem):
    args = [arg.strip('\\') for arg in re.findall(r'\\[a-z]', stem)]
    for arg in args:
        stem += " & NEGATION({0})".format(arg)
    stem += ')'
    return stem

# no
def complement(stem):
    args = [arg.strip('\\') for arg in re.findall(r'\\[a-z]', stem)]
    for arg in args:
        stem += " & COMPLEMENT({0})".format(arg)
    stem += ')'
    return stem

# definite articles
def unique(stem):
    args = [arg.strip('\\') for arg in re.findall(r'\\[a-z]', stem)]
    for arg in args:
        stem += " & UNIQUE({0})".format(arg)
    stem += ')'
    return stem



# =========================
#      Special Cases      =
# =========================

# indefinite articles
def indef():
    return "None"

# copula
def copula():
    return r'\P \x.(P(x))'

# NN, NNS
def kind():
    return r'\x.({0}(x))'

# NNP*, PRP*
def entity():
    return r'\x.(EQUAL(x, {0}))'

# CC
def conj():
    return r'\P Q x.(P(x) & Q(x))'
