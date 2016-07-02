from parser import Parser
from rules import Rules
from sentence import IntermediateSentence
from nltk import Tree
from utils import toUpper

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
    def generateOutput(self, sentence):     # will generate both the text gloss and the JS object

        js_output = ''
        gloss = sentence.getGloss()

        # necessary steps:

        # insert facial expressions e.g. hn, q, pause between groups, questions, tenses etc


        # modify individual words e.g. -er, -est, plurals
        for i,w in enumerate(sentence.words):
            if w.POStag in ['NNS', 'NNPS']:
                if w.text != w.root and w.num_modified == False and w.direct_translation == False:
                    gloss[i]+= ' them'
            elif w.POStag == 'JJR':     # if it's a comparative adjective
                gloss[i] = w.text
            elif w.POStag == 'JJS':     # if it's a superlative adjective
                gloss[i] = w.text
            elif w.dependency[0] == 'nsubj':      # if the noun is the subject, we insert a head nod
                gloss[i] = '('+gloss[i]+')[hn]'
            elif w.root in ['why', 'who','where','when']:
                gloss[i] = '(' + gloss[i] + ')[q]'

        return (' '.join(toUpper(gloss)), js_output)

    def updateRules(self):      # for testing, we may re-read the file to make it quicker
        self.rules = Rules()