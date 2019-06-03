from ks import KnowledgeStructure, Announcements
import itertools
import random
import numpy as np
import matplotlib.pyplot as plt

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

            for agent in range(P_AMOUNT_AGENTS):
                for target_agent in range(P_AMOUNT_AGENTS):
                    print ("[P{}->{}] ".format(agent, target_agent) + str(knowledgestructure.allowed_announcements(agent, target_agent)))

            # Random shuffle the target agents
            target_agents = list(range(P_AMOUNT_AGENTS))
            random.shuffle(target_agents)

            for target_agent in target_agents:
                possible_announcements = knowledgestructure.allowed_announcements(turn_agent, target_agent)
                
                # Player cannot make an announcement about this target agent
                if len(possible_announcements) < 1:
                    # Move to next target agent
                    continue
                
                # Otherwise make one of the possible announcements about this agent
                print ("Agent {} announces: ".format("abcdefghij"[turn_agent]))
                knowledgestructure.announce(target_agent, random.sample(possible_announcements, 1)[0])
                announcement_made = True
                break
            
            if not announcement_made:
                print ("Agent {} passes because he cannot make any valid announcements.")
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
    print(counts)

    plt.bar(list(counts.keys()), counts.values(), color='g')
    plt.title("Win counts of each player")
    plt.ylabel("Win count")
    plt.xlabel("Player ID")
    plt.show()


win_results = run_game(1000)
plot_win_hist(win_results)