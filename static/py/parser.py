from nltk.parse.stanford import StanfordParser, StanfordDependencyParser
from nltk.internals import find_jars_within_path
import nltk.tree
import requests
import os
from bs4 import BeautifulSoup
from itertools import chain
#nltk.internals.config_java(options='-xmx2G')

class Parser:

    def __init__(self):
        # first check if the stanford website is accessible
        status_code = 0
        try:
            initRequest = requests.post("http://nlp.stanford.edu:8080/parser/index.jsp", timeout=1) # test if the parser is still at this address
            status_code = initRequest.status_code

        except requests.ConnectionError:
            print "Not online"

        # for testing
        #status_code = 1

        if (status_code == 200): # if it's fine
            self.online = True
        else:
            self.online = False

            # set up necessary variables for local stanford parser
            os.environ['STANFORD_PARSER'] = '../lib/stanford-parser-full'
            os.environ['STANFORD_MODELS'] = '../lib/stanford-parser-full'

            # set up tree parser
            self.parser = StanfordParser()
            stanford_dir = self.parser._classpath[0].rpartition('/')[0]
            self.parser._classpath = tuple(find_jars_within_path(stanford_dir))

            # set up dependency parser
            self.dependency_parser = StanfordDependencyParser()
            stanford_dir = self.dependency_parser._classpath[0].rpartition('/')[0]
            self.dependency_parser._classpath = tuple(find_jars_within_path(stanford_dir))


    def parse(self, sentence):  # given a sentence the parser will perform the operation
        if(self.online):    # if we can operate online

            r = requests.post("http://nlp.stanford.edu:8080/parser/index.jsp",
                              data={'parse': 'Parse', 'parserSelect': 'English', 'query': sentence})

            soup = BeautifulSoup(r.text, "html.parser")

            tagging = ' '.join(soup.find("div", {"class": "parserOutputMonospace"}).text.split())#.encode('ascii', 'ignore')

            parseTree = ' '.join(soup.find_all("pre", {"class": "spacingFree"})[0].text.split())
            parseTree = nltk.Tree.fromstring(parseTree)

            #ptree = ParentedTree.fromstring(parseTree)

            dependencies = soup.find_all("pre", {"class": "spacingFree"})[1].text.split('\n')

            return [tagging, parseTree, dependencies]   # return complete analysis

        else:

            #tagging = self.tagger.tag(sentence.split())

            parseTree = list(self.parser.raw_parse(sentence))[0]

            dependencies_res = self.dependency_parser.raw_parse(sentence)
            dependencies_res = dependencies_res.next()

            dependencies = list(triples_alt(dependencies_res))

            # was not able to work out Stanford POSTagger locally, so we obtain tags from the parse tree
            # should return a string 'Could/MD you/PRP bring/VB soap/NN ,/, bread/NN and/CC water/NN ?/.'
            leaves = list(parseTree.subtrees(lambda t: t.height() == 2))
            tagging = ''
            for pair in leaves:
                txt = str(pair).strip("()").split() # remove brackets and split tag/word
                tagging += txt[1]+'/'+txt[0] + ' '

            tagging = tagging[:-1]

            return [tagging, parseTree, dependencies]

def triples_alt(dependency, node=None):
    """
    Extract dependency triples of the form:
    ((head word, head tag), rel, (dep word, dep tag))
    """
    if not node:
        node = dependency.root
        #yield 'root' + '(' + 'ROOT-0, ' + node['word'].encode('ascii', 'ignore') + '-' + str(node['address']) + ')'
        yield 'root' + '(' + 'ROOT-0, ' + node['word'] + '-' + str(node['address']) + ')'

    #head = node['word'].encode('ascii', 'ignore') + '-' + str(node['address'])
    head = node['word'] + '-' + str(node['address'])
    for i in sorted(chain.from_iterable(node['deps'].values())):
        dep = dependency.get_by_address(i)
        #yield dep['rel'].encode('ascii', 'ignore') + '(' + head + ', ' + dep['word'].encode('ascii', 'ignore') + '-' + str(dep['address']) + ')'
        yield dep['rel'] + '(' + head + ', ' + dep['word'] + '-' + str(dep['address']) + ')'
        for triple in triples_alt(dependency, node=dep):
            yield triple