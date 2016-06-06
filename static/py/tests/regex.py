import re

line = "ROOT -> S"

rule = "NP -> DT <> NN"

rule = re.sub(' <> ', '(.*)', rule)

print rule

matchObj = re.match( r'%s' % rule, line)

if matchObj:
    match = matchObj.group(1).strip()

    mapping = "NP -> DT NN <>"

    res = re.sub(r'<>', match, mapping)

    print res

else:
   print "No match!!"