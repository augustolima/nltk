import re
from nltk.sem.logic import Variable, Expression, ApplicationExpression

# ==============================
# The main semantic parsing algorithm
# CCGSem. Takes as input a CCG parse
# as an nltk.Tree and outputs a logic form.
# ==============================


lexpr = Expression.fromstring

def resolve(expression):
    """
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
    
    # If we're replacing all the variables x s.t. exists x
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

def check(expression):
    if re.findall(r'[a-zA-Z]+?(?::[0-9])?\([^a-z]', expression.__str__()): return False
    try:
        lexpr(expression.__str__())
        return True
    except:
        return False

def get_children(tree):
    subtrees = list(tree.subtrees())
    children = []
    i = 1
    while i < len(subtrees):
            children.append(subtrees[i])
            subsubtrees = list(subtrees[i].subtrees())
            i = i + len(subsubtrees)
    return children

def application(left_ex, right_ex, direction):
    if left_ex.__str__() == 'None': return right_ex
    if right_ex.__str__() == 'None': return left_ex

#    if direction == '<':
    if '<' in direction:
        return ApplicationExpression(right_ex, left_ex).simplify()
    elif '>' in direction:
        return ApplicationExpression(left_ex, right_ex).simplify() 
    else:
        raise Exception("Bad direction: {0}".format(direction))

def CCGSem(tree, predLex, verbose):
    expressions = []
    children = get_children(tree)

    if len(children) == 0:
        cat = str(tree.label())
        if '(' in cat:
            cat = re.findall(r'\((.*)\)', cat)[0]
        return predLex.get(word=tree[0], category=cat)

    if len(children) == 1:
        return CCGSem(children[0], predLex, verbose)

    direction = tree.label()[1]
    for left_ex in CCGSem(children[0], predLex, verbose):
        for right_ex in CCGSem(children[1], predLex, verbose):
            expr = application(left_ex, right_ex, direction)
            if check(expr):
                expressions.append(expr)
                if verbose:
                    print "* {0} {1} {2}\n\t==> {3}" \
                           .format(left_ex, direction, right_ex, expr)

    if verbose: print ""
    return expressions

def demo():
    from nltk.ccg import lexicon, chart
    from predicatelexicon import PredicateLexicon

    # Set up the CCG parser.
    lexstr = open('data/reagan.ccg.lex').read()
    lex = lexicon.parseLexicon(lexstr)
    parser = chart.CCGChartParser(lex, chart.DefaultRuleSet)

    # Parse the input sentence.
    sent = "Reagan was the president"
    try:
        parse = parser.parse(sent.split()).next()
    except:
        print "No valid parse for input sentence."
        return

    # Set up the predicate lexicon.
    predLex = PredicateLexicon.fromfile('data/predicates.lexicon')

    print "\n", sent, "\n"
    print "========= DERIVATION ==========\n"
    expressions = CCGSem(parse, predLex, True)
    #expressions = [resolve(expr) for expr in expressions]
    print "======= SEMANTIC PARSES =======\n"
    for expr in expressions:
        print "-> {0}".format(expr)
    print ""

if __name__ == '__main__':
    demo()
