from ks import KnowledgeStructure, Announcements
import itertools
import random
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from policies import Policies
from gui import GUI, bcolors
import os


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

#returns the policy label used in the barplot
def get_policy_label(turn_agent, knowledgestructure, game_idx, n):
    print ("[Game {} of {}] Winner: Player {} with policy : ({})".format(game_idx + 1, n,"abcdefg"[turn_agent], knowledgestructure.observables[turn_agent]["policy"]))
    winner_label = "Agent "
    winner_label += "abcdefg"[turn_agent]
    winner_label += ": "
    winner_label += str(knowledgestructure.observables[turn_agent]["policy"])[9:]
    winner_label = winner_label.replace("_", " ")
    winner_label = winner_label.lower()
    return winner_label

#plot a barplot that shows win results for each player
#by default the plot is NOT saved to a file.
def plot_bar_plot(win_results, plot_filename, do_save_figure=False):
    counts = dict()
    for i in win_results:
        counts[i] = counts.get(i, 0) + 1

    plt.rcdefaults()
    
    fig, ax = plt.subplots()
    agents  = list(counts.keys())
    y_pos   = np.arange(len(agents))
    wins    = list(counts.values())
    
    for idx, agent in enumerate(agents):
        agents[idx] = agent.replace(" ", "\n")

    ax.barh(y_pos, wins, align='center', color='c')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(agents)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel("Win Count")
    ax.set_title("Win counts for each Agent")
    if do_save_figure:
        plt.savefig(plot_filename)
        print("\nWrote (file) plot to: " + plot_filename)
    plt.show()

#creates a plot filename based on program settings/parameters
def create_plot_filename(policy_set, number_of_games_played):
    plot_path = "plots/"

    if not os.path.exists(plot_path):
        os.mkdir(plot_path)
        print("Directory ",plot_path," Created ")
    else:
        print("Directory ",plot_path," already exists")

    plot_path += "games_" + str(number_of_games_played) + "-"
    for policy in policy_set:
        plot_path += str(policy).lower()[9:].replace(" ", "_")
        plot_path += "-"
    plot_path = plot_path[:-1]
    plot_path += ".png"
    return plot_path

############################################################################
#the amount of games that will be played
n = 1000

#Choose a policy for each agent:
    # RANDOM                  = 0     #Chooses a random possible move
    # CHOOSE_OTHER_PLAYER     = 1     #Favors choosing an announcement about another players rather than himself
    # CHOOSE_THEMSELVES 	  = 2     #Favors choosing an announcement about himself rather than about another player.
    # ARGMIN                  = 3     #Chooses the announcement that results in the lowest amount of possible worlds remaining after the announcement is made.
    # ARGMAX                  = 4     #Chooses the announcement that results in the highest amount of possible worlds remaining afther the announcement is made.
policy_set = [Policies.CHOOSE_THEMSELVES, Policies.CHOOSE_OTHER_PLAYER, Policies.CHOOSE_THEMSELVES]

#Create a plot filename based on program input 
# parameters (policies and amount of games played).
plot_filename = create_plot_filename(policy_set, n)

#Set to true if you want a menu after each step
# in the game. If set to False, you can run
# many games and see results of them in a
# barplot.
show_menu_each_step = False

#Run the game n times with the given policies
# and store the results.
win_results = run_game(n, policy_set, show_menu_each_step)

#Show a barplot of each player and policy, if
# you play more than one game and have the
# menu turned off.
if not show_menu_each_step and n>1:
    plot_bar_plot(win_results, plot_filename, do_save_figure=True)
