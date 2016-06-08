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

    tree_transforms = []    # rules to be applied to the syntax trees
    direct_translation = [] # rules for direct translation

    dependency_transforms = []  # to be applied to dependencies, not used for now

    def __init__(self):

        # read the rules from the file

        # first open tree transforms
        dir = '../res/rules/'

        f_name = 'tree_transforms.txt'
        try:
            file = open(dir + f_name, 'r')
            for line in file:
                if not line.isspace():      # if the line is not empty
                    sections = line.split('|')
                    source = sections[0].strip()
                    target = sections[1].split('//')[0].strip()    # remove comments from second part

                    print source, " | ", target
                    self.tree_transforms.append(Mapping(source, target))    # add new rule

        except IOError:
            print 'File '+f_name+' not found'

        # all the stuff below happens after reading the file
        # source = 'NP -> DT <> NN'
        # target = 'NP -> DT NN <>'
        #
        # self.tree_transforms.append(Mapping(source, target))
        #
        # source = 'VP -> VBD VP'
        # target = 'VP -> _ VP'
        #
        # self.tree_transforms.append(Mapping(source, target))

    def applyRules(self, sentence):  # tree here is just for testing, remove later
        # would normally need a rules object for now we just test it

        productions = sentence.augTree.productions()  # get the context free grammar for this tree, which we then modify

        newProductions = []

        # the [:] is because we may want to modify the list
        for prod in productions:      # for each tree generation rule (in the CFG)

            modApplied = False       # if no modification is applied to the rule we add it back normally
            for m in self.tree_transforms:  # for each mapping rule

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
                target = ' '.join(maps)

                clean_prod = re.sub('_\d\s?', ' ', str(prod))   # remove any _x to match

                source = re.sub(' <> ', '(.*)', m.source)  # build the source
                match = re.match(r'%s' % source, clean_prod)  # check if the rule matches the current CFG rule

                if match:

                    if len(match.groups()) == 0:
                        rep = match.group()      # if the match is exact (no in between stuff) then just use it as is
                    else:
                        rep = match.group(1).strip()

                    target = re.sub(r'<>',rep, target)  # build the target from the source
                    modApplied = True
                    #print "match", prod, target

                    # construct nonterminal objects from target
                    target = target.replace('->', '')
                    target_sections = target.split(' ')

                    productionObjects = []
                    for section in target_sections:
                        if len(section) > 0 and section != '_':
                            #print section
                            productionObjects.append(Nonterminal(section))

                    # now construct the production object from the nonterminals

                    newProductions.append(Production(productionObjects[0], productionObjects[1:])) # add the modified rule to the list

                    break       # once a matching rule is found, no need to keep going

            if not modApplied:
                newProductions.append(prod)      # if no modification is applied, push the rule to the new list


        # testing - print old vs new production
        for i in range(len(productions)):
            print productions[i], "\t \t \t", newProductions[i]

        # THEN REBUILD THE SENTENCE
        grammar = CFG(newProductions[0].lhs(), newProductions)

        for sent in generate(grammar, n=1):  # only 1 sentence can be generated
            for word in sent:
                print word,
            print

class Mapping:
    def __init__(self, s, t):
        self.source = s
        self.target = t