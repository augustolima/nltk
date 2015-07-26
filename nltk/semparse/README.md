#NLTK Semantic Parser
Parses English sentences into Neo-Davidsonian logical forms
using a CCG parse. Following [Reddy et. al.](http://www.sivareddy.in/papers/reddy2014semanticparsing.pdf)

##Setup
The semantic parser requires data files to be built before
it can run. This section details how to build them. For the
purpose of example, the `data/` directory contains 
CCG and predicate lexicons in two domains. 

### Data required for the semantic parser
* CCG lexicon
* Predicate lexicon

###Building the required files
* First, obtain a file of tokenized sentences, one per line.
  + e.g. `data/reagan/sentences.txt`
* Parse this file using the C&C parser using `parse_sents`.
  + Read usage instructions ( `parse_sents -h` ) to make sure the C&C parser is set up as required.
  + `./parse_sents -i data/reagan/sentences.txt -o data/reagan/parses.txt`
* The output of `parse_sents` will be used to build both
      the CCG lexicon and the predicate lexicon.

####Building the CCG lexicon
* Build the CCG lexicon using `build_ccglex`
  + `./build_ccglex -i data/reagan/parses.txt -o data/reagan/ccg.lex`

####Building the predicate lexicon
* Build the predicate lexicon using `build_predlex`
  + `./build_predlex -i data/reagan/parses.txt -o data/reagan/predicates.lex`

##Usage
Once you have the required data, the semantic parser can be used as an interactive
interpreter or from within Python.

###Using the interactive interpreter
`./semparser --ccglex data/reagan/ccg.lex --predlex data/reagan/predicates.lex`

####Command line options
#####Required
* `--ccglex path/to/file`: CCG lexicon to use.
* `--predlex path/to/file`: Predicate lexicon to use.

#####Optional
* `-v --verbose`: Show full semantic derivation.
* `-s --syntax`: Show syntactic parse tree.

####Commands
* `!help`: show help message.
* `!quit`: exit the interpreter.
* `!verbose On|Off`: set verbose.
* `!syntax On|Off`: set syntax.
* `!predlex <word>`: show predicates assigned to word.


###Using the semantic parser within Python

    from nltk.semparse import SemanticParser

    ccglex = 'nltk/semparse/data/reagan/ccg.lex'
    predlex = 'nltk/semparse/data/reagan/predicates.lex'
    SemParser = SemanticParser(ccglex, predlex)
    
    sent = "Reagan was an actor."
    for parse in SemParser.parse(sent):
        print parse.expression
        break

##Testing
`test.py` holds unit tests for both the logical lexicon generation step
and the semantic parsing step. For the semantic parsing step, the tests
will output the composed logical form, nothing, or any error messages that
occur in the pipeline.
