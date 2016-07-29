from nltk import Tree
from parser import Parser
from rules import Rules
from sentence import EnglishSentence,IntermediateSentence,BSLSentence


class Analyser:

    ignore = ['#', '"', '(', ')', ',', '.', ':', '``', ';', '!', "''", "'"]  # these are possible tags we want to ignore

    def __init__(self, app = False):
        self.parser = Parser(app)
        self.APP = app
        self.rules = Rules(app)    # a rules object to apply the transfer and direct translation

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

    def removePunctuation(self, tree):
        for subtree in tree[:]:
            # print subtree
            if type(subtree) == Tree:
                if subtree.label() in Analyser.ignore:
                    # print 'found', subtree.label()
                    tree.remove(subtree)
                else:
                    self.removePunctuation(subtree)
        return tree

    def applyRules(self, sentence):

        mod_sentence = self.rules.applyTreeTranforms(sentence)   # return modified original

        i_sentence = IntermediateSentence(mod_sentence, sentence)  # create intermediate sentence representation from result

        # before applying direct translation we may want to find multiple words that make up 1 sign e.g. now and then = NOW-AND-THEN
        self.rules.applyCombinedWords(i_sentence.words)

        print i_sentence.words

        # direct translation
        self.rules.applyDirectTranslation(i_sentence)

        # special cases are handled separately e.g. in + location = WHERE? LOCATION
        i_sentence.specialCases()

        i_sentence.countIndexes()

        i_sentence.resetWordPositions()     # to make JS generation easier

        self.rules.checkForCompounds(i_sentence)

        i_sentence.toString()       # print once to see results

        bsl_data = i_sentence.setNonManualFeatures()

        print '\n========================== BSL DATA ==========================\n'

        print bsl_data

        return bsl_data

    def generateOutputs(self, bsl_sentence):
        print '\nGLOSS OUTPUT\n'
        gloss = bsl_sentence.toGlossText()

        html = bsl_sentence.toGlossHTML()

        print html

        jsobject = bsl_sentence.toJS()

        return (gloss, html, jsobject)

    def process(self,sent):
        e_sentence = EnglishSentence(sent)

        self.buildSent(e_sentence)  # build sentence object with all relationships etc

        e_sentence.toString()  # print to see result

        bsl_data = self.applyRules(e_sentence)  # apply rules to modify the sentence and return result

        bsl_sentence = BSLSentence(bsl_data)

        outputs = self.generateOutputs(bsl_sentence)

        # dont forget to clear once we're done
        e_sentence.clear()

        return outputs

    def updateRules(self):      # for testing, we may re-read the file to make it quicker
        self.rules = Rules(self.APP)