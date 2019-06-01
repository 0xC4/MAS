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
pass_count = 0

while remainingworlds != 1: # As long as one player does not have all the knowledge

    # Keep moving to the next player
    turn_agent = (turn_agent + 1) % 3

    for agent in range(P_AMOUNT_AGENTS):
        print ("[P{}->0] ".format(agent) + str(knowledgestructure.allowed_announcements(agent, 0)))
        print ("[P{}->1] ".format(agent) + str(knowledgestructure.allowed_announcements(agent, 1)))
        print ("[P{}->2] ".format(agent) + str(knowledgestructure.allowed_announcements(agent, 2)))

    possible_announcements = knowledgestructure.allowed_announcements(turn_agent, turn_agent)

    # Agent passes round if he cannot make a valid announcement.
    if len(possible_announcements) < 1:
        print ("Agent {} cannot make any annoucements and passes.".format(turn_agent))
        pass_count += 1

        # If three players pass in a row, quit with no winner
        if pass_count == 3:
            turn_agent = -1
            break
        continue

    # Otherwise make a random announcement
    knowledgestructure.announce(turn_agent, random.sample(possible_announcements, 1)[0])

    # If the turn player has only one valid world remaining, he knows everyones cards and wins the game
    remainingworlds = len(knowledgestructure.get_agent_valid_worlds(turn_agent))

if turn_agent == -1:
    print ("The game ended in a TIE, no player can make a valid announcement anymore.")
else:
    # Huray!
    print ("Winner: Player {}".format("abcdefg"[turn_agent]))