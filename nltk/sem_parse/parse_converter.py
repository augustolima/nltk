import re
from nltk.parse import DependencyGraph


def read_data(file_str):
    data = open(file_str).read().split('\n\n')
    data = [parse.split('|||') for parse in data]
    data = [(tags.strip(), deps.strip()) for (tags, deps) in data]
    return data

def to_conll(tag_str, universal_deps):
    """
    Converts a POS tag list and set of universal dependencies
    as output by the stanford parser <nlp.stanford.edu:8080/parser/>
    into conll format to be read in by the DependencyGraph constructor.
    """
    tags = tag_str.split()
    tags = dict([tag.split('/') for tag in tags])
    deps = universal_deps.split('\n')
    conll = ""
    for dep in deps:
        m = re.search(r'(.+)\(.+?-([0-9]+). ([a-z]*)-.*\)', dep, re.IGNORECASE)
        rel = m.group(1)
        head = m.group(2)
        word = m.group(3)
        formatted_str = "{0} {1} {2} {3}\n" .format(word, tags[word], head, rel)
        conll += formatted_str
    return conll.strip()

def convert(data_file_str):
    data = read_data(data_file_str)
    graphs = []
    for (tag_list, dep_list) in data:
        conll_str = to_conll(tag_list, dep_list)
        graphs.append(DependencyGraph(conll_str))
    return graphs
