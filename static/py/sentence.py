from nltk import Tree
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from copy import deepcopy

# this class will have objects describing a sentence from English
# it will have:
# - string rep: the actual string sentence
# - words: an array of word objects
# - syntaxTree: tree structure from Stanford

class EnglishSentence:

    lemmatizer = WordNetLemmatizer()

    #ignore = ['.']

    treeTraversalIndex = 0  # only used to traverse the tree

    def __init__(self, text):
        self.stringRep = text   # keep a reference to the original text
        self.words = []  # list of word objects
        self.syntaxTree = Tree  # syntax tree (unaltered, for reference)
        self.augTree = Tree     # will hold the word objects directly
        self.question = False  # if true then it is a question, false by default
        #.tense = 'present' # can be present, past or future (used to set the time at the start)

    def updateWords(self, posTags, synTree, dependencies, ignore):

        pos = posTags.split(' ')

        i = 1   # will specify the position of the word in the sentence, also used as dictionary key

        for pair in pos:        # go through all the tagged words
            text = pair.split('/')[0]
            tag = pair.split('/')[1]

            if tag not in ignore:     # do not count punctuation as words
                word = Word(text, tag, i, self.lemmatizer)
                #self.words.append(word)
                self.words.append(word)    # add new word

            i+=1

            if text == '?':
                self.question = True

        # after having updated all the words we can reassign the objects to the augmented syntax tree
        # so that they can be modified
        self.syntaxTree = deepcopy(synTree)     # we don't want to modify syntax tree (not by reference, by value)
        self.augTree = synTree

        for i,dep in enumerate(dependencies):
            fst = dep.split(',')[0] # get source node and relation
            snd = dep.split(',')[1] # get target node

            rel = fst.split('(')[0] # get the relation
            source = fst.split('(')[1]  # and source node

            #split = snd.split('-')
            #index = int(split[len(split)-1][:-1]) # get the receiving node's index in the list of words

            #temp_words[index].setDependency((rel, source))  # make tuple

            index = int(source.split('-')[1])

            source_pos = -1

            for word in self.words:
                if word == '?':
                    break
                elif word.index == index:
                    source_pos = self.words.index(word)
                    break

            self.words[i].setDependency((rel, source_pos))

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

    def toString(self):
        print 'Is it a question? ', self.question
        self.augTree.pretty_print()

        for w in self.words:
            w.toString()

    def clear(self):    # reset
        #self.words.clear()
        self.question = False
        self.treeTraversalIndex = 1


# this object will hold the intermediate representation of the sentence i.e. after applying the
# tree transform rules we give the result to this object
# the analyser will then use the original and intermediate representation to perform additional
# analysis, e.g. for dependencies

class IntermediateSentence:
    def __init__(self, words):

        if type(words[-1]) == unicode:     # if the last element is a question mark e.g. remove it
            words = words[:-1]

        self.words = words  # a list of word objects
        self.updateString()  # string representation of the current sentence

    def updateString(self):
        self.word_strings = map(lambda x: str(x), self.words)

    def toUpper(self):
        for i,word in enumerate(self.words):
            if word.root != 'Index':    # do not uppercase Index
                self.words[i].root = word.root.upper()

    def toString(self):
        return ' '.join(map(lambda s: str(s), self.words))

# this object will represent an english word with constructions such as
# - text: actual word
# - POS tag: as from Stanford
# - index: position in the sentence (not array position)
# - depIndex: position of the other word this word is related to, -1 if root
# - root: i.e. it's simplest form e.g. root(trees) = tree, root(swimming) = swim
# - dependency: its role in the sentence

class Word:

    dependency = ''
    modifier = ''   # such as 'very' for adjectives, or 'quickly' for verbs
    category = 'undefined'  # by default

    def __init__(self, text, tag, i, lemmatizer):
        self.POStag = tag
        self.index = i
        self.isUpper = text.isupper() and len(text)>1   # text is considered upper e.g. BBC, but 'I' is not considered
        self.text = text.lower()

        # get roots
        if "'" in text:
            self.rebuild(text)
        elif text.lower() == 'wo':  # should the word be won't -> leads to wo / n't
            self.root = 'will'
        elif self.POStag == 'IN':
            self.root = self.text
        else:
            wn_tag = penn_to_wn(tag)
            self.root = lemmatizer.lemmatize(self.text, pos=wn_tag).lower()
            self.setCategory(wn_tag)

        # do dependencies

    # using wordnet and the postag
    def setCategory(self, postag):
        syn = wn.synsets(self.root, pos=postag)
        if len(syn) > 0:
            #print s, syn[0].lexname()
            self.category = syn[0].lexname()

    def setDependency(self, dep):
        self.dependency = dep

    # IMPORTANT!!! remember to fix the problem "I was born" = "I be bear" == WRONG!!
    def rebuild(self, text):  # should a word begin with ' like 'm, or 'll we rebuild the original i.e. am, will
        if text == "'t" or text == "n't":
            self.root = 'not'
        elif text == "'m":
            self.root = 'am'
        elif text == "'ll":
            self.root = 'will'
        elif text == "'re":
            self.root = 'are'
        elif text == "'ve":
            self.root = 'have'
        else:
            self.root = text.lower()
        # we ignore 's and 'd since we don't gain anything from rebuilding them, the important part is the POS tag

    def toString(self):
        print self.text.encode('ascii'), self.POStag.encode('ascii'), self.category, self.index, self.root.encode('ascii'), \
            self.dependency[0].encode('ascii'), '-->', self.dependency[1]

    # this method will transform any proper noun into fingerspelled format (no need for rules as there are only a coupl
    def fingerSpell(self):
        fingerspell = '-'
        for ch in self.root:
            fingerspell += ch + '-'

        self.root = fingerspell

    # override print method for pretty_print
    def __str__(self):
        return self.root

    def __repr__(self):
        return self.root

def penn_to_wn(tag):
    if tag in ['JJ', 'JJR', 'JJS']:
        return 'a'
    elif tag in ['NN', 'NNS', 'NNP', 'NNPS']:
        return 'n'
    elif tag in ['RB', 'RBR', 'RBS']:
        return 'r'
    elif tag in ['VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VB']:
        return 'v'
    return 'n'


