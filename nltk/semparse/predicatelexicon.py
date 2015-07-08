import codecs
from collections import defaultdict
from nltk.sem.logic import Expression


class PredicateLexicon(defaultdict):
    """
    Lexicon that maps CCG categories and words to logical forms.
    If the logical form of a word is known, it is returned.
    Otherwise, user can specify a word and a category to get
    a list of possible logical forms for that word with that category.
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
                (word, pred) = line.strip().split(' :: ')
                predLex[word].append(cls._lexpr(pred))
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
        if not word:
            return self.categories[category]
        else:
            if word in self.keys():
                return self[word]
            else:
                if len(word) == 1:
                    word = "_{0}".format(word)
                return [self._lexpr(expr.__str__().format(word))
                        for expr in self.categories[category]]
