import codecs
from collections import defaultdict
from nltk.sem.logic import Expression


class PredicateLexicon(defaultdict):
    """
    Lexicon that maps words and CCG categories to logical forms.
    If the logical form of a word is known, it is returned.
    Otherwise, user can specify a word and a category to get
    a list of possible logical forms for that word with that category.

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
                predLex.categories[cat].append(cls._lexpr(pred))
            else:
                raise Exception("Invalid key in lexicon: {0}".format(key))
        return predLex

    def __init__(self):
        self.default_factory = list
        self.categories = defaultdict(list)

    def get(self, word=None, category=None):
        if not word and not category:
            return set()
        elif not word and category:
            return set(self.categories[category])
        elif word and not category:
            preds = [self[(w,c)] for (w,c) in self.keys() if word == w]
            preds = set(reduce(list.__add__, preds, []))
            return preds
        elif (word, category) in self.keys():
            return set(self[(word, category)])
        else:
            if len(word) == 1:
                word = "_{0}".format(word)
            preds = [self._lexpr(expr.__str__().format(word))
                     for expr in self.categories.get(category, [])]
            return set(preds)
