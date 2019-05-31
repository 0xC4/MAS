from delown.ks import KnowledgeStructure, Announcements
import itertools
import random

P_AMOUNT_AGENTS = 3
P_AMOUNT_CARDS  = P_AMOUNT_AGENTS * 2


knowledgestructure = KnowledgeStructure(amount_agents=P_AMOUNT_AGENTS, amount_cards=P_AMOUNT_CARDS)

print (knowledgestructure.observables[1])

print (knowledgestructure)

knowledgestructure.announce(0, Announcements.BOTH_EVEN)
knowledgestructure.announce(1, Announcements.ONE_ODD)
knowledgestructure.announce(2, Announcements.ONE_EVEN)

for idx, world in enumerate(knowledgestructure.valid_worlds):
    print()
    print("Possible world {}/{}".format(idx + 1, len(knowledgestructure.valid_worlds)))
    true_idxs = [idx for idx, truth_value in enumerate(world) if truth_value == True] 
    
    facts = [knowledgestructure.vocab[i] for i in true_idxs]
    for i in range (int(len(facts) / 2)):
        print (str(facts[i*2:i*2+2]))
    input()