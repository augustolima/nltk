import os
import re

from nltk.semparse.config import (_DATA_DIR, _CandC_MARKEDUP_FILE)


class SyntacticCategory(object):

    syncat_dict_cache = None

    @classmethod
    def get_cached_syncat_dict(cls):
        if not cls.syncat_dict_cache:
            cls.syncat_dict_cache = cls._parse_markedup_file()
        return cls.syncat_dict_cache

    @classmethod
    def _parse_markedup_file(cls):
        """
        Parses the C&C markedup file into a dictionary of the form
        {syntactic_category: indexed_syntactic_category}. E.g.
        {'S\\N': '(S{_}\\NP{Y}<1>){_}'}
        :rtype: dict
        """
        filestr = open(_CandC_MARKEDUP_FILE, 'r').read()
        marks = filestr.split('\n\n')
        marks = [line.strip() for line in marks
                 if not line.startswith('#') and not line.startswith('=')]
        pairs = [line.split('\n')[:2] for line in marks]
        pairs = [(syncat.strip(), idxsyncat.strip())
                 for (syncat, idxsyncat) in pairs]
        pairs = [(syncat, idxsyncat.split()[1])
                 for (syncat, idxsyncat) in pairs]
        # For matching the syntactic_categories to the
        # NLTK CCG syntactic categories, we have to get rid of
        # the brackets. S[adj]\\NP => S\NP.
        # This means the the resulting dictionary will collapse
        # all syntactic categories that differ only in type,
        # e.g. S[adj]\\NP & S[ng]NP => S\\NP.
        ppairs = [(re.sub(r'\[.*?\]', '', syncat), _)
                  for (syncat, _) in pairs]
        # This is necessary because of the mapping that happens
        # according to the NLTK CCG lexicon.
        # TODO: changing NP to N here is not robust. Do it on the fly.
        processed_pairs = [(syncat.replace('NP', 'N'), _)
                           for (syncat, _) in ppairs]
        # Create the dictionary that maps from syntactic
        # category to indexed syntactic category.
        pairsdict = dict(processed_pairs)
        return pairsdict

    def __init__(self, syncat_str):
        self._syncat_dict = self.get_cached_syncat_dict()
        self.syncat = syncat_str
        self.index_syncat = self._get_index_syncat()

    def _get_index_syncat(self):
        """
        Gets the indexed syntactic category from the C&C mapping.

        :rtype: str
        """
        return self._syncat_dict.get(self.syncat, None)

    def _preprocess_category(self):
        """
        For self.index_syncat
        Removes astericks in (it specifies unneeded information).
        Removes bracketed syntactic specifiers, e.g. 'S[dcl]' => 'S'

        :rtype: str
        """
        processed_category = self.index_syncat.replace('*', '')
        processed_category = processed_category.replace('_', 'e')
        reCurlyBrace = re.compile(r'(?<=\))\{[A-Ze]\}.*?')
        processed_category = reCurlyBrace.sub('', processed_category)
        return processed_category

    def parse(self):
        """
        Parses the indexed syntactic category string into a binary
        tree according to parentheses and '/' or '\\' operators.
        Result is a binary tree in which each node is a function,
        the left child is the return value and the right child
        is the argument. Represents the curried function.

        :param index_syncat: indexed syntactic category to parse.
        :type index_syncat: str
        :rtype: list
        """
        processed_category = self._preprocess_category()
        PARENS = ['(', ')']
        OPERATORS = ['\\', '/']

        def levelappend(stack, level, arg):
            levelstack = stack
            for i in range(level):
                levelstack = levelstack[-1]
            levelstack.append(arg)

        level = 0
        levelup = 0
        stack = []
        arg = ""
        for i, c in enumerate(processed_category):
            if c == '(':
                levelappend(stack, level, [])
                level += 1
            elif c not in PARENS + OPERATORS:
                arg += c
            elif c in OPERATORS:
                levelappend(stack, level, arg)
                arg = ""
                if levelup > 0 and level > 0:
                    level -= levelup
                    levelup = 0
            elif c == ')':
                levelup += 1
        if arg:
            levelappend(stack, level, arg)
        return stack
