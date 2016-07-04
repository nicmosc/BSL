from parser import Parser
from rules import Rules
from sentence import IntermediateSentence
from nltk import Tree
from utils import toUpper
from itertools import takewhile
class Analyser:

    ignore = ['#', '"', '(', ')', ',', '.', ':', '``', ';', '!', "''", "'"]  # these are possible tags we want to ignore

    def __init__(self):
        self.parser = Parser()
        self.rules = Rules()    # a rules object to apply the transfer and direct translation

    def buildSent(self, sentence):

        #no_punctuation = re.sub(r'[%s]' % ''.join(sentence.ignore), '', sentence.stringRep)     # remove punctuation to ease parse trees

        result = self.parser.parse(sentence.stringRep)  # send the text to stanford parser

        print result[2]

        no_punctuation_tree = self.removePunctuation(result[1])     # remove all punctuation from the parse tree

        sentence.updateWords(result[0], no_punctuation_tree, result[2], Analyser.ignore)

        sentence.traverseReplaceWords(sentence.augTree, [])  # replace words with word objects for modification and make tags unique

        sentence.setSentenceGroups(sentence.augTree) # set the sentence groups to each word

        # find tenses for the sentences in order to establish temporal topic
        # this is done before moving the time related words as we nned all the words for this
        sentence.setTenses()

    def applyRules(self, sentence):

        mod_sentence = self.rules.applyTreeTranforms(sentence)   # return modified original

        i_sentence = IntermediateSentence(mod_sentence, sentence)  # create intermediate sentence representation from result

        # before applying direct translation we may want to find multiple words that make up 1 sign e.g. now and then = NOW-AND-THEN
        self.rules.applyCombinedWords(i_sentence.words)

        # direct translation
        self.rules.applyDirectTranslation(i_sentence)

        # special cases are handled separately e.g. in + location = WHERE? LOCATION
        i_sentence.specialCases()

        i_sentence.countIndexes()

        i_sentence.toString()       # print once to see results

        #i_sentence.toUpper()        # set everything to upper as required
        #i_sentence.toString()

        return i_sentence

    def removePunctuation(self, tree):
        for subtree in tree[:]:
            #print subtree
            if type(subtree) == Tree:
                if subtree.label() in Analyser.ignore:
                    #print 'found', subtree.label()
                    tree.remove(subtree)
                else:
                    self.removePunctuation(subtree)

        return tree

    # this method will take the skeleton of the BSL output, that is something like MY -M-F- LIVE WHERE -E-S-S-E-X-
    # and add necessary info, as well as
    def setFacialExpressions(self, sentence):     # will generate both the text gloss and the JS object

        js_output = ''
        gloss = sentence.getGloss()

        # necessary steps:

        container_list = []

        # insert facial expressions e.g. hn, q, pause between groups, questions, tenses etc, negations
        # should also separate between facial expressions that affect a sentence group, and those which affect individual words

        # reminder: tenses and nsubj are not shown in the gloss


        temp_list = []
        i = 0
        while i < len(sentence.words):
            if sentence.words[i].is_negated:    # if the word begins a negation sequence
                temp_list = list(takewhile(lambda x: x.is_negated, sentence.words[i:]))   # get all words in that sequence
                container_list.append(Container(temp_list, 'neg'))
                i+=len(temp_list)-1

            elif sentence.words[i].is_questioned:     # if the word begins a question sequence
                temp_list = list(takewhile(lambda x: x.is_questioned, sentence.words[i:]))  # get all words in that sequence
                container_list.append(Container(temp_list, 'q'))
                i += len(temp_list) - 1

            elif sentence.words[i].sent_group in ['SQ']:       # maybe add SINV?
                temp_list = list(takewhile(lambda x: x.sent_group in ['SQ', 'SBARQ'], sentence.words[i:]))  # get all words in that sequence
                container_list.append(Container(temp_list, 'q'))
                i += len(temp_list) - 1

            elif sentence.words[i].root in ['who','where','why', 'when','how']:
                container_list.append(Container([sentence.words[i]], 'q'))

            elif sentence.words[i].dependency == 'nsubj':
                container_list.append(Container([sentence.words[i]], 'hn'))

            else:
                print sentence.words[i]
                container_list.append(sentence.words[i])
            i+=1

        # testing container
        # container_list = []
        # container_list.append(sentence.words[0])
        # container = Container(sentence.words, 'hn')
        # container.setSubContainer(2,2,Container([sentence.words[2]], 'neg'))
        # container_list.append(container)

        print container_list
        #print map(lambda x: str(x), container_list)

        # if w.POStag in ['NNS', 'NNPS']:
        #     if w.text != w.root and w.num_modified == False and w.direct_translation == False:
        #         gloss[i] += ' them'


        #return (' '.join(toUpper(gloss)), js_output)



    def updateRules(self):      # for testing, we may re-read the file to make it quicker
        self.rules = Rules()

# this object will contain a word / list of words (in order) together with a 'tag' that goes with them e.g.
# (YOU) [hn] -> object has [YOU] and tag hn, also (NOT GO) [neg] as well etc.
# if we have multiple containers e.g.
class Container:

    def __init__(self, words, tag):     # takes a list of words (can also include containers and the tag for those words
        self.words = words
        self.tag = tag

    def setSubContainer(self, start, end, container):       # replace the words at start to end with container containing those words
        self.words[end] = container
        self.words = self.words[:start]+self.words[end:]

    def __str__(self):
        return 'Container([' + ' '.join(map(lambda x: str(x), self.words)) + '], ' + self.tag + ')'

    def __repr__(self):
        return '(' + ' '.join(map(lambda x: repr(x), self.words)) + ')' + '[' + self.tag + ']'