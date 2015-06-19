from nltk.sem.logic import *
from itertools import count
from collections import defaultdict
from pprint import pprint

# Local import
import parse_converter


lexpr = Expression.fromstring
appex = ApplicationExpression


class MRExpression(object):
    """
    Class for keeping track of composed expressions and
    and their probabilities.
    """
    def __init__(self, expression, probability):
        self.expression = expression
        self.probability = probability


def read_predicate_lexicon(filename):
    """
    param str filename
    returns: dictionary of form {word: logical expression}
    """
    predicates = open(filename).readlines()
    predicates = [pred.split(' ||| ') for pred in predicates
                    if not pred.startswith('#')]
    predicates = [(word, MRExpression(lexpr(form), float(prob))) for (word, form, prob) in predicates]
    pred_lex = defaultdict(list)
    for (word,expr) in predicates:
        pred_lex[word].append(expr) 
    return pred_lex

def read_rule_lexicon(filename):
    """
    param str filename
    returns: dictionary of form {edge label: application rule} 
    """
    rules = open(filename).readlines()
    rules = [rule.strip().split(' :: ') for rule in rules
                if not rule.startswith('#')]
    return dict(rules)

def num_words(dependency_graph):
    num = 0
    for i in count(start=1, step=1):
        if dependency_graph.contains_address(i):
            num += 1
        else:
            break
    return num

def words(dependency_graph):
    """
    Gets the sentence as a list of words from the dependency_graph.

    param nltk.parse.DependencyGraph dependency_graph
    """
    return [dependency_graph.get_by_address(i)['word']
            for i in range(1, num_words(dependency_graph) + 1)]

def concat_compounds(dependency_graph):
    """
    Concatenates any two words in dependency_graph that are in a
    compound relation. Changes dependency_graph in place.

    param nltk.parse.DependencyGraph
    """
    # First pass: combine nodes in compound relation and
    #             remove old nodes.
    sent_len = num_words(dependency_graph) + 1
    for i in range(1, sent_len):
        node = dependency_graph.get_by_address(i)
        children = node['deps']
        for child_index in children:
            child = dependency_graph.get_by_address(child_index)
            if child['rel'] == 'compound':
                node['deps'].remove(child['address'])
                node['lemma'] = child['word'] + " " + node['word'] 
                node['word'] = ' '.join([child['word'], node['word']])
                dependency_graph.remove_by_address(child['address'])

    # Second pass: change node addresses and determine how
    #              arc indices should be changed.
    replacements = []  # (original_index, replacement_index) tuples
    # j: new index   i: old index
    j = 1
    for i in range(1, sent_len):
        if dependency_graph.contains_address(i):
            node = dependency_graph.get_by_address(i)
            replacements.append((node['address'], j))
            node['address'] = j
            j += 1
    # Third pass: change arc indices
    for i in range(num_words(dependency_graph) + 1):
        node = dependency_graph.get_by_address(i)
        for (orig, repl) in replacements:
            if orig in node['deps']:
                idx = node['deps'].index(orig)
                node['deps'][idx] = repl
            if node.get('head') == orig:
                node['head'] = repl

def application(parent_pred, child_pred, rule):
    """
    Determines the correct order of application of parent_pred and child_pred.

    param Expression parent_pred: logical expression for parent.
    param Expression child_pred: logical expression for child.
    param str rule: application rule from rule dictionary.
    returns: composed expression
    """
    if not parent_pred: return child_pred
    if not child_pred: return parent_pred

    if rule == 'P-C': return appex(parent_pred, child_pred)
    elif rule == 'C-P': return appex(child_pred, parent_pred)
    elif rule == 'P': return parent_pred
    elif rule == 'C': return child_pred
    else: raise Exception("Bad rule: {0}" .format(rule))

def tr_print(string, tracing=False):
    """
    Trace print. Prints only if tracing is True.
    """
    if tracing:
        print string

def buildMR(dependency_graph, predicates, rules, trace=False):
    """
    Wrapper for the recursive composition function.
    
    param nltk.parse.DependencyGraph dependency_graph: dependency parse
    param dict predicates: output of read_predicate_lexicon
    param dict rules: output of read_rule_lexicon
    """
    # stacks hold the possible predicates for each word at each step of the
    # derivation. Thus the possible predicates for a word will change as  they
    # are composed by the predicates for the words it dominates in the graph.
    stacks = [predicates.get(word, [])[::] for word in words(dependency_graph)]
    stacks.insert(0, [])

    # compose modifies stacks such that the final
    # derivation(s) are held at stacks[head['address']].
    def compose(node):
        # Leaf node
        if not node['deps']:
            return stacks[node['address']]

        # Parent node
        children = [dependency_graph.get_by_address(i) for i in node['deps']]
        for child in children:
            exprs = [] # Keeps track of partially composed expressions.
            for child_pred in compose(child):
                for parent_pred in stacks[node['address']]:
                    rule = rules.get(child['rel'])
                    expr = application(parent_pred.expression, child_pred.expression, rule)
                    prob = parent_pred.probability * child_pred.probability
                    mr = MRExpression(expr.simplify(), prob)
                    exprs.append(mr)
                    tr_print("{0} + {1} -> {2}"
                              .format(parent_pred.expression, child_pred.expression, expr.simplify()), trace)
            if exprs:
                stacks[node['address']] = exprs[::]
        tr_print("", trace)
        return stacks[node['address']]

    root = dependency_graph.get_by_address(0)
    head = dependency_graph.get_by_address(root['deps'][0])
    compose(head)  # Changes stacks in place.
    return stacks[head['address']]

def demo():
    predicates = read_predicate_lexicon('data/problexicon.txt')
    rules = read_rule_lexicon('data/rules.txt')
    graphs = parse_converter.convert('data/parses.txt')
    for graph in graphs:
        print ' '.join(words(graph)) + "\n"
        print "----------------"
        concat_compounds(graph)  # Changes graph in place.
        for mr in buildMR(graph, predicates, rules, trace=True):
            print "-->", mr.expression, mr.probability
        print '================'
        raw_input()


if __name__ == '__main__':
    demo()
