from parser import Parser
from rules import Rules
from sentence import EnglishSentence
from nltk import CFG, Tree, Nonterminal, Production
from nltk.parse.generate import generate

class Analyser:

    def __init__(self):
        self.parser = Parser()
        self.rules = Rules()    # a rules object to apply the transfer and direct translation

    def buildSent(self, sentence):
        result = self.parser.parse(sentence.stringRep)  # send the text to stanford parser

        sentence.updateWords(result[0], result[1], result[2])

        sentence.traverseReplaceWords(sentence.augTree, [])  # replace words with word objects for modification and make tags unique

def main():     # this method is used for testing, normally the sentence is sent directly to the analyser from the frontend

    analyser = Analyser()

    while (True):
        sent = raw_input('Type sentence: ')
        if sent == '0':
            break

        e_sentence = EnglishSentence(sent)
        analyser.buildSent(e_sentence)  # build sentence object with all relationships etc

        e_sentence.toString()

        analyser.rules.applyRules(e_sentence)

        e_sentence.clear()

main()