import re

line = "NP_2 -> DT ADJ NN_1"

rule = "NP -> DT <> NN"

mapping = "NP -> DT NN <>"

# modify the mapping before applying it (for unique tags

ln = line.split(' ')
maps = mapping.split(' ')

for i,map in enumerate(maps):
    for l in ln[:]:  # for each section in the line
        spl = l.split('_')      # len is 2 if the tag is unique
        if spl[0] == map:       # if the two are identical
            if len(spl) > 1:    # if the tag is unique modify the other end
                maps[i] += '_' + str(spl[1])
            ln.remove(l)
            break

mapping = ' '.join(maps)

rule = re.sub(' <> ', '(.*)', rule)

print rule
print mapping

new_line = re.sub('_\d\s?',' ',line)

print 'new line',new_line

matchObj = re.match( r'%s' % rule, new_line)

#print matchObj.group()

if matchObj:

    if len(matchObj.groups()) == 0:
        match = matchObj.group()

    else:
        match = matchObj.group(1).strip()    # will have to fix it to work with multiple <> <>

    res = re.sub(r'<>', match, mapping)

    print res

else:
   print "No match!!"