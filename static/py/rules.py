import re
from nltk import CFG
from nltk.parse.generate import generate

class Rules:

    # def __init__(self):
    #     # we read the file and get the rules
    #     file = open('rules', 'r')
    #
    #     for line in file:
    #         print(line)

    mappings = []

    def __init__(self):

        # all the stuff below happens after reading the file
        source = 'NP -> DT <> NN'
        target = 'NP -> DT NN <>'

        self.mappings.append(Mapping(source, target))

        source = 'VP -> VBD VP'
        target = '_ -> _ VP'

        self.mappings.append(Mapping(source, target))

    def applyRules(self, sentence):  # tree here is just for testing, remove later
        # would normally need a rules object for now we just test it

        production = sentence.augTree.productions()  # get the context free grammar for this tree, which we then modify

        for prod in production:
            print prod

        # TESTING
        grammar = CFG(production[0].lhs(), production)

        for sent in generate(grammar, n=10):
            for word in sent:
                print word,
            print

        # TESTING

        newProduction = []

        for m in self.mappings:     # for each rule
            source = re.sub(' <> ', '(.*)', m.source)   # build each source

            for prod in production:  # for each tree generation rule (in the CFG)

                match = re.match(r'%s' % source, str(prod))      # check if the rule matches the current CFG rule

                if match:

                    target = re.sub(r'<>', match.group(1).strip(), m.target)     # build the target from the source
                    print target


class Mapping:
    def __init__(self, s, t):
        self.source = s
        self.target = t