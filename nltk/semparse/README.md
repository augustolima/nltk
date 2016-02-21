#NLTK Semantic Parser
Parses English sentences into Neo-Davidsonian logical forms
using a CCG parse. Following [Reddy et. al.](http://www.sivareddy.in/papers/reddy2014semanticparsing.pdf)

##Setup
The semantic parser requires a CCG lexicon in order to run. 
This section explains how to build it. For the
purpose of example, the `data/lexica/` directory contains 
CCG lexicons in two domains. It also requires a language file
(e.g. `data/lib/english.txt`).

### Data required for the semantic parser
* CCG lexicon
* Language file

####Building the CCG lexicon.
The CCG lexicon can be built by hand (see example usage below) or automatically.
It is possible to use an existing CCG lexicon so long as it conforms to the format
required by `nltk.ccg.lexicon`. See [this link](http://www.nltk.org/howto/ccg.html) for more information.

#####Building the CCG lexicon automatically
* First, obtain a file of tokenized sentences, one per line.
  + e.g. `data/lexica/reagan_sentences.txt`
* Supertag these sentences using the C&C parser using `get_supertags`.
  + Read usage instructions ( `get_supertags -h` ) to make sure the C&C parser is set up as required.
  + `./get_supertags -i data/lexica/reagan_sentences.txt -o data/lexica/reagan_supertags.txt`
  + N.B. use the `-q` flag for supertagging questions.
* The output of `get_supertags` will be used to build the CCG lexicon.
* Build the CCG lexicon using `build_ccglex`
  + `./build_ccglex -i data/lexica/reagan_supertags.txt -o data/lexica/reagan.ccg`

####Language File
The language file describes language-specific side cases. It specifies the semantics for
words when the SemanticCategory class fails to generate an expression. An example can be found
at `data/lib/english.txt`. There should be a separate file for defining the mappings between
POS tags and semantic types, e.g. `data/lib/english_pos.txt`.

##Usage
Once you have the required data, the semantic parser can be used as an interactive
interpreter or from within Python.

###Using the interactive interpreter
The interpreter supports shell-like command line editing and history. Type a sentence
at the '>' prompt and press ENTER.

`Usage: semparser [-v] [-s] [--draw] <path/to/ccg_lexicon_file>`

E.g.  `./semparser -v -s data/lexica/reagan.ccg`

####Command line options
#####Required
* `<path/to/ccg_lexicon_file>`: CCG lexicon to use.

#####Optional
* `-v --verbose`: Show full semantic derivation.
* `-s --syntax`: Show syntactic parse tree.
* `--draw`: draw the semantic derivation tree in the GUI.

####Commands
* `!help`: show help message.
* `!quit`: exit the interpreter.
* `!verbose [Oo]n|[Oo]ff`: set verbose.
* `!syntax [Oo]n|[Oo]ff`: set syntax.


###Using the semantic parser within Python
The SemanticParser requires tokenized and POS tagged input, in the format
output by nltk.pos_tag.

     1 from nltk import word_tokenize, pos_tag
     2 from nltk.ccg import lexicon
     3 from nltk.semparse import SemanticParser
     4
     5 ccglex = lexicon.parseLexicon(r'''
     6  :- S, NP
     7  I => NP
     8  eat => (S\NP)/NP
     9	peaches => NP
    10 ''')	
    11 semparser = SemanticParser(ccglex)
    12  
    13 sent = "I eat peaches."
    14 tagged_sent = pos_tag(word_tokenize(sent))
    15 for parse in semparser.parse(tagged_sent):
    16   print parse.get_expression()
    17   break

###Using other CCG syntactic parsers
It is possible to use external programs for CCG syntactic parsing in place of
`nltk.ccg`. The output of the CCG parser should be in the AUTO format including POS tags
and a `str` instance. The parse string is then passed to `SemanticParser.parse()`.
The entire process looks like:

     1 from nltk.semparse import SemanticParser
     2
     3 # Set variable parse_str to a CCG parse string in AUTO format.
     4 # The semantic parser gets all needed information from the parse string.
     5 
     6 semparser = SemanticParser()
     7 for parse in semparser.parse(parse_str):
     9   print parse.get_expression()
    10   break


NB that `SemanticParser` is instantiated without a CCG lexicon.

##Testing
`test.py` holds unit tests for both the logical lexicon generation step
and the semantic parsing step. There are also functional tests of the converage of 
the semantic parser. Using NLTK CCG as input the tests output the following:

`[SYN][SEM]<input sentence>`

Where SYN/SEM will be red if syntacic/semantic derivation failed for `<input sentence>`
or green if succeeded. If any errors occur, they will be shown after `[SEM]` in yellow.

Using AUTO string input the tests just output the `[SEM]` field.
