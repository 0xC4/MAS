from delown.ks import KnowledgeStructure, Announcements
import itertools
import random

P_AMOUNT_AGENTS = 3
P_AMOUNT_CARDS  = P_AMOUNT_AGENTS * 2

def print_world(world, vocab):
    true_idxs = [idx for idx, truth_value in enumerate(world) if truth_value == True] 
    
    facts = [vocab[i] for i in true_idxs]
    for i in range (int(len(facts) / 2)):
        print (str(facts[i*2:i*2+2]))


knowledgestructure = KnowledgeStructure(amount_agents=P_AMOUNT_AGENTS, amount_cards=P_AMOUNT_CARDS)

print (knowledgestructure)

print_world(knowledgestructure.initial_world, knowledgestructure.vocab)

remainingworlds = []

turn_agent = -1

while remainingworlds != 1:
    turn_agent = (turn_agent + 1) % 3

    for agent in range(P_AMOUNT_AGENTS):
        print ("[P{}->0] ".format(agent) + str(knowledgestructure.allowed_announcements(agent, 0)))
        print ("[P{}->1] ".format(agent) + str(knowledgestructure.allowed_announcements(agent, 1)))
        print ("[P{}->2] ".format(agent) + str(knowledgestructure.allowed_announcements(agent, 2)))

    knowledgestructure.announce(turn_agent, random.sample(knowledgestructure.allowed_announcements(turn_agent, turn_agent), 1)[0])

    remainingworlds = len(knowledgestructure.get_agent_valid_worlds(turn_agent))

print ("Winner: Player {}".format("abcdefg"[turn_agent]))