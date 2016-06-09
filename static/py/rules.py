import re
from collections import defaultdict
from nltk import CFG, Nonterminal, Production
from nltk.parse.generate import generate

class Rules:

    def __init__(self):

        self.tree_transforms = []  # rules to be applied to the syntax trees
        self.direct_translation = defaultdict(lambda: defaultdict(str))  # rules for direct translation

        self.dependency_transforms = []  # to be applied to dependencies, not used for now

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

                    # REMEMBER TO MAYBE CREATE CATEGORIES FOR TREE TRANSFORMS TOO
                    if source[:2] != '//':  # if the rule is not commented out, print
                        print source, " | ", target
                    self.tree_transforms.append(Mapping(source, target))    # add new rule

        except IOError:
            print 'File '+f_name+' not found'

        # obtain direct translation rules
        f_name = 'direct_translation.txt'
        new_cat = True          # when this is true, we start a new category of direct rules
        current_cat = ''        # the category we are in at the moment
        try:
            file = open(dir + f_name, 'r')
            for line in file:
                if line.isspace():      # whenever a new category is introduced (space)
                    new_cat = True
                else:
                    if new_cat:
                        #print 'new category:',line
                        current_cat = line.strip()
                        new_cat = False
                    else:               # add rules to the dictionary, no need for Mapping cause we don't change the source
                        src = line.split('->')[0]
                        tgt = line.split('->')[1].strip()
                        self.direct_translation[current_cat][src] = tgt
        except IOError:
            print 'File ' + f_name + ' not found'

        for k,v in self.direct_translation.iteritems():
            print k
            for k1,v1 in v.iteritems():
                print k1,v1

    def treeTranforms(self, sentence):

        productions = sentence.augTree.productions()  # get the context free grammar for this tree, which we then modify

        for i in range(len(productions)):
           print productions[i]

        newProductions = []

        # the [:] is because we may want to modify the list
        for prod in productions:  # for each tree generation rule (in the CFG)

            modApplied = False  # if no modification is applied to the rule we add it back normally

            for m in self.tree_transforms:  # for each mapping rule

                p_list = str(prod).split(' ')  # split both CFG and target rules into separate chunks
                maps = m.target.split(' ')

                result = self.rebuildTarget(maps, p_list)  # rebuild the target with unique tags

                target = result[0]
                p_list = result[1]

                match = self.performMatch(prod, m)  # check for match

                if match:

                    #print p_list, 'LOOK HERE'

                    if len(match.groups()) == 0:
                        rep = match.group()         # if the match is exact (no in between stuff) then just use it as is
                    else:
                        #rep = match.group(1).strip()    # for now we assume there can be 1 group max, may have to upgrade later
                        rep = ' '.join(list(reversed(p_list)))      # whatever was not matched earlier is what we need to replace

                    target = re.sub(r'<>', rep, target)  # build the target from the source (special case)

                    print 'Match:',match.group(),' | ',target

                    modApplied = True

                    newProductions.append(self.constructProduction(target))     # append new production from target

                    break  # once a matching rule is found, no need to keep going

            if not modApplied:
                newProductions.append(prod)  # if no modification is applied, push the rule to the new list

        # testing - print old vs new production
        # for i in range(len(productions)):
        #    print productions[i], "\t \t \t", newProductions[i]

        # THEN REBUILD THE SENTENCE
        grammar = CFG(newProductions[0].lhs(), newProductions)

        result = None

        for sent in generate(grammar, n=1):  # only 1 sentence can be generated
            result = sent

        print result
        return result

    def directTranslation(self, i_sentence):

        for i,word in enumerate(i_sentence.words):       # go through all the words in the sentence
            new_word = self.direct_translation[word.POStag][str(word)]
            if len(new_word) != 0:      # if there is a rule
                if new_word == '_':     # if the rule maps to nothing, remove the word
                    i_sentence.words.remove(word)
                else:
                    i_sentence.words[i].root = new_word


    # all the stuff below is for the tree transformation
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

    def performMatch(self, prod, mapping):
        # before doing anything we need to replace any occurrence of NN_1 in the target
        clean_prod = re.sub('_\d\s?', ' ', str(prod))  # remove any _x to match
        #clean_prod = str(prod)
        source = re.sub('\s?<>\s?', '(.*)', mapping.source)  # build the source
        return re.match(r'%s' % source, clean_prod)  # check if the rule matches the current CFG rule

    def rebuildTarget(self, maps, production):
        # rebuild the target with new tags
        for i, map in enumerate(maps):
            for sec in production[:]:  # for each section in the line (production)
                spl = sec.split('_')  # len is 2 if the tag is unique
                any = map[-1] == '*'  # if asterisk is found at the end of the tag, it means any tag with extra at the end will match
                if spl[0] == map or map == '_' or (any and map[:-1] in spl[0]):
                    maps[i] = sec
                    production.remove(sec)
                    break
            if map == '<>':  # if we find this symbol, change direction
                production = list(reversed(production))
        return (' '.join(maps), production)

# used for direct translation -> some POS tags need to be modified directly
# may modify tree transforms to this as well (improves performance if we have many rules)
# dict means we can use a default dict to store rules -> faster than list

class Category:
    def __init__(self, cat, dict):
        self.name = cat
        if dict:
            self.mappings = defaultdict(str)
        else:
            self.mappings = []   # will hold the mappings for this category of rules

class Mapping:
    def __init__(self, s, t):
        self.source = s
        self.target = t