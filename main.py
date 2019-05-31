from delown.ks import KnowledgeStructure, Announcements
import itertools
import random

P_AMOUNT_AGENTS = 3
P_AMOUNT_CARDS  = P_AMOUNT_AGENTS * 2


knowledgestructure = KnowledgeStructure(amount_agents=P_AMOUNT_AGENTS, amount_cards=P_AMOUNT_CARDS)

print (knowledgestructure.observables[1])

print (knowledgestructure)

knowledgestructure.announce(0, Announcements.ONE_EVEN)
knowledgestructure.announce(0, Announcements.ONE_ODD)
knowledgestructure.announce(1, Announcements.ONE_ODD)
knowledgestructure.announce(2, Announcements.ONE_ODD)

# for w in knowledgestructure.valid_worlds:
    # print (w)
    