import re
from nltk.sem.logic import Variable, Expression, ApplicationExpression

# ==============================
# The main semantic parsing algorithm
# CCGSem. Takes as input a CCG parse
# as an nltk.Tree and outputs a logic form.
# ==============================


lexpr = Expression.fromstring

# Does not currently work for all expressions.
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

def check(expression):
    """
    Checks if expression is valid.
    return type bool
    """
    # Check for misplaced lambda expressions.
    if re.findall(r'[a-zA-Z]+?(?::[0-9])?\([^a-z]', expression.__str__()):
        return False
    try:
        lexpr(expression.__str__())
        return True
    except:
        return False

def typeraise(expression):
    """
    Typeraises expression.

    param Expression expression
    return type Expression
    """
    pass

def compose(expr1, expr2):
    """
    Performs the functional composition of 
    expr1 and expr2.

    param Expression expr1 expr2: input expressions
    return type Expression
    """
    first = ApplicationExpression(expr2, lexpr('C')).simplify()
    sec = ApplicationExpression(expr1, first).simplify()
    string = sec.__str__() 
    try:
        first_var = re.match(r'\\.*?([a-z])[a-z]*?\.', string).group(1)
        index = string.index(first_var)
        newstring = string[:index] + 'C ' + string[index:]
    except AttributeError:  # Regex did not match. No lambdas in expression.
        newstring = '\\C. ' + string
    return lexpr(newstring)

def substitute(expr1, expr2):
    """
    Performs the substitute operation of expr1 and expr2

    param Expression expr1 expr2: input expressions
    return type Expression
    """
    first = ApplicationExpression(expr1, lexpr('S'))
    sec = ApplicationExpression(first, expr2).simplify()
    newstring = '\\S ' + sec.__str__()
    return lexpr(newstring)

def apply_rule(left_ex, right_ex, rule):
    """
    Passes left_ex and right_ex to the correct rule application
    function.

    param Expression left_ex right_ex: input expressions
    param str rule: CCG combinatory rule as specified by the CCG parse.
    return type Expression
    """
    if left_ex.__str__() == 'None': return right_ex
    if right_ex.__str__() == 'None': return left_ex

    if rule == '>':  # Forward application
        return ApplicationExpression(left_ex, right_ex).simplify() 
    if rule == '<':  # Backward application
        return ApplicationExpression(right_ex, left_ex).simplify()
    if rule == '>Sx':  # Forward substitution
        return substitute(left_ex, right_ex)
    if rule == '<Sx':  # Backward substitution
        return substitute(right_ex, left_ex)
    if rule == '>B':  # Forward composition
        return compose(left_ex, right_ex)
    if rule == '<B':  # Backward composition
        return compose(right_ex, left_ex)
    raise Exception("Bad rule: {0}".format(rule))

def get_children(tree):
    subtrees = list(tree.subtrees())
    children = []
    i = 1
    while i < len(subtrees):
            children.append(subtrees[i])
            subsubtrees = list(subtrees[i].subtrees())
            i = i + len(subsubtrees)
    return children

def CCGSem(tree, predLex, verbose):
    """
    The main MR composition algorithm.

    param nltk.Tree tree: input CCG parse
    param nltk.semparse.PredicateLexicon predLex: predicate lexicon to use
    param bool verbose: Whether to print steps of semantic derivation
    return type list(Expression)
    """
    derivation = []
    def recurse(tree):
        expressions = []
        children = get_children(tree)

        # Leaf
        if len(children) == 0:
            cat = str(tree.label())
            if '(' in cat:  # Get rid of extra parentheses.
                cat = re.findall(r'\((.*)\)', cat)[0]
            return predLex.get(word=tree[0], category=cat)

        # Unary rule
        if len(children) == 1:
            return recurse(children[0])

        # Binary rule
        rule = tree.label()[1]
        for left_ex in recurse(children[0]):
            for right_ex in recurse(children[1]):
                expr = apply_rule(left_ex, right_ex, rule)
                if check(expr):
                    expressions.append(expr)
                    string = "* {0} {1} {2}\n\t==> {3}" \
                              .format(left_ex, rule, right_ex, expr)
                    if string not in derivation:
                        derivation.append(string)

        if derivation and derivation[-1] != '\n':
            derivation.append('\n')
        return expressions

    expressions = recurse(tree)
    if verbose:
        for step in derivation:
            print step
    return expressions

def demo():
    from nltk.ccg import lexicon, chart
    from predicatelexicon import PredicateLexicon

    # Set up the CCG parser.
    lexstr = open('data/reagan/ccg.lex').read()
    lex = lexicon.parseLexicon(lexstr)
    parser = chart.CCGChartParser(lex, chart.DefaultRuleSet)

    # Parse the input sentence.
    sent = "Reagan was the president and an actor"
    try:
        parse = parser.parse(sent.split()).next()
    except:
        print "No valid parse for input sentence."
        return

    # Set up the predicate lexicon.
    predLex = PredicateLexicon.fromfile('data/reagan/predicates.lex')

    print "\n", sent, "\n"
    print "======= SYNTACTIC PARSE =======\n"
    chart.printCCGDerivation(parse)

    print "========= DERIVATION ==========\n"
    expressions = CCGSem(parse, predLex, True)
    #expressions = [resolve(expr) for expr in expressions]

    print "======= SEMANTIC PARSES =======\n"
    for expr in expressions:
        print "+  {0}".format(expr)
    print ""


if __name__ == '__main__':
    demo()
