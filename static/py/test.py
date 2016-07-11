from termcolor import colored
from terminaltables import AsciiTable

from analyser import Analyser
from sentence import EnglishSentence, BSLSentence

from bleu import sentence_bleu, corpus_bleu
from re import sub

import sys
from os import devnull

analyser = Analyser()

def main():

    while (True):
        sent = raw_input('Type sentence: ')
        if sent == '0':
            break

        elif sent == 'update':
            analyser.updateRules()

        elif sent.split(' ')[0] == 'view_unit':  # if we want to do a unit test and display results in a table,
            # bleu score is shown at sentence level
            tableResults(sent)
        elif sent.split(' ')[0] == 'system_accuracy':
            systemAccuracy(sent)
        else:   # if we want to just test a sentence
            print process(sent)

def tableResults(sent):
    f_name = sent.split(' ')[1]
    try:
        file = open('unit-test/' + f_name + '.txt', 'r')
        table_data = [['Input', 'Expected', 'BLEU Accuracy', 'Output']]
        for line in file:
            if line.rstrip():
                input = line.split(' | ')[0]
                output = sub('\t|//.*', '', line).split(' | ')[1].strip()  # remove possible comments and tabs

                # suppress printing from the result method
                sys.stdout = open(devnull, 'w')
                result = process(input)
                sys.stdout = sys.__stdout__

                # do the test evaluation here...
                color = 'green'
                if result.strip() != output:
                    color = 'red'

                accuracy = sentence_bleu([output], result)

                accuracy_plain = sentence_bleu([sub('[\(\)]|\[.*\]','',output)], sub('[\(\)]|\[.*\]','',result))

                print input,'|',output,'|',colored(result,color),'|',accuracy,'|',accuracy_plain

                table_data.append([input, output, accuracy, colored(result, color)])
        table = AsciiTable(table_data)
        print table.table
        file.close()

    except IOError:
        print 'File ' + f_name + ' not found'

# calculate bleu score only over the whole test set (only returns a number at the end: 0.610444977652 now 0.632765476997 (184)
# only classifiers 0.391927292578 (49 sent)
# combined: 0.563023520503
# re.sub('[\(\)]|\[.*\]','',sent) to remove non manual features
def systemAccuracy(sent):
    f_name = sent.split(' ')[1]
    try:
        reference = []
        hypothesis = []

        file = open('unit-test/' + f_name + '.txt', 'r')

        file_lines = file.readlines()

        num_lines = sum(1 for i in list(file_lines) if i.rstrip())

        print num_lines

        current_line = 1
        for line in list(file_lines):
            if line.rstrip():   # avoid empty lines
                #print line
                input = line.split(' | ')[0]
                output = sub('\t|//.*', '', line).split(' | ')[1]   # remove possible comments and tabs

                # suppress printing from the result method
                sys.stdout = open(devnull, 'w')

                reference.append([output])
                result = process(input)
                hypothesis.append(result)   # for each english sentence we have the expected translation (reference) and result
                # from our system (hypothesis

                sys.stdout = sys.__stdout__

                #print reference, result

                #sys.stdout.write(str(int(float(current_line)/num_lines)*100.0)+'%'+'    \r')
                sys.stdout.write('\r'+str(int((float(current_line) / num_lines) * 100.0)) + '% '+ input)
                sys.stdout.flush()

                current_line += 1

        print '\r'

        # we then calculate the system score and print it
        accuracy = corpus_bleu(reference, hypothesis)

        print accuracy
        file.close()

    except IOError:
        print 'File ' + f_name + ' not found'

def process(sent):
    e_sentence = EnglishSentence(sent)

    analyser.buildSent(e_sentence)  # build sentence object with all relationships etc

    e_sentence.toString()  # print to see result

    bsl_data = analyser.applyRules(e_sentence)  # apply rules to modify the sentence and return result

    bsl_sentence = BSLSentence(bsl_data)

    outputs = analyser.generateOutputs(bsl_sentence)

    #accuracy_plain = sentence_bleu(['ME NOT LOVE IX_1'], sub('[\(\)]|\[.*\]', '', outputs[0]))
    #accuracy_plain = sentence_bleu(['ME NOT LOVE IX_1'], outputs[0])
    #print accuracy_plain

    #fe_bsl_sentence = analyser.setFacialExpressions(bsl_skeleton)

    # dont forget to clear once we're done
    e_sentence.clear()

    return outputs[0]

if __name__ == '__main__':
    main()