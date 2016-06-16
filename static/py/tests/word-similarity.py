from nltk.corpus import wordnet as wn

def animals():

    dog = wn.synsets('dog')[0]

    wolf = wn.synsets('wolf')[0]

    sim1 = dog.path_similarity(wolf)

    house = wn.synsets('house')[0]

    sim2 = dog.path_similarity(house)

    print(sim1, sim2)

def adjectives():   # this kind of works
    time = wn.synsets('time')
    space = wn.synsets('space')
    size = wn.synsets('size')
    speed = wn.synsets('speed')


    word1 = 'before'
    word2 = 'was'

    set1 = wn.synsets(word1)[0]

    set2 = wn.synsets(word2)[0]

    maxSim1 = 0
    maxSim2 = 0

    for meaning in time:
        sim = set1.path_similarity(meaning)
        if sim > maxSim1:
            maxSim1 = sim

    for meaning in space:
        sim = set1.path_similarity(meaning)
        if sim > maxSim2:
            maxSim2 = sim

    print(word1 + " ? " + 'time' + " = " + str(maxSim1) + " | "+ word1 + " ? " + 'place' + " = " + str(maxSim2))

    maxSim1 = 0
    maxSim2 = 0

    for meaning in time:
        sim = set2.path_similarity(meaning)
        if sim > maxSim1:
            maxSim1 = sim

    for meaning in space:
        sim = set2.path_similarity(meaning)
        if sim > maxSim2:
            maxSim2 = sim

    print(word2 + " ? " + 'time' + " = " + str(maxSim1) + " | "+ word2 + " ? " + 'place' + " = " + str(maxSim2))

def times():

    while(True):
        sentence = raw_input('Type sentence: ')
        sent = sentence.split(' ')

        for s in sent:
            syn = wn.synsets(s, pos='v')
            if len(syn) > 0:
                print s, syn[0].lexname()

times()
