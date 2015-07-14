from __future__ import unicode_literals

# ============================
# Rules for translating words/phrases
# into Neo-Davidsonian logic forms 
# as described in Reddy et. al. 2014.
# ===========================

#-----------------------------
#   WORD RULES
#-----------------------------

# Definite articles.
def def_art():
    return [r'\P x.(UNIQUE(x) & P(x))']

# Indefinite articles are ignored.
def indef_art():
    return [r'None']

def copula():
    return [r'\P R. exists x.(R(x) & P(x))',
            r'\P x.(P(x))']
#    return [r'\Q P y. exists x.(P(Q(x)) & P(x) & Q(y))']

def negate():
    return [r'\P Q e. exists x.(NEGATION(e) & P(e,x) & Q(x))']

def no():
    return [r'\P x.(COMPLEMENT(x) & P(x))']


#-----------------------------
#   POS RULES
#-----------------------------

# Proper nouns.
def const():
    return [r'\x.(EQUAL(x, {0}))']

# Regular nouns
def const2():
    return [r'\x.({0}(x))']

# Adjectives.
def adj():
    return [r'\P x.(P({0}(x)) & P(x))']

# Prepositions in, of, etc.
def prep():
    return [r'\B C y e. exists z .(C({0}:1(e, y)) & C({0}:2(e, z)) & C(y) & B(z))']

# TO
def to():
    return [r'\B C y e. exists w .(to:1(e, y) & C({0}:2(e, w)) & C(y) & B(w))']

# Adverbs. NOT WORKING.
def adv():
    return [r'\P e.(P({0}(e)) & P(e))']

# Numbers are constants or counts.
def num():
    return [const()[0],
            r'\P x.(COUNT(x, {0}) & P(x))']

# Conjunctions are &-expressions.
def conj():
    return [r'\P Q x.(P(x) & Q(x))']

# Question words.
def what():
    return [r'\P. exists x.(TARGET(x) & P(x))',
            r'\P Q x. exists e.(P(x,e) & Q(x))']
