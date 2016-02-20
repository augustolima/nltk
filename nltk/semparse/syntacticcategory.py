import re


class SyntacticCategory(object):

    def __init__(self, syncat_str, syncat_dict=None):
        self._syncat_dict = syncat_dict
        self.syncat = syncat_str.replace("'", '')
        self.index_syncat = self._get_index_syncat()

    def __str__(self):
        return self.index_syncat

    def __repr__(self):
        return self.index_syncat

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
