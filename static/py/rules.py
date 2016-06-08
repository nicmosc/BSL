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




    def applyRules(self, sentence):  # apply all rules in order
        self.treeTranforms(sentence)

    def treeTranforms(self, sentence):

        productions = sentence.augTree.productions()  # get the context free grammar for this tree, which we then modify

        newProductions = []

        # the [:] is because we may want to modify the list
        for prod in productions:  # for each tree generation rule (in the CFG)

            modApplied = False  # if no modification is applied to the rule we add it back normally
            for m in self.tree_transforms:  # for each mapping rule

                p = str(prod).split(' ')  # split both CFG and target rules into separate chunks
                maps = m.target.split(' ')

                target = self.rebuildTarget(maps, p)  # rebuild the target with unique tags

                match = self.performMatch(prod, m)  # check for match

                if match:

                    if len(match.groups()) == 0:
                        rep = match.group()         # if the match is exact (no in between stuff) then just use it as is
                    else:
                        rep = match.group(1).strip()    # for now we assume there can be 1 group max, may have to upgrade later

                    target = re.sub(r'<>', rep, target)  # build the target from the source (special case)

                    modApplied = True

                    newProductions.append(self.constructProduction(target))     # append new production from target

                    break  # once a matching rule is found, no need to keep going

            if not modApplied:
                newProductions.append(prod)  # if no modification is applied, push the rule to the new list

        # testing - print old vs new production
        for i in range(len(productions)):
            print productions[i], "\t \t \t", newProductions[i]

        # THEN REBUILD THE SENTENCE
        grammar = CFG(newProductions[0].lhs(), newProductions)

        for sent in generate(grammar, n=1):  # only 1 sentence can be generated
            for word in sent:
                print word,
            print

    def constructProduction(self, target):
        # construct nonterminal objects from target
        target = target.replace('->', '')
        target_sections = target.split(' ')

        productionObjects = []
        for section in target_sections:
            if len(section) > 0 and section != '_':
                # print section
                productionObjects.append(Nonterminal(section))
        # now construct the production object from the nonterminals
        return Production(productionObjects[0], productionObjects[1:])  # return the modified rule to the list

    def performMatch(self, prod, m):
        # before doing anything we need to replace any occurrence of NN_1 in the target
        clean_prod = re.sub('_\d\s?', ' ', str(prod))  # remove any _x to match
        source = re.sub(' <> ', '(.*)', m.source)  # build the source
        return re.match(r'%s' % source, clean_prod)  # check if the rule matches the current CFG rule

    def rebuildTarget(self, maps, p):
        # rebuild the target with new tags
        for i, map in enumerate(maps):
            for sec in p[:]:  # for each section in the line
                spl = sec.split('_')  # len is 2 if the tag is unique
                if spl[0] == map:  # if the two are identical
                    if len(spl) > 1:  # if the tag is unique modify the other end
                        maps[i] += '_' + str(spl[1])
                    p.remove(sec)
                    break
        return ' '.join(maps)

class Mapping:
    def __init__(self, s, t):
        self.source = s
        self.target = t