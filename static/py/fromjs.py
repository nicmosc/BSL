from parser import Parser
from rules import Rules
from sentence import EnglishSentence, IntermediateSentence
from nltk import Tree

class Analyser:

    ignore = ['#', '"', '(', ')', ',', '.', ':', '``', ';', '!']  # these are possible tags we want to ignore

    def __init__(self):
        self.parser = Parser()
        self.rules = Rules()    # a rules object to apply the transfer and direct translation

    def buildSent(self, sentence):

        #no_punctuation = re.sub(r'[%s]' % ''.join(sentence.ignore), '', sentence.stringRep)     # remove punctuation to ease parse trees

        result = self.parser.parse(sentence.stringRep)  # send the text to stanford parser

        no_punctuation_tree = self.removePunctuation(result[1])     # remove all punctuation from the parse tree

        sentence.updateWords(result[0], no_punctuation_tree, result[2], Analyser.ignore)

        sentence.toString()

        sentence.traverseReplaceWords(sentence.augTree, [])  # replace words with word objects for modification and make tags unique

    def applyRules(self, sentence):
        mod_sentence = self.rules.applyTreeTranforms(sentence)   # return modified original

        i_sentence = IntermediateSentence(mod_sentence)  # create intermediate sentence representation from result

        self.rules.applyDirectTranslation(i_sentence)

        i_sentence.toUpper()
        i_sentence.toString()

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

    def updateRules(self):      # for testing, we may re-read the file to make it quicker
        self.rules = Rules()

def main():     # this method is used for testing, normally the sentence is sent directly to the analyser from the frontend

    analyser = Analyser()

    while (True):
        sent = raw_input('Type sentence: ')
        if sent == '0':
            break

        if sent == 'update':
            analyser.updateRules()
        else:
            e_sentence = EnglishSentence(sent)
            analyser.buildSent(e_sentence)  # build sentence object with all relationships etc
            e_sentence.toString()           # print to see result

            analyser.applyRules(e_sentence)   # apply rules to modify the sentence and return result

            # dont forget to clear once we're done
            e_sentence.clear()

main()