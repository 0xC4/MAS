import itertools
import random
from enum import Enum
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from policies import Policies
from gui import ANMT, INFO, VALD

# Implemented announcements
class Announcements(Enum):
    # [!] Announcements starting with ONE refer to AT LEAST ONE
    # [!] Announcements starting with BOTH refer to both two cards

    # Parity announcements
    ONE_ODD         = 0
    ONE_EVEN        = 1
    BOTH_ODD        = 2
    BOTH_EVEN       = 3
    
    # Card value announcements where: {LOW=[1,2,3], HIGH=[4,5,6]}
    ONE_HIGH        = 4
    ONE_LOW         = 5
    BOTH_HIGH       = 6
    BOTH_LOW        = 7

    # Multiple of three announcements
    ONE_MUL_THREE   = 8
    BOTH_MUL_THREE  = 9 # See NOTE
    
    # Card difference announcement (Card values differ by 1)
    ONE_DIFF        = 10 # Says something about both cards
    
    # K-announcements
    # Targetted agent knows at least one card of player X
    K_ONE_CARD_A    = 11 # X = agent A
    K_ONE_CARD_B    = 12 # " "   "   B
    K_ONE_CARD_C    = 13 # " "   "   C

    # NOTE: Announcing BOTH_MUL_THREE in the current set-up can logically only
    #       be done about oneself. For, two multiples of three limits the 
    #       targets player's cards to [3,6], and logically, knowing an agent's
    #       both cards, as well as your own, means that you know the last 
    #       agent's cards as well. We left this in for fun, so that sometimes
    #       a player has to say it if it is the only announcement possible to
    #       make.

    # Not implemented, because with current settings, agents cannot make these
    # announcements about other players without already being the winner.
    #K_BOTH_CARD_A   = 14 
    #K_BOTH_CARD_B   = 15
    #K_BOTH_CARD_C   = 16

class KnowledgeStructure:
    def __init__ (self, amount_agents, amount_cards):
        # Amount of agents participating in the game (3)
        self.amount_agents  = amount_agents
        # Amount of cards in the game (6)
        self.amount_cards   = amount_cards
        # NOTE is this redundant?
        self.num_policies   = len(Policies)
        self.policies       = [Policies.RANDOM, Policies.CHOOSE_OTHER_PLAYER, Policies.CHOOSE_THEMSELVES]
        # The propositional atoms in the model
        self.vocab          = self.generate_vocab(self.amount_agents, self.amount_cards)
        # Stores the worlds which are still valid for at least one agent with the currently done announcements
        self.valid_worlds   = self.get_valid_worlds()
        # Pick one world to be the actual current world of the model
        self.initial_world  = self.pick_initial_world(self.valid_worlds)
        # Set the agents cards using the picked world
        self.observables    = self.make_agents_observables(self.amount_agents, self.initial_world, self.vocab)
        # Stores the previously made announcements
        self.prev_announced = []
        # Update the valid worlds by removing the worlds in which no agent has their own cards
        self.valid_worlds   = self.get_worlds_possible_for_agents()
        # Create an enumerated list of the initial worlds, used for maintaining world numbers after worlds
        # are deleted from the valid worlds list. Needed for relations and plotting the model with world numbers..
        self.make_enumerated_worlds()

    def __repr__(self):
        return """Model: 
        Amount agents:   {}
        Amount cards:    {}
        Prop. Atoms:     {}
        Amt val. worlds: {}""".format(self.amount_agents, self.amount_cards, self.vocab, len(self.valid_worlds))


    #creates a graph based on relations
    #addes nodes/relations and layout to the kripke model
    #all nodes is a list of lists containing all relations for each agent.
    #all relations is a list of lists that contains all relations of each agent.
    def make_graph(self):
        #create all relations and nodes in one list
        all_relations   = []
        all_nodes       = []
        edge_colors = ['b', 'm', 'chartreuse'] # Colors of edges
        G=nx.DiGraph()

        all_relations = [self.get_relations(agent_idx) for agent_idx in range(self.amount_agents)]
        all_nodes     = [self.get_nodes_agent(all_relations[agent_idx]) for agent_idx in range(self.amount_agents)]

        #add all nodes to the graph
        for world in self.valid_worlds:
            G.add_node([i for i, w in self.enumerated_worlds if world == w][0])

        pos=nx.spring_layout(G)
        labels={}       #init empty label dict

        line_collections = []
        #draw all nodes and edges
        for agent_idx in range(self.amount_agents):
            nx.draw_networkx_nodes(G, pos, nodelist=all_nodes[agent_idx], node_color='black', node_size=3000, alpha=1.0)
            line_collections.append(nx.draw_networkx_edges(G,pos, edgelist=all_relations[agent_idx], width=2, alpha=0.5, edge_color=edge_colors[agent_idx], arrows=True))

        for idx, node in enumerate(G.nodes()):
            extra_info = self.get_string_version_of_world(node)
            labels[node] = str(node) + "\n" + extra_info

        nx.draw_networkx_labels(G,pos,labels,font_size=8, font_color='c')
        proxies = [self.make_proxy(clr, line_collections[0], lw=5) for clr in edge_colors]
        plt.legend(proxies, ["Agent a", "Agent b", "Agent c"], loc='best')
        plt.title("Kripke Model of Numper Pile")
        plt.show()

    #helper function for creating a legend for the graph/kripke_model
    def make_proxy(self, clr, mappable, **kwargs):
        return Line2D([0, 1], [0, 1], color=clr, **kwargs)

    #returns a string version of the given world
    def get_string_version_of_world(self, world_idx):
        world = self.enumerated_worlds[world_idx][1]
        info = ""
        for agent_idx in range(self.amount_agents):
            agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
            cards = [i+1 for i, x in enumerate(agentworld) if x]
            info = info + "abcdefghijklmnopqrstuvwxyz"[agent_idx] + str(cards) + "\n"
        return info

    def get_agent_cards(self, world, agent_idx):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        return [i for i, x in enumerate(agentworld) if x]

    #returns a list of unique world names for an agent - a node is a possible world
    def get_nodes_agent(self, relations):
        nodes = []
        for tup in relations:
            for item in tup:
                if item not in nodes:
                    nodes.append(item)
        return nodes

    def make_enumerated_worlds(self):
        self.enumerated_worlds = list(enumerate(self.valid_worlds))
    
    # Get world number after worlds have been removed from the list of valid worlds
    def get_world_number (self, world):
        for idx, w in self.enumerated_worlds:
            if w == world:
                return idx
        return -1
    
    # Gets a list of tuples of two worlds for an agent between which there are a relations
    def get_relations (self, agent_idx):
        world_names = tuple([self.get_world_number(w) for w in self.get_agent_valid_worlds(agent_idx)])
        relations = list(itertools.product(world_names, repeat=2))
        return relations

    # Set of all propositional atoms
    def generate_vocab (self, amt_agents, amt_cards):
        vocab = []
        for agent in range(amt_agents): 
            for card in range(amt_cards):
                vocab.append(tuple(((card + 1), "abcdefghijklmnopqrstuvwxyz"[agent])))
        return vocab

    # All possible permutations of True and False value of propositional atoms for given amount agents and cards
    def get_valid_worlds(self):
        valid_worlds = []
        for obs in itertools.permutations(range(self.amount_cards)):
            world = [False] * self.amount_cards * self.amount_agents
            for idx, o in enumerate(obs):
                agent_idx = idx // 2
                # world[agent_idx*self.amount_cards:agent_idx*self.amount_cards + self.amount_cards])
                world[o + agent_idx * self.amount_cards] = True
                if self.apply_state_laws(world):
                    if world not in valid_worlds:
                        valid_worlds.append(world)
        return valid_worlds

    def get_agent_cards(self, world, agent_idx):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        return [i for i, x in enumerate(agentworld) if x]

    # Test whether a world is in accordance with the laws, returns false if world is invalid according to rules
    def apply_state_laws(self, world):
        return all([self.two_card_law(world), self.no_same_card_law(world)])

    # Returns only the worlds that are in accordance with the given laws
    def get_worlds_possible_for_agents(self):
        all_agent_valid_worlds = []
        for i in range(self.amount_agents):
            all_agent_valid_worlds += self.get_agent_valid_worlds(i)
        return [world for world in self.valid_worlds if world in all_agent_valid_worlds]

    # No agent can have more or less than two cards
    def two_card_law(self, world):
        for x in range (self.amount_agents):
            if sum(world[x*self.amount_cards:x*self.amount_cards + self.amount_cards]) != 2:
                return False
        return True

    # No more than one agent can have the same card
    def no_same_card_law(self, world):
        for i in range(self.amount_cards):
            cnt = 0
            for j in range(self.amount_agents):
                cnt += world[i + j * self.amount_cards]
            if cnt != 1:
                return False
        return True

    # AT LEAST ONE odd card
    def one_odd_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        odd_agentworld = [w for idx, w in enumerate(agentworld) if idx%2 == 0] # ODD is even since index 0 corresponds with 1
        if sum(odd_agentworld) > 0:
            return True
        return False

    # AT LEAST ONE even card
    def one_even_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        even_agentworld = [w for idx, w in enumerate(agentworld) if idx%2 == 1] # EVEN is odd since index 0 corresponds with 1
        if sum(even_agentworld) > 0:
            return True
        return False

    # BOTH ODD
    def both_odd_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        odd_agentworld = [w for idx, w in enumerate(agentworld) if idx%2 == 0] # ODD is EVEN since index 0 corresponds with 1
        if sum(odd_agentworld) == 2:
            return True
        return False

    # BOTH EVEN
    def both_even_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        even_agentworld = [w for idx, w in enumerate(agentworld) if idx%2 == 1] # EVEN is ODD since index 0 corresponds with 1
        if sum(even_agentworld) == 2:
            return True
        return False

    # AT LEAST ONE low card
    def one_low_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        low_agentworld = [w for idx, w in enumerate(agentworld) if idx <= 2] # LOW cards are 1 - 3
        if sum(low_agentworld) > 0:
            return True
        return False

    # AT LEAST ONE low card
    def one_high_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        high_agentworld = [w for idx, w in enumerate(agentworld) if idx >= 3] # HIGH cards are 1 - 3
        if sum(high_agentworld) > 0:
            return True
        return False

    # BOTH low cards
    def both_low_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        low_agentworld = [w for idx, w in enumerate(agentworld) if idx <= 2] # LOW cards are 1 - 3
        if sum(low_agentworld) == 2:
            return True
        return False

    # BOTH high cards
    def both_high_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        high_agentworld = [w for idx, w in enumerate(agentworld) if idx >= 3] # HIGH cards are 1 - 3
        if sum(high_agentworld) == 2:
            return True
        return False


    # AT LEAST ONE of my cards is a multiple of three.
    def one_multiple_three_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        mul_three_agentworld = [w for idx, w in enumerate(agentworld) if (idx+1)%3 == 0] # (idx+1) because the cards start at index 1 instead of index 0.
        if sum(mul_three_agentworld) > 0:
            return True
        return False

    # BOTH of my cards are a multiple of three.
    def both_multiple_three_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        mul_three_agentworld = [w for idx, w in enumerate(agentworld) if (idx+1)%3 == 0] # (idx+1) because the cards start at index 1 instead of index 0.
        if sum(mul_three_agentworld) > 1:
            return True
        return False

    # My numbers only differ by one number, so it should return true if you have a (1,2) or (5,6) for example.
    def one_diff_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        one_diff_agentworld = []
        for idx, w in enumerate(agentworld):
            if idx < (len(agentworld)-1):
                if agentworld[idx] == 1 and agentworld[idx+1] == 1:             #two indices next to each other have a value that contains true.
                    one_diff_agentworld.append(w)
        if sum(one_diff_agentworld) > 0:
            return True
        return False
    
    # I know one card of the target agent, with certainty.
    def knows_one_card_law(self, src_agent, target_agent):

        # Obtain valid worlds for the announcing agent
        announcing_agent_worlds = self.valid_worlds

        # Initial known cards
        for w1 in announcing_agent_worlds:
            known_cards = (self.get_agent_cards(w1, target_agent))
           
            # Take one step with K-relations
            for w2 in announcing_agent_worlds:

                # Source agent cards must remain constant between worlds
                if not self.get_agent_cards(w1, src_agent) == self.get_agent_cards(w2, src_agent):
                    continue
               
                # Update the list of cards that are the same between the related worlds
                known_cards = [c for c in known_cards if c in self.get_agent_cards(w2, target_agent)]
                
                # If there are no cards that remain constant between all related worlds
                # src agent is not always in a world where he knows one card of target_agent
                if len(known_cards) < 1:
                    return False
        return True

    # Make announcement and apply the new law
    # If verbose is set to True, print the announcement.
    def announce(self, agent_idx, announcement_type, verbose=True):
        previous_worlds = len(self.valid_worlds)
        
        if announcement_type == Announcements.ONE_ODD:
            if verbose: 
                print (ANMT + " Agent {} has one odd card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_odd_card_law(agent_idx, w)]

        if announcement_type == Announcements.ONE_EVEN:
            if verbose: 
                print (ANMT + " Agent {} has one even card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_even_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_ODD:
            if verbose: 
                print (ANMT + " Agent {} has both odd cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_odd_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_EVEN:
            if verbose: 
                print (ANMT + " Agent {} has both even cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_even_card_law(agent_idx, w)]

        if announcement_type == Announcements.ONE_LOW:
            if verbose: 
                print (ANMT + " Agent {} has one low card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_low_card_law(agent_idx, w)]

        if announcement_type == Announcements.ONE_HIGH:
            if verbose: 
                print (ANMT + " Agent {} has one high card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_high_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_LOW:
            if verbose: 
                print (ANMT + " Agent {} has both low cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_low_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_HIGH:
            if verbose: 
                print (ANMT + " Agent {} has both high cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_high_card_law(agent_idx, w)]

        if announcement_type == Announcements.ONE_MUL_THREE:
            if verbose: 
                print (ANMT + " Agent {} has one multiple of three card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_multiple_three_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_MUL_THREE:
            if verbose: 
                print (ANMT + " Agent {} has two multiple of three cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_multiple_three_card_law(agent_idx, w)]

        if announcement_type == Announcements.ONE_DIFF:
            if verbose: 
                print (ANMT + " Agent {} announces he has two cards that only differ by one.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_diff_card_law(agent_idx, w)]

        # K-ANNOUNCEMENTS
        if announcement_type == Announcements.K_ONE_CARD_A:
            if verbose: 
                print (ANMT + " Agent {} knows one card of agent a".format("abcd"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.knows_one_card_law(agent_idx, 0)]

        if announcement_type == Announcements.K_ONE_CARD_B:
            if verbose: 
                print (ANMT + " Agent {} knows one card of agent b".format("abcd"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.knows_one_card_law(agent_idx, 1)]

        if announcement_type == Announcements.K_ONE_CARD_C:
            if verbose: 
                print (ANMT + " Agent {} knows one card of agent c".format("abcd"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.knows_one_card_law(agent_idx, 2)]

        # Store the announcement in the list of already made announcements
        self.prev_announced.append(tuple((agent_idx, announcement_type)))
        
        # Report on the amount of valid worlds that have been removed, and the amount of valid worlds 
        # that remain for each agent.
        if verbose: 
            print (INFO + " Worlds removed:   {}".format(previous_worlds - len(self.valid_worlds)))
            print ("    Worlds remaining: {}".format(len(self.valid_worlds)))
            self.print_agent_valid_worlds()

    # Create agents and their respective observables
    # Also contains information about the policy of the agent.
    def make_agents_observables(self, amount_agents, init_world, vocab):
        agents = list()
        for i in range(amount_agents):
            agent = dict()
            agent["name"] = "abcdefghijklmnopqrstuvwxyz"[i]
            agent["observations"] = [vocab.index(obs) for obs in self.get_observations_from_world(init_world, i)]
            agent["policy"] = self.policies[i]
            agents.append(agent)
        return agents

    # Picks a random initial world as the actual world as a random sample of the valid worlds
    def pick_initial_world(self, valid_worlds):
        return random.sample (valid_worlds, 1)[0]

    # Returns the observables for each agent from the initial picked world
    def get_observations_from_world (self, world, agent_idx):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        obs = [(idx + 1, "abcdefghijklmnopqrstuvwxyz"[agent_idx]) for idx, truth in enumerate(agentworld) if truth]
        return obs
    
    # Take subset of valid worlds where the agents own cards are known
    def get_agent_valid_worlds(self, agent_idx):
        worlds = []
        for world in self.valid_worlds:
            # Take the intersection of all valid worlds, and the worlds where the agent
            # has the cards which he actually has.
            if all([world[obs] for obs in self.observables[agent_idx]["observations"]]):
                worlds.append(world)
        return worlds
    
    # Print the valid worlds for each agent in the knowledgestructure.
    def print_agent_valid_worlds(self):
        print (VALD + " Valid worlds:")
        for agent_idx in range(self.amount_agents):
            print ("    Agent {}: {}".format("abcdefghijklmnopqrstuvwxyz"[agent_idx], len(self.get_agent_valid_worlds(agent_idx))))
    
    # Determines whether an agent is allowed to make a given announcement about a given target
    # agent. Evaluates if the agent is totally certain about the announcement, and whether the 
    # announcement has been made before.
    # Applies the announcement laws to all valid worlds for the agent, to see if it holds in all of them.
    def announcement_allowed(self, announcing_agent_idx, target_agent_idx, announcement_type):
        # Don't allow the same announcement about same agent's cards twice
        if (tuple((target_agent_idx, announcement_type)) in self.prev_announced):
            return False
        
        # Get the current valid worlds for the announcing agent
        worlds = self.get_agent_valid_worlds(announcing_agent_idx)

        # Loop over all of them
        for world in worlds: 

            # Check if the law associated with the announcement holds 
            if announcement_type == Announcements.ONE_ODD:
                if not self.one_odd_card_law(target_agent_idx, world):
                    return False
            if announcement_type == Announcements.ONE_EVEN:
                if not self.one_even_card_law(target_agent_idx, world):
                    return False
            if announcement_type == Announcements.BOTH_ODD:
                if not self.both_odd_card_law(target_agent_idx, world):
                    return False
            if announcement_type == Announcements.BOTH_EVEN:
                if not self.both_even_card_law(target_agent_idx, world):
                    return False
            if announcement_type == Announcements.ONE_LOW:
                if not self.one_low_card_law(target_agent_idx, world):
                    return False
            if announcement_type == Announcements.ONE_HIGH:
                if not self.one_high_card_law(target_agent_idx, world):
                    return False
            if announcement_type == Announcements.BOTH_LOW:
                if not self.both_low_card_law(target_agent_idx, world):
                    return False
            if announcement_type == Announcements.BOTH_HIGH:
                if not self.both_high_card_law(target_agent_idx, world):
                    return False
            if announcement_type == Announcements.ONE_MUL_THREE:
                if not self.one_multiple_three_card_law(target_agent_idx, world):
                    return False
            if announcement_type == Announcements.BOTH_MUL_THREE:
                if not self.both_multiple_three_card_law(target_agent_idx, world):
                    return False
            if announcement_type == Announcements.ONE_DIFF:
                if not self.one_diff_card_law(target_agent_idx, world):
                    return False
        
        # K-Announcements loop over more than the valid worlds of the announcing agent
        # since they pertain to the knowledge of the targetted agent. Therefor we 
        # loop seperately within the law.
        if announcement_type == Announcements.K_ONE_CARD_A:
            if not self.knows_one_card_law(target_agent_idx, 0):
                return False
         
        if announcement_type == Announcements.K_ONE_CARD_B:
            if not self.knows_one_card_law(target_agent_idx, 1):
                return False
        
        if announcement_type == Announcements.K_ONE_CARD_C:
            if not self.knows_one_card_law(target_agent_idx, 2):
                return False
        
        # If the announcement law holds in all worlds, return true
        return True

    # Returns a list of the announcements which an agent is allowed to make with
    # the inferences that it can make combining the knowledge of their own cards,
    # as well as the knowledge obtained from the public announcements made by 
    # other agents.
    def allowed_announcements(self, agent_idx, target_agent_idx):
        announcements = []
        # Loop over all announcements
        for announcement_type in [Announcements.BOTH_ODD, Announcements.BOTH_EVEN, Announcements.ONE_EVEN, Announcements.ONE_ODD, Announcements.ONE_LOW, Announcements.ONE_HIGH, Announcements.BOTH_HIGH, Announcements.BOTH_LOW, Announcements.ONE_MUL_THREE, Announcements.BOTH_MUL_THREE, Announcements.ONE_DIFF, Announcements.K_ONE_CARD_A, Announcements.K_ONE_CARD_B, Announcements.K_ONE_CARD_C]:
            # if the announcement can be made with certainty by the agent with its current knowledge
            if self.announcement_allowed(agent_idx, target_agent_idx, announcement_type):
                # Append it to the list of allowed announcements
                announcements.append(announcement_type)
        return announcements
