import re

def regex():
    line = "NP -> DT JJ NN"

    source = "NP -> DT <> NN~"

    target = "NP -> DT NN~ <>"   # needs [1, (4,5), 2, 3]


    # modify the mapping before applying it (for unique tags


    src = source.split(' ')
    source_copy = src[:]

    for i, s in enumerate(source_copy):
        if s != '<>' and s != '->':
            source_copy[i] += '(_?\d?)'

    source = ' '.join(source_copy)

    source = re.sub('\s<>\s', '(.*\s)', source)
    source = re.sub('\s<>', '(\s?.*)', source)

    source = re.sub('~', '([A-Z]*)', source)

    source += '$'   # match end of string exactly

    # replace the * with   to specify letters
    #source = re.sub('~', '(\w*)', source)

    print "\nRESULTS BELOW"

    print "line: ",line
    print "source: ",source
    print "target: ",target

    # clean the production
    #new_line = re.sub('_\d\s?',' ',line)

    #print 'new line: ',new_line

    matchObj = re.match( r'%s' % source, line)

    #print ln

    if matchObj:

        print matchObj.groups()
        trg = target.split(' ')

        source_i = []  # index of each element in the source
        target_i = []  # mapping of the above e.g.

        #  1     2  3 (4,5)      1    2(4,5) 3
        # NP -> DT <> NN~   =  NP -> DT NN~ <>

        # if a match exists, create linkage between the source and target for the match groups
        # (so that correct tags ids and <> can be placed properly)
        i = 1
        for s in src:
            if s != '->':
                if s[-1] == '~':  # if tag can be matched to anything, make tuple for match groups
                    source_i.append((i, i + 1))
                    i += 1
                else:
                    source_i.append(i)
                i += 1

        print source_i

        temp_source = src[:]        # make a copy, we'll need src later

        i = -1
        backtrace = 0       # used if our match is further on in the rule
        last_point = 0
        skip = 0
        needs_backtrace = False
        seen_tags = []      # will store the tags seen (for backtracing)
        for t in trg:                   # iterate through all target tags
            for s in temp_source[:]:    # for each source tag
                if t == '->':  # ignore ->
                    continue
                if s != '->':  # if the source tag is not -> increase index by one (to obtain group index from source_i)
                    i += 1
                else:
                    temp_source.remove(s)   # otherwise remove it as it's not needed
                    continue                # skip the stuff below
                print t, s, i, backtrace, 'skip',skip, ' seen tags:', seen_tags
                if t == s or t == '_':                  # if the two tags match
                    print source_i, len(source_i), i
                    if s in seen_tags:
                        target_i.append(source_i[i])
                        seen_tags.remove(s)
                    else:
                        target_i.append(source_i[i+skip])    # add the corresponding group index to the target position
                        #if skip > 1: skip -=1
                    if i == last_point and skip > 0:
                        i += skip-1
                        skip = 0
                    if needs_backtrace:             # if the tag was found further in the list, reset the backtrace
                        i = i - backtrace - 1
                        skip = backtrace
                        backtrace = 0
                        print 'resetting index and backtrace', i, backtrace
                    temp_source.remove(s)           # remove the source tag found
                    needs_backtrace = False
                    print '\t\t\t',target_i, temp_source
                    break
                else:
                    if s != '->' and t != '->':     # if both source and target tags are not -> then it means the tag we're looking for is further awat
                        print 'setting backtrace'
                        seen_tags.append(s)
                        if not needs_backtrace:
                            needs_backtrace = True
                            last_point = i+1
                        backtrace += 1
                print '\t\t\t',target_i, temp_source

        # go through each group and assign it to the target as explained
        i = 0       # this index is used to get the index of the group
        new_target = []
        for j,t in enumerate(trg):  # for each target tag
            if t != '->':
                if t[-1] == '~':
                    new_target.append(t[:-1] + matchObj.group(target_i[i][0]) + matchObj.group(target_i[i][1]))   # set the tuple (tag + tuple)
                elif t == '<>':
                    #trg[j] = matchObj.group(target_i[i]).strip()        # replace all the tags in the group as it's a <>
                    tags = matchObj.group(target_i[i]).strip().split(' ')
                    new_target.extend(tags)
                else:
                    if t != '_':
                        new_target.append(t + matchObj.group(target_i[i]) )       # append the id to the tag
                print new_target, t, target_i[i]
                i+=1
            else:
                new_target.append(t)

        target = ' '.join(new_target)

        print 'final target: ', target

    else:
       print "No match!!"

regex()