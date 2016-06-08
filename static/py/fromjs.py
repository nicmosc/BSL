from parser import Parser
from rules import Rules
from sentence import EnglishSentence, IntermediateSentence
import re

class Analyser:

    def __init__(self):
        self.parser = Parser()
        self.rules = Rules()    # a rules object to apply the transfer and direct translation

    def buildSent(self, sentence):

        no_punctuation = re.sub(r'[%s]' % ''.join(sentence.ignore), '', sentence.stringRep)     # remove punctuation to ease parse trees

        result = self.parser.parse(no_punctuation)  # send the text to stanford parser

        sentence.updateWords(result[0], result[1], result[2])

        sentence.traverseReplaceWords(sentence.augTree, [])  # replace words with word objects for modification and make tags unique

    def applyRules(self, sentence):
        mod_sentence = self.rules.treeTranforms(sentence)   # return modified original

        i_sentence = IntermediateSentence(mod_sentence)  # create intermediate sentence representation from result



        # don't forget to clear once we're done
        i_sentence.clear()

def main():     # this method is used for testing, normally the sentence is sent directly to the analyser from the frontend

    analyser = Analyser()

    while (True):
        sent = raw_input('Type sentence: ')
        if sent == '0':
            break

        e_sentence = EnglishSentence(sent)
        analyser.buildSent(e_sentence)  # build sentence object with all relationships etc
        e_sentence.toString()           # print to see result

        analyser.applyRules(e_sentence)   # apply rules to modify the sentence and return result

        # dont forget to clear once we're done
        e_sentence.clear()

main()