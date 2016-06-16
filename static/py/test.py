from fromjs import Analyser
from sentence import EnglishSentence
from terminaltables import AsciiTable
from termcolor import colored

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

                table_data = [['Input', 'Expected', 'Output']]


                for line in file:

                    input = line.split(' | ')[0]

                    output = line.split(' | ')[1]

                    result = process(input)

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

    result = analyser.applyRules(e_sentence)  # apply rules to modify the sentence and return result

    # dont forget to clear once we're done
    e_sentence.clear()

    return result

if __name__ == '__main__':
    main()