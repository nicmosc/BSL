from nltk import Tree
from static import APP_NLTK_DATA
import nltk
from copy import deepcopy
from terminaltables import AsciiTable
from utils import formatNumber, abbreviateMonth, findGender, toUpper
from collections import defaultdict
from itertools import takewhile
from re import compile, escape, sub
import json

# this class will have objects describing a sentence from English
# it will have:
# - string rep: the actual string sentence
# - words: an array of word objects
# - syntaxTree: tree structure from Stanford

class EnglishSentence:

    nltk.data.path = []

    nltk.data.path.append(APP_NLTK_DATA)
    print nltk.data.path

    lemmatizer = nltk.stem.WordNetLemmatizer()

    #ignore = ['.']

    treeTraversalIndex = 0  # only used to traverse the tree

    def __init__(self, text):
        self.stringRep = text   # keep a reference to the original text
        self.words = []  # list of word objects
        self.syntaxTree = Tree  # syntax tree (unaltered, for reference)
        self.augTree = Tree     # will hold the word objects directly
        self.question = False  # if true then it is a question, false by default
        self.exclamation = False    # if true then it will be signed faster and with wider eyes

        self.subSentences = defaultdict(list)  # will contain the sentence groups words belong to as well as the tense of the subsentence
        # it will be kept for the JS data, not for the simple gloss
        self.sentence_tenses = []   # specify the tenses of the above group
        self.dependency_groups = []     # contains the dependency group ids (so we dont repeat them)

        #.tense = 'present' # can be present, past or future (used to set the time at the start)

    def updateWords(self, posTags, synTree, dependencies, ignore):

        pos = posTags.split(' ')

        i = 1   # will specify the position of the word in the sentence, also used as dictionary key

        for pair in pos:        # go through all the tagged words
            text = '/'.join(pair.split('/')[:-1])
            tag = pair.split('/')[-1]

            print tag

            if tag not in ignore:     # do not count punctuation as words
                word = Word(text, tag, i)
                #self.words.append(word)
                self.words.append(word)    # add new word

            i+=1

            if text == '?':
                self.question = True
            if text == '!':
                self.exclamation = True

        # after having updated all the words we can reassign the objects to the augmented syntax tree
        # so that they can be modified
        self.syntaxTree = deepcopy(synTree)     # we don't want to modify syntax tree (not by reference, by value)
        self.augTree = synTree

        for dep in dependencies:
            fst = dep.split(',')[0] # get target node and relation

            snd = dep.split(',')[1] # get the source node

            rel = fst.split('(')[0] # get the relation
            target = fst.split('(')[1]  # and target node

            target_index = int(target.split('-')[-1])
            source_index = int(snd.split('-')[-1].strip(')'))

            target_pos = -1
            source_pos = -1

            for word in self.words:     # look for the target
                if word == '?':
                    break
                elif word.index == target_index:
                    target_pos = self.words.index(word)     # get the target position
                elif word.index == source_index:
                    source_pos = self.words.index(word)     # get the source position

            # we set the dependency for the word, and pass it the already existing dependency groups to avoid repetition
            self.words[source_pos].setDependency(rel, self.words[target_pos], self.dependency_groups)

    def traverseReplaceWords(self, tree, seenLabels):
        for index, subtree in enumerate(tree):
            if type(subtree) == Tree:

                # if the label of the node already exists, make it unique
                newLabel = subtree.label()
                count = seenLabels.count(newLabel)
                seenLabels.append(newLabel)
                if count > 0:
                    newLabel += '_' + str(count)
                    tree[index].set_label(newLabel)

                # continue traversing the tree
                self.traverseReplaceWords(subtree, seenLabels)
            else:        # if we reach the leaf
                subtree = self.words[self.treeTraversalIndex]
                self.treeTraversalIndex +=1 # increase index
                tree[index] = subtree

    # assigns the sentence tag to the words that fall within it -> used to modify sentence sections individually
    def setSentenceGroups(self, tree):
        for subtree in tree:
            if type(subtree) == Tree:
                group = subtree.label().split('_')[0]
                if group in ['S', 'SBAR', 'SBARQ', 'SINV', 'SQ']:
                    #if subtree.label() not in self.subSentences:
                    #    self.subSentences.append(subtree.label())
                    for word in subtree.leaves():
                        if word.sent_group.split('_')[0] == 'S' or word.sent_group == '':    # if the word gorup is a generic sentence, update, otherwise
                            word.sent_group = subtree.label()       # leave it (we want to keep everything under SBAR etc)

                self.setSentenceGroups(subtree)

    def setTenses(self):
        # for each word we encounter, while we're still in the same sentence group, we check what combination of verbs there are
        # to determine the temporal topic of the sentence

        temp_verb_dict = defaultdict(list)      # will hold the roots
        for word in self.words:
            if word.POStag[:2] == 'VB' or word.POStag == 'MD':
                print word.POStag
                self.subSentences[word.sent_group]+=[word.POStag]
                temp_verb_dict[word.sent_group]+=[word.root]

        print self.subSentences
        print temp_verb_dict
        # now check for tense specific constructs
        # rework this - BROKEN
        for k,v in self.subSentences.iteritems():
            print v
            tense = None
            if v in [['VBD', 'VBG'],['VBD'],['VBZ', 'VBN'], ['VBP','VBN'], ['VBD', 'VB']]:
                tense = 'past'
            elif v == ['VBZ', 'VBG']:
                tense = 'future'
            elif v[0] == 'MD' and temp_verb_dict[k][0] not in ['have', 'can']:
                tense = 'future'

            if tense: self.subSentences[k] = tense
            else: self.subSentences[k] = ''

    def toString(self):
        print 'Is it a question? ', self.question
        print 'Subsentence groups ', self.subSentences
        self.augTree.pretty_print()

        # nicely prints all the details of the words
        table_data = [['i','Word', 'POS', 'S-group', 'WN Category', 'Root','dep', 'dep-group','target', 'num_modified','negated','questioned']]

        for w in self.words:
            info = w.toString()
            # get the word the dependency is related to (only for display clarity)
            table_data.append(info)

        table = AsciiTable(table_data)
        print table.table

    def clear(self):    # reset
        #self.words.clear()
        self.question = False
        self.treeTraversalIndex = 1


# this object will hold the intermediate representation of the sentence i.e. after applying the
# tree transform rules we give the result to this object
# the analyser will then use the original and intermediate representation to perform additional
# analysis, e.g. for dependencies

class IntermediateSentence:
    def __init__(self, words, e_sentence):

        self.question = e_sentence.question
        self.sentenceGroups = e_sentence.subSentences

        self.words = words  # a list of word objects
        if e_sentence.exclamation:
            self.words[0].intense = True
        #elif self.question:
        #    self.words[0].is_questioned = True

        self.updateString()  # string representation of the current sentence

    def updateString(self):
        self.word_strings = map(lambda x: str(x), self.words)

    def toString(self):
        # nicely prints all the details of the words
        table_data = [['i', 'Word', 'POS', 'S-group', 'WN Category', 'Root', 'dep', 'dep-group','target','num_modified', 'negated', 'questioned']]

        for w in self.words:
            info = w.toString()
            table_data.append(info)

        table = AsciiTable(table_data)
        print table.table

    # this method will cover anything which couldnt be handled with external rules
    def specialCases(self):

        # for testing
        print "\nSPECIAL CASES\n"
        print map(lambda x: str(x.sent_group), self.words)

        # in case the word is a number we look for other number words to format it
        # this is done before the general loop as we may extensively modify the list
        # first look for other CDs in case the number is a combination of words e.g. thirty five
        self.formatNumbers()

        i = 0
        while i < len(self.words):

            word = self.words[i]

            # this handles the case that the noun is a location and the previous word is 'in' or 'at', we need WHERE
            #if word.category in ['noun.location', 'noun.artifact', 'noun.object', 'noun.group'] and i > 0:
            if word.category in ['noun.location'] and i > 0:
                if self.words[i - 1].root in ['in', 'at']:
                    if word.sent_group not in ['SBARQ', 'SQ']:
                        self.words[i - 1].root = 'where'
                    else:
                        del self.words[i-1]
                        i -=1
                    # self.facial_expression = '[q]'      # set it as a question
            else:
                if self.words[i - 1].root == 'at':
                    del self.words[i-1]
                    i -= 1

            # in this case if we use an abbreviated version of "Have you not eaten?" = "Haven't you eaten?" we must flip the
            # words for them to work in BSL
            if word.text == "n't" and self.question and self.words[i+1].POStag == 'PRP':
                self.words[i] = self.words[i+1]
                self.words[i+1] = word

            # this handles the case of numbers + other elements
            if word.POStag == 'CD':
                # the age case and money
                if i < len(self.words) - 1:     # if not the last element of the sentence
                    if self.words[i + 1].root in ['age', 'pound', 'euro', 'dollar']:
                        # self.words[i+1].facial_expression = '[q]'  # also set this as a question
                        self.words[i] = self.words[i + 1]
                        self.words[i + 1] = word

                if i > 0:                       # if not the first element of the sentence
                   if self.words[i-1].root in ['in', 'on']:
                        del self.words[i-1]
                        i -=1

            # handles subordinating conjunction 'that'
            if word.root == 'that' and word.sent_group == 'SBAR':
                del self.words[i]
                i -= 1

            # as 'that' is changed to index, if that is not a determiner, we want to keep the sign for that
            if word.root == 'ix' and word.text == 'that' and word.dependency[0] != 'det':
                word.root = 'that'

            # we also insert a 'IX' whenever a name is the subject
            if word.POStag == 'NNP' and word.dependency[0] == 'nsubj':
                print 'inserting IX'
                new_word = Word('ix', 'PRP', -word.index)     # create new index word object
                new_word.dep_group = word.dep_group
                new_word.dependency = word.dependency
                new_word.sent_group = word.sent_group
                new_word.is_questioned = word.is_questioned
                word.dependency = ('name', word.dependency[1])
                self.words.insert(i+1, new_word)          # insert at correct index

            if self.sentenceGroups[word.sent_group] == 'past-finished':     # in this case we insert a keyword to say the action is finished
                pass

            if word.POStag == 'NNS' and word.category != 'noun.body' \
                    and word.text != word.root and not word.num_modified and not word.direct_translation and word.specific:
                    #self.words.insert[i+1] += ' them'
                    print 'inserting THEM'
                    new_word = Word('them', 'PRP', -word.index)  # create new index word object
                    new_word.dep_group = word.dep_group
                    new_word.dependency = ('plural', word)
                    new_word.sent_group = word.sent_group
                    new_word.is_questioned = word.is_questioned
                    #word.dependency = ('name', word.dependency[1])
                    self.words.insert(i + 1, new_word)  # insert at correct index

            # this handles the time case i.e. whenever we mention yesterday, today, in a week etc
            if word.category == 'noun.time' and i > 0:
                if self.words[i-1].root in ['in', 'on']:      # remove the "on monday"
                    del self.words[i-1]
                    i -=1
                # move the word (or word group) to the beginning of the sentence group
                s_group = word.sent_group
                for j, w in reversed(list(enumerate(self.words[:i]))):
                    #print j, w, i, word, w.sent_group, s_group
                    if w.sent_group != s_group or j == 0:  # if we reached the end of the sentence group or the beginning of the sentence
                        if j != 0:  # if we didnt reach the end of the sentence, set j up 1
                            j += 1
                        # we insert the dependency group / word at j
                        group = [word]
                        self.words.remove(word) #remove from words
                        for _w in self.words[:]:
                            print 'checking',_w
                            if _w.dep_group == word.dep_group and word.dep_group != None:  # if the word is in the same sentence group, the group is not null and it's not the same word
                                print word,'in group',_w
                                group.append(_w)
                                print 'removing',_w
                                self.words.remove(_w)

                        print 'dep group',group
                        # now insert the group of words at the correct position
                        #self.words.insert(j, self.words.pop(i))  # move word to the desired location
                        self.words = self.words[:j] + group + self.words[j:]
                        print self.words
                        break
            i+=1

    def formatNumbers(self):
        numFound = False
        baseNum = None
        i = len(self.words)
        for word in self.words[:]:
            # print baseNum, i, len(self.words)-1
            if word.POStag == 'CD':
                if numFound:
                    baseNum.root += ' ' + word.root
                    self.words.remove(word)  # remove as you go
                else:
                    numFound = True
                    baseNum = word
            if numFound:  # if all numbers have been found
                if word.POStag != 'CD' or i == 1:  # if we reached the end of the list, or the end of the compound number
                    baseNum.root = formatNumber(baseNum.root)  # format the new compound number
                    numFound = False
            i -= 1

        print self.words

    def countIndexes(self):     # this function sets the index numbers e.g. index_1 index_2 if those are separate entities
        print '\nCOUNTING INDEXES\n'

        indexes = []        # will be of the form [(1, male, False), (1, male True), (2, None, False)] where False means...

        for word in self.words:
            if word.root == 'ix':
                # if word.dependency[0] == 'det':
                #     word.root+='_'+str(indexes[-1])      # set the index to the last found id
                #     indexes.append(indexes[-1]+1)
                new_id = 0
                if word.index < 0:      # if the index refers to someone's name
                    for n in self.words:
                        if n.index == -word.index:
                            gender = findGender(n.text)
                            print word.root,gender
                            addIndex(indexes, gender, True)     # True if is referring to a noun ( then it's a different person)
                else:   # if the index represents a determiner or a personal pronoun
                    gender = None
                    if word.text in ['he', 'him']:
                        gender = 'male'
                    elif word.text in ['she', 'her']:
                        gender = 'female'
                    # else the word is an object (determiner)
                    addIndex(indexes, gender, False)

                word.root += '_'+str(indexes[-1][0])      # set the index to the last found id
            elif word.root == 'her':
                word.root = addPoss(indexes,gender='female')
            elif word.root == 'his':
                word.root = addPoss(indexes,gender='male')
            elif word.root == 'its':
                word.root = addPoss(indexes,gender=None)
                # this method will take the skeleton of the BSL output, that is something like MY -M-F- LIVE WHERE -E-S-S-E-X-

    def resetWordPositions(self):
        i = 0
        for word in self.words:
            word.index = i
            i+=1

    # return the BLS data
    def setNonManualFeatures(self):  # will generate both the text gloss and the JS object

        print '\n SETTING FACIAL EXPRESSIONS \n'

        # insert facial expressions e.g. hn, q, pause between groups, questions, tenses etc, negations
        # should also separate between facial expressions that affect a sentence group, and those which affect individual words

        # reminder: tenses and nsubj are not shown in the gloss

        c_tags = []

        aug_sentence = self.traverseContainers(self.words, -1, c_tags)

        # this is a bit of a hack but necessary
        if 'q' not in c_tags and self.question:     # if the sentence is a question but no q tag was inserted, wrap everything into a question
            aug_sentence = [Container(aug_sentence, 'q', True)]

        return (aug_sentence, self.words)

    def traverseContainers(self, sentence, container_length, c_tags):
        if container_length == -1:  # initial case, start with no containers and no tags
            print 'Initial case'
            new_sent, new_length = self.setContainers(sentence, c_tags)
            print new_sent, new_length
            return self.traverseContainers(new_sent, new_length, c_tags)
        elif container_length == 0:  # stop when we have no more containers to check
            print 'done'
            return sentence
        else:
            print 'more to traverse'
            # print sentence.words, container_length
            for c in sentence:
                if isinstance(c, Container):  # if it's a container
                    print 'word is a container', str(c), c.words, c.tag
                    c_tags.append(c.tag)
                    new_sent, new_length = self.setContainers(c.words, c_tags)
                    print new_sent, new_length
                    c.words = new_sent
                    self.traverseContainers(c.words, new_length, c_tags)

            return sentence

    def setContainers(self, words, container_tags):

        container_list = []
        containers_left = 0
        i = 0

        # special var for dep groups
        notify = (False, -1)

        while i < len(words):

            # to insert pauses between dependency groups
            if words[i].dep_group != None and words[i].dep_group not in container_tags and not notify[0]:
                print words[i]
                notify = (True, words[i].dep_group)

            if words[i].dep_group != notify[1] and notify[0]:       # if the dep group is different and notify is enabled
                if isinstance(container_list[-1], Word):
                    del container_list[-1]      # delete the word regardless if it was part of something else
                    container_list.append(Container([words[i - 1]], notify[1], False, mod=True))

                notify = (False, -1)        # reset notify

            if words[i].intense and 'intense' not in container_tags:
                container_list.append(Container(words, 'intense', False))     # plays open eyes throughout the sentence
                i = len(words)

            # elif words[i].is_questioned and words[i].sent_group == 'S' and 'q' not in container_tags:
            #     container_list.append(Container(words, 'q', True))
            #     i = len(words)

            # if the word begins a question sequence
            elif words[i].is_questioned and 'q' not in container_tags:
                temp_list = list(
                    takewhile(lambda x: x.is_questioned, words[i:]))  # get all words in that sequence
                container_list.append(Container(temp_list, 'q', True))
                print container_list
                i += len(temp_list) - 1

            # if the word begins a negation sequence
            elif words[i].is_negated and 'neg' not in container_tags:
                temp_list = list(
                    takewhile(lambda x: x.is_negated, words[i:]))  # get all words in that sequence
                container_list.append(Container(temp_list, 'neg', True))
                i += len(temp_list) - 1
            # setting the tenses for the sentence group the word is part of
            elif self.sentenceGroups[words[i].sent_group] not in container_tags\
                    and len(self.sentenceGroups[words[i].sent_group]) != 0 :      # if there is a tense (most often there is, except present)
                tense = self.sentenceGroups[words[i].sent_group]
                print 'tense',tense
                temp_list = list(takewhile(lambda x: x.sent_group == words[i].sent_group, words[i:]))
                container_list.append(Container(temp_list, tense, False))
                i += len(temp_list) - 1

            elif words[i].sent_group in ['SQ'] and 'q' not in container_tags:  # maybe add SINV?
                temp_list = list(takewhile(lambda x: x.sent_group in ['SQ', 'SBARQ'],
                                           words[i:]))  # get all words in that sequence
                container_list.append(Container(temp_list, 'q', True))
                i += len(temp_list) - 1

            elif words[i].root in ['who', 'why', 'when', 'how', 'what'] and 'q' not in container_tags\
                    and words[i].sent_group in ['SQ', 'SBARQ','SBAR']:
                container_list.append(Container([words[i]], 'q', True))
            #elif words[i].root in ['who', 'where', 'why', 'when', 'how', 'what'] and 'q' not in container_tags:
            elif words[i].root == 'where' and 'q' not in container_tags:
                container_list.append(Container([words[i]], 'q', True))
            elif words[i].dependency[0] == 'nsubj' and 'hn' not in container_tags:      # adds a head nod for subject
                container_list.append(Container([words[i]], 'hn', False))
            elif words[i].POStag == 'JJR' and 'cp' not in container_tags:
                container_list.append(Container([words[i]], 'cp', False, mod=True))  # comparative
            elif words[i].POStag == 'JJS' and 'sp' not in container_tags:
                container_list.append(Container([words[i]], 'sp', False, mod=True))  # superlative
            else:
                print words[i], words[i].dependency
                container_list.append(words[i])
                containers_left -= 1  # decrease the number of containers if no new ones were added
            containers_left += 1
            i += 1
            #print container_list

        return container_list, containers_left

def addPoss(indexes, gender):
    latest = 0
    for tpl in indexes:
        if tpl[0] > latest: latest = tpl[0]
        if tpl[1] == gender:
            #print tpl[0]
            return 'poss_'+str(tpl[0])

    return 'poss_'+str(latest+1)

def addIndex(indexes, gender, name):
    latest = 0
    print indexes
    for tpl in indexes:
        if tpl[0] > latest:
            latest = tpl[0]
        if gender == tpl[1] and gender != None and name != tpl[2]:
            indexes.append(tpl)
            return
        elif gender == tpl[1] and gender != None and name == tpl[2]:
            if name == True:
                break
            else:
                indexes.append(tpl)
                return

    # if we don't find the same info, add a new entity
    indexes.append((latest+1, gender, name))

# this object simply contains the final information required to construct the gloss and js objects
class BSLSentence:

    def __init__(self, data):
        self.word_objects = data[0]
        self.word_list = data[1]

    # returns simple text representation
    def toGlossText(self, html=False):
        if html:
            return ' '.join([w.__str__(html=True) if isinstance(w, Word) else w.__str__(html=True) for w in self.word_objects])
        else:
            return ' '.join([str(w).upper() if isinstance(w, Word) else str(w) for w in self.word_objects])

    def toGlossHTML(self, gloss=None):
        # if gloss is given use it directly
        if not gloss: gloss = self.toGlossText(html=True)

        temp_gloss = ''
        i = 0
        while temp_gloss != gloss:
            temp_gloss = gloss
            gloss = gloss.replace('?', str(i),1)
            i+=1

        print gloss

        rep = {'(': '<over>', ')': '</over>', '[': '<sup> ', ']': '</sup>'}  # define desired replacements here

        # use these three lines to do the replacement
        rep = dict((escape(k), v) for k, v in rep.iteritems())
        pattern = compile("|".join(rep.keys()))
        html = pattern.sub(lambda m: rep[escape(m.group(0))], gloss)

        return html

    # will need to make a toJS method
    def toJS(self):

        word_index_js = []      # will contain the words in order

        # first split all future files with paths and indexes
        for w in self.word_list:
            obj = {}
            if w.root[0] == '-' and w.root[-1] == '-':  # if the word is finger spelled
                for letter in w.root.split('-'):
                    if letter != '':
                        obj['name'] = letter.upper()
                        obj['index'] = w.index
                        if letter.isdigit():
                            obj['path'] = 'numbers'
                        else:
                            obj['path'] = 'alphabet'
                        word_index_js.append(json.dumps(obj))
            else:
                obj['name'] = w.root
                obj['index'] = w.index
                obj['path'] = 'words/'+w.root[0]  # arranged in alphabetical order
                word_index_js.append(json.dumps(obj))

        # now get the non_manual stuff

        mod = [[] for _ in xrange(len(self.word_list))]     # list of lists of modifiers e.g. BIG can have modifier cp or sp (and pause)
        non_man = [([],[]) for _ in xrange(len(self.word_list))]   # possible non manual object for each element
        '''
        example for the above in ((tomorrow rain)[past])[q], (tonight (me)[hn] (not go)[neg] beach)[future]
        >>> non_man = [([q, past],[]),([],[q, past]), ([future],[]), ([hn],[hn]), ([neg],[]), ([],[neg]), ([],[future])]
                               0            1               2               3           4          5            6
        '''
        container_list = self.treeToList(self.word_objects, containers=[])
        self.getAllLeaves(container_list, non_man, mod)

        temp_obj = {}
        temp_obj['anims'] = [x.tag for x in container_list if not x.modifier]
        non_man_obj = json.dumps(temp_obj)  # contains a list with all the non_manuals required (to be loaded as clips in JS)

        non_man_js = []
        mod_js = []

        for tpl in non_man:
            obj = {}
            obj['start'] = tpl[0]
            obj['end'] = tpl[1]
            non_man_js.append(json.dumps(obj))

        for mods in mod:
            obj = {}
            obj['modifiers'] = mods
            mod_js.append(json.dumps(obj))

        return (word_index_js,non_man_obj,non_man_js,mod_js)        # return the three lists for JS

    def treeToList(self, objects, containers):
        for obj in objects:
            if isinstance(obj, Container):
                containers.append(obj)
                self.treeToList(obj.words, containers)
        return containers

    def getAllLeaves(self, container_list, non_man, mod):
        # go through all the containers and get the leaves i.e. the indexes
        for container in container_list:
            indexes = list(container.flatten())
            if container.modifier:
                tag = container.tag
                if isinstance(tag, int): tag = 'pause'
                mod[indexes[0]].append(tag)
            else:
                indexes = list(container.flatten())
                start_index = indexes[0]
                end_index = indexes[-1]
                non_man[start_index][0].append(container.tag)
                non_man[end_index][1].append(container.tag)

# this object will represent an english word with constructions such as
# - text: actual word
# - POS tag: as from Stanford
# - index: position in the sentence (not array position)
# - depIndex: position of the other word this word is related to, -1 if root
# - root: i.e. it's simplest form e.g. root(trees) = tree, root(swimming) = swim
# - dependency: its role in the sentence

class Word:

    dependency = ''     # the dependency is a tuple (relation, reference to word the relation is applied to)
    modifier = ''   # such as 'very' for adjectives, or 'quickly' for verbs
    category = 'undefined'  # by default
    sent_group = ''         # the 'sub' sentence the word belongs to
    dep_group = None          # the dependency group the word belongs to
    num_modified = False    # the number modification that a word has on this particular word
    direct_translation = False
    intense = False
    specific = False        # if the word is denoted by a determiner e.g. The dogs is specific, dogs is not, used to insert 'THEM'

    #facial_expr = ''        # the facial expression associated with the word
    is_negated = False      # if the word is connected to a neg, it is negated (used for nouns, verbs, adjectives)
    is_questioned = False   # if word is part of a question

    def __init__(self, text, tag, i):
        self.POStag = tag
        self.index = i
        self.isUpper = text.isupper() and len(text)>1   # text is considered upper e.g. BBC, but 'I' is not considered
        self.text = text.lower()
        self.is_negated = False     # by default
        self.num_modified = False

        # get roots
        if "'" in text:
            self.rebuild(text)
        elif text.lower() == 'wo':  # should the word be won't -> leads to wo / n't
            self.root = 'will'
        elif text.lower() == 'ca':
            self.root = 'can'
        elif self.POStag == 'IN':
            self.root = self.text
        else:
            wn_tag = penn_to_wn(tag)
            # if wn_tag != None:
            #     print 'before lemmatizer'
            #     self.root = EnglishSentence.lemmatizer.lemmatize(self.text, pos=wn_tag).lower()
            #     self.setCategory(wn_tag)
            #     print 'after lemmatizer'
            # else:
            self.root = self.text
            # after getting the cateogory
            if isMonth(self.text):
                self.root = abbreviateMonth(self.text)
            elif isDay(self.text):
                self.root = self.text[0] + self.text[0]

        # do dependencies

    # using wordnet and the postag
    def setCategory(self, postag):
        syn = nltk.corpus.wordnet.synsets(self.root, pos=postag)
        if len(syn) > 0:
            #print s, syn[0].lexname()
            self.category = syn[0].lexname()

    # handle all the dependency stuff
    def setDependency(self, rel, target, dep_groups):

        # if it's a negation, we modify the source word, saying it is negated
        if rel == 'neg':
            target.is_negated = True       # set both the target and the negation as facially negated
            self.is_negated = True

        elif rel == 'det':
            target.specific = True

        elif rel in ['amod','advmod','case']: # (maybe also conj?)
            if target.dep_group:    # if a group already exists, use the same
                self.dep_group = target.dep_group
            elif self.dep_group:        # similarly the other way around
                target.dep_group = self.dep_group
            else:                   # otherwise create a new one and link
                if len(dep_groups) > 0:
                    self.dep_group = dep_groups[-1]+1
                else:
                    self.dep_group = 1
                target.dep_group = self.dep_group
                dep_groups.append(self.dep_group)       # update the total groups

            if self.is_negated: target.is_negated = True
            elif target.is_negated: self.is_negated = True

        elif rel == 'nummod':
            target.num_modified = True

        self.dependency = (rel, target)

        # this must happen afterwards, otherwise we don't record the change correctly
        if rel == 'conj':  # if the word is directly related to another one, we basically copy them
            self.dependency = target.dependency

    # IMPORTANT!!! remember to fix the problem "I was born" = "I be bear" == WRONG!!
    def rebuild(self, text):  # should a word begin with ' like 'm, or 'll we rebuild the original i.e. am, will
        if text == "'t" or text == "n't":
            self.root = 'not'
        elif text == "'m":
            self.root = 'be'
        elif text == "'ll":
            self.root = 'will'
        elif text == "'re":
            self.root = 'be'
        elif text == "'ve":
            self.root = 'have'
        elif text == "'s" and self.POStag == 'VBZ':
            self.root = 'be'
        else:
            self.root = text.lower()
        # we ignore 's and 'd since we don't gain anything from rebuilding them, the important part is the POS tag

    def toString(self):

        return [self.index, self.text.encode('ascii'), self.POStag.encode('ascii'), self.sent_group, self.category, self.root.encode('ascii'), \
            self.dependency[0].encode('ascii'),self.dep_group, self.dependency[1].root, self.num_modified ,self.is_negated, self.is_questioned]

    # this method will transform any proper noun into fingerspelled format (no need for rules as there are only a coupl
    def fingerSpell(self):
        fingerspell = '-'
        for ch in self.root:
            fingerspell += ch + '-'

        self.root = fingerspell

    # override print method for pretty_print
    def __str__(self, html=False):
        if html:
            if self.root[0] == '-' and self.root[-1] == '-':
                res = ''
                for let in self.root.split('-')[1:-1]:
                    res += '-<span id="?">'+let.upper()+'</span>'
                res += '-'
                return res
            return '<span id="?">'+self.root.upper()+'</span>'
        return self.root

    def __repr__(self, html=False):
        if html:
            if self.root[0] == '-' and self.root[-1] == '-':
                res = ''
                for let in self.root.split('-')[1:-1]:
                    res += '-<span id="?">' + let.upper() + '</span>'
                res += '-'
                return res
            return '<span id="?">' + self.root.upper() + '</span>'
        return self.root

def isMonth(word):
    return word in ['january', 'february', 'march', 'april', 'may', 'june', 'july','august','september','october','november','december']

def isDay(word):
    return word in ['monday','tuesday','wednesday','thursday','friday','saturday', 'sunday']

def penn_to_wn(tag):
    if tag in ['JJ', 'JJR', 'JJS']:
        return 'a'
    elif tag in ['NN', 'NNS', 'NNP', 'NNPS']:
        return 'n'
    elif tag in ['RB', 'RBR', 'RBS']:
        return 'r'
    elif tag in ['VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VB']:
        return 'v'
    return None

# this object will contain a word / list of words (in order) together with a 'tag' that goes with them e.g.
# (YOU) [hn] -> object has [YOU] and tag hn, also (NOT GO) [neg] as well etc.
# if we have multiple containers e.g.
class Container:

    def __init__(self, words, tag, show, mod = False):     # takes a list of words (can also include containers and the tag for those words
        self.show_gloss = show                     # if the container is printed as part of the gloss
        self.words = words
        self.tag = tag
        self.modifier = mod             # by default the container does not modify the word(s), but plays a non-manual sign in parallel
                                        # if we want to modify the sign itself, we make modifier = true
    def __str__(self, html=False):
        if self.show_gloss:
            return self.__repr__(raw=False, html=html)
        else:
            #return ' '.join(map(lambda x: str(x), self.words))
            if html:
                return ' '.join([w.__str__(html=True) if isinstance(w, Word) else w.__str__(html=True) for w in self.words])
            return ' '.join([str(w).upper() if isinstance(w, Word) else str(w) for w in self.words])

    def __repr__(self, raw = True, html=False):      # if we want the raw representation, we print everything, otherwise only the show gloss ones
        if raw and not html: return '(' + ' '.join(map(lambda x: repr(x), self.words)) + ')' + '[' + str(self.tag) + ']'

        elif html: return '('+' '.join([w.__str__(html=True) if isinstance(w, Word) else w.__str__(html=True) for w in self.words])+ ')' + '[' + str(self.tag) + ']'

        return '('+' '.join([str(w).upper() if isinstance(w, Word) else str(w) for w in self.words])+ ')' + '[' + str(self.tag) + ']'
        #return str(self.words)
        # else: return '(' + ' '.join(map(lambda x: str(x), self.words)) + ')' + '[' + str(self.tag) + ']'

    # this method returns a list of word indexes contained in this container (also words in sub containers)
    def flatten(self):
        return self.flatten_(self.words)
    def flatten_(self, l):
        for el in l:
            if isinstance(el, Container):
                for sub in self.flatten_(el.words):
                    yield sub
            else:
                yield el.index