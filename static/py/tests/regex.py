import re

line = "NP -> DT PP XP NN_1"

rule = "NP -> DT <> NN"

mapping = "NP -> <> NN DT"

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

print rule
print mapping

rule = re.sub(' <> ', '(.*)', rule)

matchObj = re.match( r'%s' % rule, line)

#print matchObj.group()

if matchObj:

    if len(matchObj.groups()) == 0:
        match = matchObj.group()

    else:
        match = matchObj.group(1).strip()    # will have to fix it to work with multiple <> <>

    # modify the mapping to match the unique tags e.g. the second VP becomes VP_1

    # maps = mapping.split(' ')
    # tags = line.split(' ')
    # print tags, maps
    # for i,tag in enumerate(tags):
    #     spl = tag.split('_')
    #     if len(spl) > 1 and spl[0] == maps[i]:     # if the tag has a unique ID
    #         maps[i]+='_'+ str(spl[1])
    #
    # mapping = ' '.join(maps)

    res = re.sub(r'<>', match, mapping)

    print res

else:
   print "No match!!"