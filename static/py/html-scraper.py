import requests
from bs4 import BeautifulSoup


url = 'http://www.handspeak.com/translate/index.php?id='

index = 1

file = open('translations.txt', 'w')

while(index < 350):
    try:

        page = requests.get(url+str(index))

        soup = BeautifulSoup(page.text, "html.parser")

        gloss = soup.find("span", {"class": "asl"}).text.encode('ascii', 'ignore')  # convert unicode to string
        english = soup.find("span", {"class": "eng"}).text.encode('ascii', 'ignore')

        if(len(gloss) > 2 and len(english) > 0):    # discard erroneous/missing sentences

            file.write(english + " //// " + gloss + "\n")
            print(index, gloss, english)

        index += 1

    except AttributeError:
        print("Skipping")
        index += 1

print("DONE")
file.close()