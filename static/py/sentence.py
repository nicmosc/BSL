from nltk import Tree
from nltk.stem.wordnet import WordNetLemmatizer

# this class will have objects describing a sentence from English
# it will have:
# - string rep: the actual string sentence
# - words: an array of word objects
# - syntaxTree: tree structure from Stanford

class EnglishSentence:

    lemmatizer = WordNetLemmatizer()

    def __init__(self, text):
        self.stringRep = text   # keep a reference to the original text
        self.words = []  # an array of word objects
        self.syntaxTree = Tree
        self.question = False  # if true then it is a question, false by default

    def updateWords(self, posTags, dependencies):

        pos = posTags.split(' ')

        print dependencies

        i = 0   # will specify the position of the word in the sentence

        for pair in pos:        # go through all the tagged words
            text = pair.split('/')[0]
            tag = pair.split('/')[1]

            if(tag != '.'):     # do not count punctuation as words
                word = Word(text, tag, i, self.lemmatizer)
                self.words.append(word)
                i+=1

            if text == '?':
                self.question = True

    def toString(self):
        print 'Is it a question? ', self.question
        self.syntaxTree.pretty_print()

        for word in self.words:
            word.toString()

    def clear(self):
        self.words = []
        self.question = False

# this object will represent an english word with constructions such as
# - text: actual word
# - POS tag: as from Stanford
# - index: position in the sentence
# - depIndex: position of the other word this word is related to, -1 if root
# - root: i.e. it's simplest form e.g. root(trees) = tree, root(swimming) = swim
# - dependency: its role in the sentence
# if the word is an adjective we want to know if it's a superlative, sub, etc
#   - to add later if necessary

class Word:

    def __init__(self, text, tag, i, lemmatizer):
        self.POStag = tag
        self.index = i
        self.text = text

        # get roots
        if "'" in text:
            self.rebuild(text)
        elif text.lower() == 'wo':  # should the word be won't -> leads to wo / n't
            self.root = 'will'
        else:
            wn_tag = penn_to_wn(tag)
            self.root = lemmatizer.lemmatize(text, pos=wn_tag)

        # do dependencies


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
            self.root = text
        # we ignore 's and 'd since we don't gain anything from rebuilding them, the important part is the POS tag

    def toString(self):
        print self.text.encode('ascii'), self.POStag.encode('ascii'), self.index, self.root.encode('ascii')

def penn_to_wn(tag):
    if tag in ['JJ', 'JJR', 'JJS']:
        return 'a'
    elif tag in ['NN', 'NNS', 'NNP', 'NNPS']:
        return 'n'
    elif tag in ['RB', 'RBR', 'RBS']:
        return 'r'
    elif tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
        return 'v'
    return 'n'