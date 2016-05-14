from nltk.corpus import wordnet as wn

dog = wn.synsets('dog')[0]

wolf = wn.synsets('wolf')[0]

sim1 = dog.path_similarity(wolf)

house = wn.synsets('house')[0]

sim2 = dog.path_similarity(house)

print(sim1, sim2)