# some useful method I did not know where else to put


def formatNumbers(textnum):

    # two cases: if the number is already in integer form, and if it is a float
    float = textnum.split(',')
    if len(float) > 1:
        return  '-'+'-'.join(float[0]) + '-point-'+ '-'.join(float[1])+'-'

    elif textnum.isdigit():     # if the string is already in integer form
        number = int(textnum)
        if number < 19:         # if the number is below 19, we use the corresponding sign
            return textnum
        else:


    #num = text2int(textnum)

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

#print text2int("seven billion one hundred million thirty one thousand three hundred thirty seven")
#print text2int("19")
formatNumbers('eighteen')