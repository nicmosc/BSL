from parser import Parser
from sentence import EnglishSentence
from nltk import Tree

class Analyser:

    def __init__(self):
        self.parser = Parser()


    def buildSent(self, sentence):
        result = self.parser.parse(sentence.stringRep)  # send the text to stanford parser

        sentence.syntaxTree = result[1]     # assign the syntax tree from the analysis
        sentence.updateWords(result[0], result[2])

def main():     # this method is used for testing, normally the sentence is sent directly to the analyser from the frontend

    analyser = Analyser()

    while (True):
        sent = raw_input('Type sentence: ')
        if sent == '0':
            break

        e_sentence = EnglishSentence(sent)
        analyser.buildSent(e_sentence)  # build sentence object with all relationships etc

        e_sentence.toString()

        e_sentence.clear()

main()