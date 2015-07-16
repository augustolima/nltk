import codecs
from collections import defaultdict
from nltk.sem.logic import Expression


class PredicateLexicon(defaultdict):
    """
    Lexicon that maps words and CCG categories to logical forms.
    The lexicon is keyed by both tuple(word, category) and 
    just category. It can be queryed in multiple ways.

    predlex.get("cat")
        => predicates assigned to "cat" for all categories of "cat".
    predlex.get(("cat", 'N'))
        => predicates assign to "cat" only for category 'N'.
    predlex.get(('N'))
        => All predicates assigned to 'N'.
    predlex.get(("slurm", 'N'))
        => For unknown word "slurm", fills in all predicates for 'N' with "slurm".

    PredicateLexicon should only be queryed with the get method,
        not __getitem__.

    Predicate lexicon file format:
    #WORDS
    word :: category :: predicate 
    #CATEGORIES
    category :: predicate
    """
    
    _lexpr = Expression.fromstring

    @classmethod
    def fromfile(cls, filename):
        """
        Loads predicate lexicon from filename.
        Input file should be of the format as created
        by the build_predlex script.

        :param filename: path to predicate lexicon file.
        :type filename: str
        """
        predLex = cls()
        fp = codecs.open(filename, 'r', 'utf-8')
        key = None
        for line in fp:
            if not line or line.startswith('"'): # Comments
                continue
            if line.startswith('#'):
                key = line[1:].strip()
                continue
            if key == 'WORDS':
                (word, cat, pred) = line.strip().split(' :: ')
                predLex[(word, cat)].append(cls._lexpr(pred))
            elif key == 'CATEGORIES':
                (cat, pred) = line.strip().split(' :: ')
                predLex[cat].append(cls._lexpr(pred))
            else:
                raise Exception("Invalid key in lexicon: {0}".format(key))
        return predLex

    def __init__(self):
        self.default_factory = list

    def get(self, key):
        # Exact key match.
        if key in self.keys():
            return defaultdict.__getitem__(self, key)

        # No match or inexact match (i.e. word doesn't match but cat does).
        elif type(key) == tuple:
            (word, cat) = key
            # templates will be [] if cat not a key.
            templates = defaultdict.__getitem__(self, cat)
            return [self._lexpr(template.__str__().format(word))
                    for template in templates] 

        # The word is known but no category specified.
        else:
            word_keys = [k for k in self.keys() if type(k) == tuple]
            word_list = [word for (word, cat) in word_keys]
            if key in word_list:
                preds = [defaultdict.__getitem__(self, (w,c))
                         for (w,c) in word_keys if key == w]
                return set(reduce(list.__add__, preds, []))
        
        # Invalid key altogether.
        return defaultdict.__getitem__(self, key)
