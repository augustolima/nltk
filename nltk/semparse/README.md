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
  + `./get_supertags data/lexica/reagan_sentences.txt > data/lexica/reagan_supertags.txt`
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

`Usage: semparser [-v] [-s] -l <path/to/ccg lexicon file>`

E.g.  `./semparser -l data/lexica/reagan.ccg`

####Command line options
#####Required
* `-l --ccglex <path/to/file>`: CCG lexicon to use.

#####Optional
* `-v --verbose`: Show full semantic derivation.
* `-s --syntax`: Show syntactic parse tree.

####Commands
* `!help`: show help message.
* `!quit`: exit the interpreter.
* `!verbose On|Off`: set verbose.
* `!syntax On|Off`: set syntax.


###Using the semantic parser within Python
The SemanticParser requires tokenized and POS tagged input, in the format
output by nltk.pos_tag.

     1 from nltk import word_tokenize, pos_tag
     2 from nltk.ccg import lexicon
     3 from nltk.semparse import SemanticParser
     4
     5 ccglex = lexicon.parseLexicon(r'''
     6  :- S, N
     7  I => N
     8  eat => (S\N)/N
     9	 peaches => N
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
`nltk.ccg`. The output of the CCG parser should be in the AUTO format and
a `str` instance. The parse string is then passed as an optional argument
to `SemanticParser.parse()`. The entire process looks like:

     1 from nltk import word_tokenize, pos_tag
     2 from nltk.semparse import SemanticParser
     3
     4 semparser = SemanticParser()
     5  
     6 # Set variable auto_str to the CCG parse string.
     7 sent = "I eat peaches."
     8 tagged_sent = pos_tag(word_tokenize(sent))
     9 for parse in semparser.parse(tagged_sent, ccg_parse_str=auto_str):
    10   print parse.get_expression()
    11   break
    

NB that `SemanticParser` is instantiated without a CCG lexicon.

##Testing
`test.py` holds unit tests for both the logical lexicon generation step
and the semantic parsing step. For the semantic parsing step, the tests
output the following:

`[SYN][SEM]<input sentence>`

Where SYN/SEM will be red if syntacic/semantic derivation failed for `<input sentence>`
or green if succeeded. If any errors occur, they will be shown after `[SEM]` in yellow.
