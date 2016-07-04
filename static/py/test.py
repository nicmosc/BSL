from analyser import Analyser
from sentence import EnglishSentence
from terminaltables import AsciiTable
from termcolor import colored
import requests

analyser = Analyser()

def main():

    while (True):
        sent = raw_input('Type sentence: ')
        if sent == '0':
            break

        elif sent == 'update':
            analyser.updateRules()

        elif sent.split(' ')[0] == 'unit':  # if we want to do a unit test
            f_name = sent.split(' ')[1]
            try:

                file = open('unit-test/' + f_name+'.txt', 'r')

                table_data = [['Input', 'Expected', 'Accuracy','Output']]


                for line in file:

                    input = line.split(' | ')[0]

                    output = line.split(' | ')[1]

                    result = process(input)

                    # now get the similarity score from the website
                    #r = requests.post("https://www.tools4noobs.com",
                                      #data={'action': 'ajax_string_similarity', 'text': output.strip(), 'text2': result.strip(),
                                      #      'limit': 0.4})
                    #similarity = '.'.join(r.text.split()[-1].split('.')[:-1])

                    # do the test evaluation here...
                    color = 'green'
                    if result.strip() != output.strip():
                        color = 'red'
                    table_data.append([input, output, colored(result, color)])

                table = AsciiTable(table_data)
                print table.table

                file.close()

            except IOError:
                print 'File ' + f_name + ' not found'
        else:   # if we want to just test a sentence
            print process(sent)

def process(sent):
    e_sentence = EnglishSentence(sent)

    analyser.buildSent(e_sentence)  # build sentence object with all relationships etc

    e_sentence.toString()  # print to see result

    bsl_skeleton = analyser.applyRules(e_sentence)  # apply rules to modify the sentence and return result

    ''' AFTER THIS POINT WE WANT TO PROCESS FACIAL EXPRESSIONS ETC '''

    fe_bsl_sentence = analyser.setFacialExpressions(bsl_skeleton)

    # dont forget to clear once we're done
    e_sentence.clear()

    #return output[0]

if __name__ == '__main__':
    main()