import nltk
import time
import os
from nltk.parse import stanford
from nltk.internals import find_jars_within_path
import requests
from bs4 import BeautifulSoup
from itertools import chain
from parser import Parser


def tag():
    sentence = "I'll see you at 11.30, let me know if you can't come"

    sentence = "When cooking I listen to music"
    # tokenizer = nltk.tokenize.TreebankWordTokenizer()

    tokens = nltk.word_tokenize(sentence)

    tagged = nltk.pos_tag(tokens)

    print(tagged)


def CST():  # constituent structure tree
    # first we get the grammar
    sentence = "The little yellow dow barked at the cat"
    tokens = nltk.pos_tag(nltk.word_tokenize(sentence))

    grammar = "NP: {<DT>?<JJ>*<NN>}"  # an optional determiner (DT) followed by any number of adjectives (JJ) and then a noun (NN)

    chunkParser = nltk.RegexpParser(nltk.grammar)
    result = chunkParser.parse(tokens)
    print(result)
    result.draw()


def chartParsing():
    sent = "Mary saw a dog".split()


# not necessary anymore but we can keep it
def stanfordParsing():
    # os.environ['STANFORD_PARSER'] = '../res/stanford-parser-files'
    # os.environ['STANFORD_MODELS'] = '../res/stanford-parser-files'

    stanford_parser_jar = '../lib/stanford-parser-files/stanford-parser.jar'
    stanford_model_jar = '../lib/stanford-parser-files/stanford-parser-3.6.0-models.jar'
    english_model = '../lib/stanford-parser-files/englishPCFG.ser.gz'

    print(stanford_model_jar)

    parser = stanford.StanfordParser(path_to_jar=stanford_parser_jar, path_to_models_jar=stanford_model_jar)

    # parser = stanford.StanfordParser(model_path="../res/stanford-parser-files/englishPCFG.ser.gz")
    sentences = parser.raw_parse_sents(("Hello, My name is Melroy.", "What is your name?"))
    print sentences

    # GUI
    for line in sentences:
        for sentence in line:
            sentence.draw()


def stanfordParsing2():
    os.environ['STANFORD_PARSER'] = '../lib/stanford-parser-full'
    os.environ['STANFORD_MODELS'] = '../lib/stanford-parser-full'

    parser = stanford.StanfordParser()
    stanford_dir = parser._classpath[0].rpartition('/')[0]
    parser._classpath = tuple(find_jars_within_path(stanford_dir))

    sentence = raw_input('Type sentence: ')

    result = list(parser.raw_parse(sentence))

    print(result)

    for tree in result:
        print(tree)

    #result[0].draw()

    dependency_parser = stanford.StanfordDependencyParser()
    stanford_dir = dependency_parser._classpath[0].rpartition('/')[0]
    dependency_parser._classpath = tuple(find_jars_within_path(stanford_dir))

    dep = dependency_parser.raw_parse(sentence)

    dep = dep.next()

    # testing
    # print(dep.root['word'], dep.root['tag'])
    # for i in chain.from_iterable(dep.root['deps'].values()):
    #     obj = dep.get_by_address(i)
    #     print(obj['word'], obj['tag'], obj['rel'])

    # figure out how to represent this properly
    #print(dep.next())
    for item in list(triples_alt(dep)):
        print(item)

def triples_alt(dependency, node=None):
    """
    Extract dependency triples of the form:
    ((head word, head tag), rel, (dep word, dep tag))
    """
    if not node:
        node = dependency.root
        yield 'root' + '('+'ROOT-0, ' + node['word'].encode('ascii', 'ignore') + '-' + str(node['address']) + ')'

    head = node['word'].encode('ascii', 'ignore') +  '-' + str(node['address'])
    for i in sorted(chain.from_iterable(node['deps'].values())):
        dep = dependency.get_by_address(i)
        yield dep['rel'].encode('ascii', 'ignore') + '(' + head + ',' + dep['word'].encode('ascii', 'ignore') + '-' + str(dep['address'])+ ')'
        for triple in triples_alt(dependency, node=dep):
            yield triple


def requestFromStanford():
    sentence = raw_input('Type sentence: ')

    r = requests.post("http://nlp.stanford.edu:8080/parser/index.jsp",
                      data={'parse': 'Parse', 'parserSelect': 'English', 'query': sentence})

    soup = BeautifulSoup(r.text, "html.parser")

    tagging = ' '.join(soup.find("div", {"class": "parserOutputMonospace"}).text.split())

    print(tagging)

    # parseTree = ' '.join(soup.find("pre", {"id": "parse"}).text.split())

    parseTree = ' '.join(soup.find_all("pre", {"class": "spacingFree"})[0].text.split())

    print(parseTree)

    ptree = nltk.ParentedTree.fromstring(parseTree)

    dependencies = ' '.join(soup.find_all("pre", {"class": "spacingFree"})[1].text.split())

    print(dependencies)

def parserObjectTest():

    parser = Parser()
    while(True):
        sentence = raw_input('Type sentence: ')
        if sentence == '0':
            break

        start = time.time()
        result = parser.parse(sentence)
        end = time.time()
        print(end - start)
        # we can also print the tree with pformat_latex_qtree --> for latex!!
        print(result)
        result[1].pretty_print()

# ptree.draw()

def stemming():  # i.e. removing suffixes from words (to extract the "root" stem)
    stemmer = nltk.stem.PorterStemmer()
    print(stemmer.stem('driving'))  # outputs drive


def lemmatization():  # i.e. finding the root word -> this will be very useful to find files for words
    lemmatizer = nltk.stem.WordNetLemmatizer()
    root = lemmatizer.lemmatize('gave',
                                pos='v')  # the pos tags dont work directly i.e. VB, VBG VBP dont work (only works with n and v)
    # if we dont specify the pos it defaults to noun
    print(root)


#start = time.time()

parserObjectTest()
#lemmatization()


