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

        sentence.traverseReplaceWords(sentence.augTree)  # replace words with word objects for modification

    # the following is kind of useless, may remove
    def traverse(self, tree, rule, mapping):
        for node in tree:
            if isinstance(node, Tree):      # if it's a node i.e. non terminal
                if node.label() == rule[0]:    #taken from rules lhs
                    if len(node) == len(rule)-1:    # if the rule matches the number of nodes
                        pos = 1                       # position of mappings
                        for child in node:
                            if child.label() == rule[pos]:
                                if mapping[pos] == '_':  # if we want to delete the node we do so
                                    node.remove(child)
                                pos+=1
                            else:               # if the rule does not match we stop
                                break
                self.traverse(node, rule, mapping)

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

def ruleTest1():
    string = '(ROOT (S (NP (PRP He)) (VP (VBD was) (VP (VBN gone)))))'
    tree = Tree.fromstring(string)

    rule = 'VP -> VBD VP'
    mapping = '_ -> _ VP'

    tree.pretty_print()

    production = tree.productions()       # get the context free grammar for this tree, which we then modify

    print production

    newProduction = []

    for r in production:
        if str(r) == rule:
            r = Production(Nonterminal('VP'), [Nonterminal('VP')])

        else:
            newProduction.append(r)

    print newProduction

    grammar = CFG(newProduction[0].lhs(), newProduction)

    for sentence in generate(grammar, n=10):
        print(' '.join(sentence))

def ruleTest3():
    string = '(ROOT (S (NP (PRP He)) (VP (VBD was) (VP (VBN gone)))))'
    tree = Tree.fromstring(string)

    rule = 'VP -> VBD VP'
    mapping = '_ -> _ VP'

    tree.pretty_print()

    production = tree.productions()  # get the context free grammar for this tree, which we then modify

    print production

    newProduction = []

    for r in production:
        if str(r) == rule:
            r = Production(Nonterminal('VP'), [Nonterminal('VP')])

        else:
            newProduction.append(r)

    print newProduction

    grammar = CFG(newProduction[0].lhs(), newProduction)

    for sentence in generate(grammar, n=10):
        print(' '.join(sentence))

def ruleTest2():

    analyser = Analyser()

    string = '(ROOT (S (NP (PRP He)) (VP (VBD was) (VP (VBN gone)))))'
    tree = Tree.fromstring(string)

    rule = ['VP', 'VBD', 'VP']
    mapping = ['_','_','VP']

    tree.pretty_print()

    analyser.traverse(tree, rule, mapping)

    tree.pretty_print()

main()