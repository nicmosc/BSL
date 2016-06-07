import re
from nltk import CFG, Nonterminal, Production
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

        # read the rules from the file

        # all the stuff below happens after reading the file
        source = 'NP -> DT <> NN'
        target = 'NP -> DT NN <>'

        self.mappings.append(Mapping(source, target))

        source = 'VP -> VBD VP'
        target = 'VP -> _ VP'

        self.mappings.append(Mapping(source, target))

    def applyRules(self, sentence):  # tree here is just for testing, remove later
        # would normally need a rules object for now we just test it

        production = sentence.augTree.productions()  # get the context free grammar for this tree, which we then modify

        # TESTING
        for prod in production:
            print prod

        newProductions = []

        # the [:] is because we may want to modify the list
        for prod in production:      # for each tree generation rule (in the CFG)

            modApplied = False         # if no modification is applied to the rule we add it back normally
            for m in self.mappings:  # for each mapping rule

                target = m.target       # we don't want to modify the original rules otherwise
                source = m.source       # the next sentence will be affected

                # before doing anything we need to replace any occurrence of NN_1 in the target

                p = str(prod).split(' ')
                maps = m.target.split(' ')

                for i, map in enumerate(maps):
                    for sec in p[:]:  # for each section in the line
                        spl = sec.split('_')  # len is 2 if the tag is unique
                        if spl[0] == map:  # if the two are identical
                            if len(spl) > 1:  # if the tag is unique modify the other end
                                maps[i] += '_' + str(spl[1])
                            p.remove(sec)
                            break
                m.target = ' '.join(maps)

                source = re.sub(' <> ', '(.*)', m.source)  # build the source
                match = re.match(r'%s' % source, str(prod))  # check if the rule matches the current CFG rule

                if match:

                    if len(match.groups()) == 0:
                        rep = match.group()      # if the match is exact (no in between stuff) then just use it as is
                    else:
                        rep = match.group(1).strip()

                    target = re.sub(r'<>',rep, m.target)  # build the target from the source
                    modApplied = True
                    print "match", prod, target

                    # construct nonterminal objects from target
                    target = target.replace('->', '')
                    target_sections = target.split(' ')

                    productionObjects = []
                    for section in target_sections:
                        if len(section) > 0 and section != '_':
                            print section
                            productionObjects.append(Nonterminal(section))

                    # now construct the production object from the nonterminals

                    newProductions.append(Production(productionObjects[0], productionObjects[1:])) # add the modified rule to the list

                    break       # once a matching rule is found, no need to keep going

            if not modApplied:
                newProductions.append(prod)      # if no modification is applied, push the rule to the new list

        # THEN REBUILD THE TREE
        grammar = CFG(newProductions[0].lhs(), newProductions)

        for sent in generate(grammar, n=1):  # only 1 sentence can be generated
            for word in sent:
                print word,
            print

class Mapping:
    def __init__(self, s, t):
        self.source = s
        self.target = t