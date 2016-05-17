import nltk
import time

def tag():
	sentence = "I'll see you at 11.30, let me know if you can't come"

	sentence = "When cooking I listen to music"
	#tokenizer = nltk.tokenize.TreebankWordTokenizer()

	tokens = nltk.word_tokenize(sentence)

	tagged = nltk.pos_tag(tokens)

	print(tagged)

def CST():	# constituent structure tree
	# first we get the grammar
	sentence = "The little yellow dow barked at the cat"
	tokens = nltk.pos_tag(nltk.word_tokenize(sentence))

	grammar = "NP: {<DT>?<JJ>*<NN>}"	#an optional determiner (DT) followed by any number of adjectives (JJ) and then a noun (NN)

	chunkParser = nltk.RegexpParser(nltk.grammar)
	result = chunkParser.parse(tokens)
	print(result)
	result.draw()


def chartParsing():
	sent = "Mary saw a dog".split()

def stanfordParsing():
	sent =  "The little yellow dow barked at the cat"
	#tree = nltk.parse

def stemming():		#i.e. removing suffixes from words (to extract the "root" stem)
	stemmer = nltk.stem.PorterStemmer()
	print(stemmer.stem('driving')) # outputs drive

def lemmatization():	# i.e. finding the root word -> this will be very useful to find files for words
	lemmatizer = nltk.stem.WordNetLemmatizer()
	root = lemmatizer.lemmatize('cooking', pos = 'v')	# the pos tags dont work directly i.e. VB, VBG VBP dont work (only works with n and v)
	# if we dont specify the pos it defaults to noun
	print(root)


start = time.time()

#tag()
#lemmatization()
chartParsing()

end = time.time()
print(end-start)