import re
from collections import defaultdict
from nltk import CFG, Nonterminal, Production
from nltk.parse.generate import generate

class Rules:

    def __init__(self):

        self.tree_transforms = []  # rules to be applied to the syntax trees
        self.direct_translation = defaultdict(lambda: defaultdict(str))  # rules for direct translation

        self.combined_words = defaultdict(list)

        # read the rules from the file

        # first open tree transforms
        self.dir = '../res/rules/'

        f_name = 'tree_transforms.txt'
        try:
            self.readTreeRules(f_name)
        except IOError:
            print 'File '+f_name+' not found'

        # obtain direct translation rules
        f_name = 'direct_translation.txt'
        try:
            self.readDirectRules(f_name)
        except IOError:
            print 'File ' + f_name + ' not found'

        self.readCombinedWords()    # load combined words from signbank
        print self.combined_words

        for k,v in self.direct_translation.iteritems():
            print k
            for k1,v1 in v.iteritems():
                print k1,v1

    def readTreeRules(self, f_name):
        file = open(self.dir + f_name, 'r')
        for line in file:
            if not line.isspace() and line[0] != '/':  # if the line is not empty
                sections = line.split('|')
                source = sections[0].strip()
                target = sections[1].split('//')[0].strip()  # remove comments from second part

                # REMEMBER TO MAYBE CREATE CATEGORIES FOR TREE TRANSFORMS TOO
                if source[:2] != '//':  # if the rule is not commented out, print
                    print source, " | ", target
                self.tree_transforms.append(Mapping(source, target))  # add new rule

        file.close()

    def readDirectRules(self, f_name):
        new_cat = True  # when this is true, we start a new category of direct rules
        current_cat = ''  # the category we are in at the moment
        file = open(self.dir + f_name, 'r')
        for line in file:
            if line.isspace():  # whenever a new category is introduced (space)
                new_cat = True
            else:
                if new_cat:
                    # print 'new category:',line
                    current_cat = line.strip()
                    new_cat = False
                else:  # add rules to the dictionary, no need for Mapping cause we don't change the source
                    src = line.split('->')[0].strip()
                    tgt = line.split('->')[1].split("//")[0].strip()
                    self.direct_translation[current_cat][src] = tgt

        file.close()

    # this method returns a list of of list of words (words that have multiple combinations)
    def readCombinedWords(self):
        f_name = 'signbank_multi.txt'
        try:
            f = open('../res/rules/' + f_name, 'r')
            for line in f:
                split = line.strip().split(' ')
                self.combined_words[split[0]].append(split[1:])
            f.close()
        except IOError:
            print 'File ' + f_name + ' not found'


    def applyTreeTranforms(self, sentence):

        productions = sentence.augTree.productions()  # get the context free grammar for this tree, which we then modify

        # for i in range(len(productions)):
        #    print productions[i]

        print '\nTREE TRANSFORM\n'

        newProductions = []

        # the [:] is because we may want to modify the list
        for prod in productions:  # for each tree generation rule (in the CFG)

            modApplied = False  # if no modification is applied to the rule we add it back normally

            prod_string = str(prod)

            for m in self.tree_transforms:  # for each mapping rule

                source_chunks = m.source.split(' ')   # split the source to apply regex rules

                source_copy = source_chunks[:]        # make a copy

                source = self.rebuildSource(source_copy)  # rebuild the target with unique tags

                match = re.match( r'%s' % source, prod_string) # check for match between source and the current rule

                if match:
                    # if a match exists, create linkage between the source and target for the match groups
                    # (so that correct tags ids and <> can be placed properly)

                    print 'Match:', match.group(), ' | ', m.source

                    target_chunks = m.target.split(' ')     # split the target rule so reassign correct tags
                    # index of each element in the source
                    source_i = self.makeSourceGroupIndexes(source_chunks)
                    # mapping of the above e.g.
                    target_i = self.linkSourceTarget(source_chunks, target_chunks, source_i)

                    # get the new target using the object groups from the match
                    new_target_chunks = self.constructNewTarget(target_chunks, match ,target_i)

                    #print new_target_chunks

                    modApplied = True

                    prod_string = ' '.join(filter(lambda x: len(x) > 0, new_target_chunks))
                    #break  # once a matching rule is found, no need to keep going

            if modApplied:
                # create new production from the new target
                newProductions.append(self.constructProduction(prod_string.split(' ')))  # append new production from target
            else:
                newProductions.append(prod)  # if no modification is applied, push the rule to the new list

        #testing - print old vs new production
        for i in range(len(productions)):
            print productions[i], "\t \t \t", newProductions[i]

        # THEN REBUILD THE SENTENCE
        grammar = CFG(newProductions[0].lhs(), newProductions)

        result = None

        for sent in generate(grammar, n=1):  # only 1 sentence can be generated
            result = sent

        #print result
        return result

    def applyDirectTranslation(self, i_sentence):

        print '\nDIRECT TRANSLATION\n'

        print i_sentence.words

        # go by SPECIAl category, includes word swapping, multiple words etc
        # first apply swap rules

        # will need to be refined for multiple rules, this is not enough
        for i, word in enumerate(i_sentence.words):
            if self.direct_translation['SWAP'][str(word)]:
                if str(word) == 'if':   # if the word is 'if', then we want to make that part a question
                    j=i
                    while j < len(i_sentence.words) and i_sentence.words[j].sent_group == 'SBAR':
                        i_sentence.words[j].is_questioned = True
                        j+=1

                i_sentence.words = i_sentence.words[i:]+i_sentence.words[:i]

        print i_sentence.words
        i_sentence.updateString()

        # for the special case TAGS
        #for k, v in self.direct_translation['TAG'].iteritems():

        # now by multiple words
        for k,v in self.direct_translation['WORDS'].iteritems():
            indexes = subfinder(i_sentence.word_strings, k.split(' '))
            if len(indexes) != 0:
                backtrace = 0
                target = v.split(' ')
                for seq in indexes:
                    j = 0   #index for the target
                    for i in range (seq[0],seq[1]):     # replace those words in the given range
                        t = target[j].strip()
                        if t == '_':       # remove word
                            del i_sentence.words[i-backtrace]
                            backtrace += 1
                        else:
                            i_sentence.words[i-backtrace].root = t
                        j+=1
                i_sentence.updateString()   # update the string representation
        print i_sentence.words

        # go by POS tag category, solely word to word
        i = 0
        for word in i_sentence.words[:]:       # go through all the words in the sentence
            new_word = self.direct_translation[word.POStag][str(word)]
            if len(new_word) != 0:      # if there is a rule
                if new_word == '_':     # if the rule maps to nothing, remove the word
                    i_sentence.words.remove(word)
                    i-=1
                else:
                    i_sentence.words[i].root = new_word
                    i_sentence.words[i].direct_translation = True
            if word.POStag == 'NNP' or word.POStag == 'NNPS' or word.isUpper:   # if the word is proper or stands for something (is all caps)
                word.fingerSpell()
                word.direct_translation = True
            i+=1

    # all the stuff below is for the TREE TRANSFORMATION

    def rebuildSource(self, source_copy):
        for i, s in enumerate(source_copy):  # iterate through all tags in the source
            if s != '<>' and s != '->':
                source_copy[i] += '(_?\d?)'  # every tag which is not -> or <> set a regex match for
                # possible unique id
        source = ' '.join(source_copy)

        source = re.sub('\s<>\s', '(.*\s)', source)
        source = re.sub('\s<>', '(\s?.*)', source)  # set regex match for anything where <> is found

        source += '$'  # match end of string exactly

        return re.sub('~', '([A-Z]*)', source)  # set regex match for tag endings e.g. NN~ can match NNS, NNPS etc

    def makeSourceGroupIndexes(self, source):
        source_i = []
        i = 1
        for s in source:
            if s != '->':
                if s[-1] == '~':  # if tag can be matched to anything, make tuple for match groups
                    source_i.append((i, i + 1))
                    i += 1
                else:
                    source_i.append(i)
                i += 1

        return source_i

    def linkSourceTarget(self, source, target, source_i):
        print source, target, source_i
        target_i = []
        i = -1
        backtrace = 0  # used if our match is further on in the rule
        needs_backtrace = False
        seen_tags = []  # will store the tags seen (for backtracing)
        last_point = 0
        skip = 0
        for t in target:  # iterate through all target tags
            for s in source[:]:  # for each source tag
                if t == '->':  # ignore ->
                    continue
                if s != '->':  # if the source tag is not -> increase index by one (to obtain group index from source_i)
                    i += 1
                else:
                    source.remove(s)  # otherwise remove it as it's not needed
                    continue  # skip the stuff below
                #print t, s, i, backtrace
                if t == s or t == '_':  # if the two tags match
                    #print source_i, len(source_i), i
                    if s in seen_tags:
                        target_i.append(source_i[i])
                        seen_tags.remove(s)
                    else:
                        target_i.append(source_i[i + skip])  # add the corresponding group index to the target position
                    if i == last_point and skip > 0:
                        i += skip - 1
                        skip = 0
                    if needs_backtrace:  # if the tag was found further in the list, reset the backtrace
                        i = i - backtrace - 1
                        skip = backtrace
                        backtrace = 0
                        #print 'resetting index and backtrace', i, backtrace
                    source.remove(s)  # remove the source tag found
                    needs_backtrace = False
                    #print target_i, source
                    break
                else:
                    if s != '->' and t != '->':  # if both source and target tags are not -> then it means the tag we're looking for is further awat
                        #print 'setting backtrace'
                        seen_tags.append(s)
                        if not needs_backtrace:
                            needs_backtrace = True
                            last_point = i + 1
                        backtrace += 1
                #print target_i, source

        return target_i

    def constructNewTarget(self, target, match, target_i):
        # go through each group and assign it to the target as explained
        i = 0  # this index is used to get the index of the group
        new_target = []
        for j, t in enumerate(target):  # for each target tag
            if t != '->':  # if the tag is not ->
                #print t
                if t[-1] == '~':
                    new_target.append(t[:-1] + match.group(target_i[i][0]) + match.group(
                        target_i[i][1]))  # set the tuple (tag + tuple)
                elif t == '<>':
                    #target[j] = match.group(target_i[i]).strip()  # replace all the tags in the group as it's a <>
                    tags = match.group(target_i[i]).split(' ')
                    new_target.extend(tags)
                else:
                    #print 'tar: ', target_i[i]
                    if t != '_':
                        new_target.append(t + match.group(target_i[i]))  # append the id to the tag
                i += 1
            else:
                new_target.append(t)
        return new_target

    def constructProduction(self, target):
        # construct nonterminal objects from target

        print 'New target', ' '.join(target)

        productionObjects = []
        for tag in target:
            if len(tag) > 0 and tag != '_' and tag != '->':
                # print section
                productionObjects.append(Nonterminal(tag))
        # now construct the production object from the nonterminals
        return Production(productionObjects[0], productionObjects[1:])  # return the modified rule to the list

    def applyCombinedWords(self, words):

        print '\nCOMBINED WORDS\n'

        i = 0
        while i < len(words)-1:
            if self.combined_words[words[i].root]:  # if the first word is found in the file, check if the following matches
                for sequence in self.combined_words[words[i].root]:
                    match = True
                    for j, word in enumerate(sequence):  # one sequence may have more than 1 word e.g. Not [give, a , damn]
                        if 1+i+j < len(words):  # prevent index error
                            if word != words[1 + i + j].root:
                                match = False
                                break
                        else:
                            match = False
                            break
                    if match:
                        words[i].root += '-' + '-'.join(sequence)  # create new combined word
                        # then delete all the ones that are in the sequence
                        for j in range(len(sequence)):
                            del words[1+i]
                        break
            i+=1

def subfinder(mylist, pattern):
    return [(i, i + len(pattern)) for i in range(len(mylist)) if mylist[i:i + len(pattern)] == pattern]

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