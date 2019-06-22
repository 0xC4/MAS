from ks import KnowledgeStructure, Announcements
import itertools
import random
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from policies import Policies

P_AMOUNT_AGENTS = 3
P_AMOUNT_CARDS  = P_AMOUNT_AGENTS * 2

def print_world(world, vocab):
    true_idxs = [idx for idx, truth_value in enumerate(world) if truth_value == True] 
    
    facts = [vocab[i] for i in true_idxs]
    for i in range (int(len(facts) / 2)):
        print (str(facts[i*2:i*2+2]))

def run_game(amt_games=1):
    winners = []
    for game_idx in range(amt_games):
        knowledgestructure = KnowledgeStructure(amount_agents=P_AMOUNT_AGENTS, amount_cards=P_AMOUNT_CARDS)

        print (knowledgestructure)

        print_world(knowledgestructure.initial_world, knowledgestructure.vocab)

        remainingworlds = []

        turn_agent = -1
        pass_count = 0

        while remainingworlds != 1: # As long as one player does not have all the knowledge

            # Keep moving to the next player
            turn_agent = (turn_agent + 1) % P_AMOUNT_AGENTS


            # The agent has not made an announcement yet
            announcement_made = False
            
            choice = -1
            while choice != 0:
                print ()
                print ("# MENU")
                print ("[3] Show made announcements")
                print ("[2] Show agent holdings")
                print ("[1] Show possible announcements")
                print ("[ENTER] Next step")
                choice = input()
                print ()
                print ("----")
                print ()
                if choice == "":
                    choice = 0
                else:
                    choice = int (choice)
                if choice == 1:
                    for agent in range(P_AMOUNT_AGENTS):
                        for target_agent in range(P_AMOUNT_AGENTS):
                           print ("[P{}->{}] ".format(agent, target_agent) + str(knowledgestructure.allowed_announcements(agent, target_agent)))
                if choice == 2:
                    for i in range(P_AMOUNT_AGENTS):
                        print ("Agent {} has: {}".format("abcd"[i], knowledgestructure.get_agent_cards(knowledgestructure.initial_world, i)))
                if choice == 3:
                    idx = 0
                    for agent, announcement in knowledgestructure.prev_announced:
                        print ("Agent {} announced: Agent {}, {}".format("abcd"[idx%3], "abcd"[agent], announcement))
                        idx += 1
                
                if choice != 0:
                    print ()
                    print ("----")
                    print ()
            target_agents = list(range(P_AMOUNT_AGENTS))

            #Apply Policies
            #RANDOM, CHOOSE_OTHER_PLAYER, CHOOSE_THEMSELVES
            if knowledgestructure.observables[turn_agent]["policy"] in [Policies.RANDOM, Policies.CHOOSE_OTHER_PLAYER, Policies.CHOOSE_THEMSELVES]:

                random.shuffle(target_agents)

                #CHOOSE_OTHER_PLAYER puts self last in the list
                if knowledgestructure.observables[turn_agent]["policy"] == Policies.CHOOSE_OTHER_PLAYER:
                    target_agents.remove(turn_agent)
                    target_agents.append(turn_agent)
                    print(target_agents)

                #CHOOSE_THEMSELVES puts self first in the list
                if knowledgestructure.observables[turn_agent]["policy"] == Policies.CHOOSE_THEMSELVES:
                    target_agents.remove(turn_agent)
                    target_agents.insert(0,turn_agent)
                    print(target_agents)

                for target_agent in target_agents:
                    possible_announcements = knowledgestructure.allowed_announcements(turn_agent, target_agent)
                    
                    # Player cannot make an announcement about this target agent
                    if len(possible_announcements) < 1:
                        # Move to next target agent
                        continue
                    
                    # Otherwise make one of the possible announcements about this agent
                    print ("Agent {} announces: ".format("abcdefghij"[turn_agent]))
                    print(knowledgestructure.observables[turn_agent]["policy"])
                    knowledgestructure.announce(target_agent, random.sample(possible_announcements, 1)[0])
                    announcement_made = True
                    break

            #ARGMIN, ARGMAX
            if knowledgestructure.observables[turn_agent]["policy"] in [Policies.ARGMIN, Policies.ARGMAX]:
                possible_announcements = []
                best_announcement = None
                if knowledgestructure.observables[turn_agent]["policy"] == Policies.ARGMIN:
                    num_worlds = 1000
                elif knowledgestructure.observables[turn_agent]["policy"] == Policies.ARGMAX:
                    num_worlds = 0
                for target_agent in target_agents:
                    possible_announcements = knowledgestructure.allowed_announcements(turn_agent, target_agent)
                    for announcement in possible_announcements:
                        old_worlds = knowledgestructure.valid_worlds
                        knowledgestructure.announce(target_agent, announcement)
                        if knowledgestructure.observables[turn_agent]["policy"] == Policies.ARGMIN and len(knowledgestructure.valid_worlds) < num_worlds:
                            num_worlds = len(knowledgestructure.valid_worlds)
                            best_announcement = (target_agent, announcement)
                        elif knowledgestructure.observables[turn_agent]["policy"] == Policies.ARGMAX and len(knowledgestructure.valid_worlds) > num_worlds:
                            num_worlds = len(knowledgestructure.valid_worlds)
                            best_announcement = (target_agent, announcement)
                        knowledgestructure.valid_worlds = old_worlds
                if best_announcement != None:
                    print(best_announcement)
                    print ("Agent {} announces: ".format("abcdefghij"[turn_agent]))
                    print(knowledgestructure.observables[turn_agent]["policy"])
                    knowledgestructure.announce(best_announcement[0], best_announcement[1])
                    announcement_made = True

            if not announcement_made:
                print ("Agent {} passes because he cannot make any valid announcements.".format("abcdefghij"[turn_agent]))
                pass_count += 1
                if pass_count >= P_AMOUNT_AGENTS:
                    turn_agent = -1
                    break
                continue

            # If the turn player has only one valid world remaining, he knows everyones cards and wins the game
            remainingworlds = len(knowledgestructure.get_agent_valid_worlds(turn_agent))

        if turn_agent == -1:
            print ("The game ended in a TIE, no player can make a valid announcement anymore.")
        else:
            # Huray!
            print ("Winner: Player {}".format("abcdefg"[turn_agent]))
            winners.append("abcdefg"[turn_agent])
    return winners


#plot a histogram that shows win results for each player
def plot_win_hist(win_results):    
    counts = dict()
    for i in win_results:
        counts[i] = counts.get(i, 0) + 1

    plt.bar(list(counts.keys()), counts.values(), color='c')
    plt.title("Win counts of each player")
    plt.ylabel("Win count")
    plt.xlabel("Player ID")
    plt.show()

win_results = run_game(100)       #Turn up to increase number of games played. Printed output printed is not suppressed yet, sorry for this. A 1000 games will take about a minute to compute.
plot_win_hist(win_results)
