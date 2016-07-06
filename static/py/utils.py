# some useful method I did not know where else to put

from datetime import date
from nltk.corpus import names

# formats numbers in the way we want them
def formatNumber(textnum):

    ########## FLOAT CASE ##########
    float = textnum.split(',')
    if len(float) > 1:
        return  '-'+'-'.join(float[0]) + '-point-'+ '-'.join(float[1])+'-'

    ########## DATE CASE ##########
    dby = textnum.split('/')
    if len(dby) == 3:
        # get the date in text format
        date_text = date(day = int(dby[0]), month=int(dby[1]),year=int(dby[2])).strftime('%d %B %Y').split(' ')
        month = abbreviateMonth(date_text[1])

        return '-'+'-'.join(date_text[0]+month+date_text[2]) + '-'

    if len(dby) == 2:
        if int(dby[1]) > 12: # if the second argument is the year (and not the month)
            date_text = date(day = 1, month=int(dby[0]),year=int(dby[1])).strftime('%B %Y').split(' ')
            month = abbreviateMonth(date_text[1])
            return '-' + '-'.join(month + date_text[1]) + '-'
        else:
            date_text = date(day=int(dby[0]), month=int(dby[1]), year = 1990).strftime('%d %B').split(' ')
            month = abbreviateMonth(date_text[1])
            return '-' + '-'.join(date_text[0]+month) + '-'

    ########## DIGIT CASE ##########
    if textnum.isdigit():     # if the string is already in integer form
        number = int(textnum)
        if number < 20:         # if the number is below 19, we use the corresponding sign
            return textnum
        else:
            return '-'+'-'.join(textnum)+'-'

    ########## TEXT CASE ##########
    else:                       # otherwise we convert it to int, then do as above
        number = text2int(textnum)
        return '-'+'-'.join(str(number))+'-'

def abbreviateMonth(word):
    if word in ['May', 'June', 'July']:
        return word
    elif word == 'September':
        return 'Sept'
    else:
        return word[:3]

# converts numbers in text form to integer form
def text2int(textnum, numwords={}):
    if not numwords:
        units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):    numwords[word] = (1, idx)
        for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
            raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

def findGender(name):
    if name.title() in names.words('male.txt'):
        return 'male'
    elif name.title() in names.words('female.txt'):
        return 'female'
    else:
        return None

def toUpper(words):
    for i, word in enumerate(words):
        if 'index' not in word:  # do not uppercase Index
            words[i] = word.upper()
    return words
