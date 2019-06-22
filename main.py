from ks import KnowledgeStructure, Announcements
import itertools
import random
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from policies import Policies
from gui import GUI, bcolors

P_AMOUNT_AGENTS = 3
P_AMOUNT_CARDS  = P_AMOUNT_AGENTS * 2

# Initialize the GUI class for showing the menu etc.

def print_world(world, vocab):
    true_idxs = [idx for idx, truth_value in enumerate(world) if truth_value == True] 
    
    facts = [vocab[i] for i in true_idxs]
    for i in range (int(len(facts) / 2)):
        print (str(facts[i*2:i*2+2]))

def run_game(amt_games=1, policy_set=[Policies.RANDOM, Policies.RANDOM, Policies.RANDOM], show_menu_each_step=True):
    
    # Only prints if we are running in step mode
    def printc (string):
        if show_menu_each_step:
            print (string)

    winners = []
    for game_idx in range(amt_games):
        knowledgestructure = KnowledgeStructure(amount_agents=P_AMOUNT_AGENTS, amount_cards=P_AMOUNT_CARDS)
        #Apply Policies to each agent
        for idx, policy in enumerate(policy_set):
            knowledgestructure.observables[idx]["policy"] = policy

        gui = GUI(ks=knowledgestructure)
        
        printc(bcolors.HEADER + "\n\n--- NEW GAME [{} of {}] ---".format(game_idx + 1, n)+ bcolors.ENDC)
        printc(knowledgestructure)

        if show_menu_each_step:
            print_world(knowledgestructure.initial_world, knowledgestructure.vocab)

        remainingworlds = []

        turn_agent = -1
        pass_count = 0

        while remainingworlds != 1: # As long as one player does not have all the knowledge

            # Keep moving to the next player
            turn_agent = (turn_agent + 1) % P_AMOUNT_AGENTS

            # The agent has not made an announcement yet
            announcement_made = False
            
            # Show the menu
            if show_menu_each_step:
                gui.show_menu()
            
            target_agents = list(range(P_AMOUNT_AGENTS))

            #RANDOM, CHOOSE_OTHER_PLAYER, CHOOSE_THEMSELVES
            if knowledgestructure.observables[turn_agent]["policy"] in policy_set:

                random.shuffle(target_agents)

                #CHOOSE_OTHER_PLAYER puts self last in the list
                if knowledgestructure.observables[turn_agent]["policy"] == Policies.CHOOSE_OTHER_PLAYER:
                    target_agents.remove(turn_agent)
                    target_agents.append(turn_agent)
                    printc(target_agents)

                #CHOOSE_THEMSELVES puts self first in the list
                if knowledgestructure.observables[turn_agent]["policy"] == Policies.CHOOSE_THEMSELVES:
                    target_agents.remove(turn_agent)
                    target_agents.insert(0,turn_agent)
                    printc(target_agents)

                for target_agent in target_agents:
                    possible_announcements = knowledgestructure.allowed_announcements(turn_agent, target_agent)
                    
                    # Player cannot make an announcement about this target agent
                    if len(possible_announcements) < 1:
                        # Move to next target agent
                        continue
                    
                    # Otherwise make one of the possible announcements about this agent
                    printc ("Agent {} announces: ".format("abcdefghij"[turn_agent]))
                    printc(knowledgestructure.observables[turn_agent]["policy"])
                    knowledgestructure.announce(target_agent, random.sample(possible_announcements, 1)[0], verbose=show_menu_each_step)
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
                    printc(best_announcement)
                    printc ("Agent {} announces: ".format("abcdefghij"[turn_agent]))
                    printc(knowledgestructure.observables[turn_agent]["policy"])
                    knowledgestructure.announce(best_announcement[0], best_announcement[1], verbose=False)
                    announcement_made = True

            if not announcement_made:
                printc ("Agent {} passes because he cannot make any valid announcements.".format("abcdefghij"[turn_agent]))
                pass_count += 1
                if pass_count >= P_AMOUNT_AGENTS:
                    turn_agent = -1
                    break
                continue

            # If the turn player has only one valid world remaining, he knows everyones cards and wins the game
            remainingworlds = len(knowledgestructure.get_agent_valid_worlds(turn_agent))

        if turn_agent == -1:
            print ("[Game {} of {}] The game ended in a TIE, no player can make a valid announcement anymore.".format(game_idx + 1, n))
        else:
            winners.append(get_policy_label(turn_agent, knowledgestructure, game_idx, n))
    return winners

#returns the policy label used in the histogram plot
def get_policy_label(turn_agent, knowledgestructure, game_idx, n):
    print ("[Game {} of {}] Winner: Player {} with policy : ({})".format(game_idx + 1, n,"abcdefg"[turn_agent], knowledgestructure.observables[turn_agent]["policy"]))
    winner_label = "Agent "
    winner_label += "abcdefg"[turn_agent]
    winner_label += ": "
    winner_label += str(knowledgestructure.observables[turn_agent]["policy"])[9:]
    winner_label = winner_label.replace("_", " ")
    winner_label = winner_label.lower()
    return winner_label


#plot a histogram that shows win results for each player
def plot_win_hist(win_results):    
    counts = dict()
    for i in win_results:
        counts[i] = counts.get(i, 0) + 1

    plt.bar(list(counts.keys()), counts.values(), color='c')
    plt.title("Win counts of each player")
    plt.ylabel("Win count")
    plt.xlabel("Policy of player")
    plt.show()

############################################################################
#the amount of games that will be played
n = 100

#Choose a policy for each agent:
    # RANDOM                  = 0     #Chooses a random possible move
    # CHOOSE_OTHER_PLAYER     = 1     #Favors choosing an announcement about another players rather than himself
    # CHOOSE_THEMSELVES 	  = 2     #Favors choosing an announcement about himself rather than about another player.
    # ARGMIN                  = 3     #Chooses the announcement that results in the lowest amount of possible worlds remaining after the announcement is made.
    # ARGMAX                  = 4     #Chooses the announcement that results in the highest amount of possible worlds remaining afther the announcement is made.
policy_set = [Policies.RANDOM, Policies.RANDOM, Policies.RANDOM]

#Set to true if you want a menu after each step
# in the game. If set to False, you can run
# many games and see results of them in a
# histogram.
show_menu_each_step = True

#Turn up to increase number of games played. 
# Printed output printed is not suppressed
# yet, sorry for this. A 1000 games will 
# take about a minute to compute.
win_results = run_game(n, policy_set, show_menu_each_step)
if not show_menu_each_step and n>1:             #you probably do not want a histogram if you play just one game
    plot_win_hist(win_results)
