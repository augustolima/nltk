##Setup
The semantic parser requires data files to be built before
it can run. This section details how to build them. For the
purpose of example, the `data/reagan` directory contains data
built from a Wikipedia article on Ronald Reagan.

### Data required for the semantic parser
* CCG lexicon
* Predicate lexicon

###Building the required files
* First, obtain a file of tokenized sentences, one per line.
  + e.g. `data/reagan/sentences.txt`
* Parse this file using the C&C parser using scripts/parse\_sents
  + `./parse_sents -i data/reagan/sentences.txt -o data/reagan/parses.txt`
* The output of parse\_sents will be used to build both
      the CCG lexicon and the predicate lexicon.

####Building the CCG lexicon
* Build the CCG lexicon using build\_ccglex
  + `./build_ccglex -i data/reagan/parses.txt -o data/reagan/ccg.lex`

####Building the predicate lexicon
* Build the predicate lexicon using build\_predlex
  + `./build_predlex -i data/reagan/parses.txt -o data/reagan/predicates.lex`

##Usage
The semantic parser can be used as a CLI tool or
from within Python.

###Using the command line semantic parser
`./semparser --ccglex data/reagan/ccg.lex --predlex data/reagan/predicates.lex`

####Command line options
#####Required
* --ccglex path/to/file
* --predlex path/to/file

#####Optional
* -v --verbose: Show full semantic derivation.
* -s --syntax: Show syntactic parse tree.

####Shell commands
* !quit: exit the shell.
* !verbose=[True|False]: set verbose.
* !syntax=[True|False]: set syntax.


###Using the semantic parser within Python

    from nltk.ccg import lexicon, chart
    from nltk.semparse.predicatelexicon import PredicateLexicon
    from nltk.semparse.CCGSem import CCGSem
    
    lexfile = open('data/reagan/ccg.lex').read()
    ccglex = lexicon.parseLexicon(lexfile)
    parser = chart.CCGChartParser(ccglex, chart.DefaultRuleSet)
    
    predLex = PredicateLexicon.fromfile('data/reagan/predicates.lex')
    
    sent = "Reagan was an actor".split()
    parse = parser.parse(sent).next()
    
    expressions = CCGSem(parse, predLex, False)
    for expression in expressions:
        print expression
