import re

line = "NP -> DT JJ NNP"

source = "NP -> DT <> NN*"

target = "NP -> DT NN* <>"

# we want to see NP -> NP_1 NN_1 JJ

# modify the mapping before applying it (for unique tags

ln = line.split(' ')
targ = target.split(' ')

for i,map in enumerate(targ):
    for l in ln[:]:  # for each section in the line
        spl = l.split('_')      # len is 2 if the tag is unique
        any = map[:-1] == '*'   # if asterisc is found at the end of the tag, it means any tag with extra at the end will match
        print map,l
        if spl[0] == map or map == '_':       # if the two are identical or if the map is _ i.e. nothing
            if len(spl) > 1:    # if the tag is unique modify the other end
                targ[i] += '_' + str(spl[1])
            ln.remove(l)
            print '\t\t\t', ln
            break
    if map == '<>':     # if we find this symbol, change direction
        ln = list(reversed(ln))

target = ' '.join(targ)

source = re.sub('\s?<>\s?', '(.*)', source)

print "\nRESULTS BELOW"

print "source: ",source
print "target: ",target

new_line = re.sub('_\d\s?',' ',line)

print 'new line: ',new_line

matchObj = re.match( r'%s' % source, new_line)

print ln

if matchObj:

    if len(matchObj.groups()) == 0:
        match = matchObj.group()

    else:
        #match = matchObj.group(1).strip()    # will have to fix it to work with multiple <> <>
        match = ' '.join(list(reversed(ln)))


    print 'match: ', match

    res = re.sub(r'<>', match, target)

    print res

else:
   print "No match!!"