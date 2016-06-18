import requests
from bs4 import BeautifulSoup
from string import ascii_uppercase

url = 'http://bslsignbank.ucl.ac.uk/dictionary/search/?'
query = 'query='
page = '&page='

file = open('signbank.txt', 'w')

for letter in ascii_uppercase:

    index = 1

    prevWords = ''

    while(True): # until we havent found all the words for this letter

        html = requests.get(url+query+letter+page+str(index))

        soup = BeautifulSoup(html.text, "html.parser")

        table = soup.find('div', {'id':'searchresults'})

        soup = BeautifulSoup(table.text, 'html.parser')

        words = filter(lambda x: len(x) > 0, soup.get_text().split('\n'))

        if words == prevWords:
            break

        print words

        prevWords = words

        for w in words:
            if len(w.split(' ')) > 1:   # we only save those words that make up 1 sign
                file.write(w+'\n')

        index += 1

    # gloss = soup.find("span", {"class": "asl"}).text.encode('ascii', 'ignore')  # convert unicode to string
    # english = soup.find("span", {"class": "eng"}).text.encode('ascii', 'ignore')

    # if(len(gloss) > 2 and len(english) > 0):    # discard erroneous/missing sentences
    #
    #     file.write(english + " //// " + gloss + "\n")
    #     print(index, gloss, english)
    #
    # index += 1

print("DONE")
file.close()