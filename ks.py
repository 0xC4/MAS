import itertools
import random
from enum import Enum

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
ANMT = bcolors.FAIL + "[A]" + bcolors.ENDC
INFO = bcolors.OKBLUE + "[I]" + bcolors.ENDC
VALD = bcolors.WARNING + "[V]" + bcolors.ENDC

class Announcements(Enum):
    ONE_ODD         = 0
    ONE_EVEN        = 1
    BOTH_ODD        = 2
    BOTH_EVEN       = 3
    ONE_HIGH        = 4
    ONE_LOW         = 5
    BOTH_HIGH       = 6
    BOTH_LOW        = 7
    ONE_MUL_THREE   = 8
    BOTH_MUL_THREE  = 9
    ONE_DIFF        = 10

class KnowledgeStructure:
    def __init__ (self, amount_agents, amount_cards):
        self.amount_agents  = amount_agents
        self.amount_cards   = amount_cards
        self.vocab          = self.generate_vocab(self.amount_agents, self.amount_cards)
        self.valid_worlds   = self.get_valid_worlds()
        self.initial_world  = self.pick_initial_world(self.valid_worlds)
        self.observables    = self.make_agents_observables(self.amount_agents, self.initial_world, self.vocab)
        self.prev_announced = []
        self.valid_worlds   = self.get_worlds_possible_for_agents()
        self.make_enumerated_worlds()

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

    def __repr__(self):
        return """Model: 
        Amount agents:   {}
        Amount cards:    {}
        Prop. Atoms:     {}
        Amt val. worlds: {}""".format(self.amount_agents, self.amount_cards, self.vocab, len(self.valid_worlds))

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

    # Make announcement and apply the new law
    def announce(self, agent_idx, announcement_type):
        previous_worlds = len(self.valid_worlds)
        
        if announcement_type == Announcements.ONE_ODD:
            print (ANMT + " Agent {} has one odd card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_odd_card_law(agent_idx, w)]

        if announcement_type == Announcements.ONE_EVEN:
            print (ANMT + " Agent {} has one even card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_even_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_ODD:
            print (ANMT + " Agent {} has both odd cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_odd_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_EVEN:
            print (ANMT + " Agent {} has both even cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_even_card_law(agent_idx, w)]

        if announcement_type == Announcements.ONE_LOW:
            print (ANMT + " Agent {} has one low card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_low_card_law(agent_idx, w)]

        if announcement_type == Announcements.ONE_HIGH:
            print (ANMT + " Agent {} has one high card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_high_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_LOW:
            print (ANMT + " Agent {} has both low cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_low_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_HIGH:
            print (ANMT + " Agent {} has both high cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_high_card_law(agent_idx, w)]

        if announcement_type == Announcements.ONE_MUL_THREE:
            print (ANMT + " Agent {} has one multiple of three card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_multiple_three_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_MUL_THREE:
            print (ANMT + " Agent {} has two multiple of three cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_multiple_three_card_law(agent_idx, w)]

        if announcement_type == Announcements.ONE_DIFF:
            print (ANMT + " Agent {} announces he has two cards that only differ by one.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_diff_card_law(agent_idx, w)]

        # Store the announcement in the list of already made announcements
        self.prev_announced.append(tuple((agent_idx, announcement_type)))

        print (INFO + " Worlds removed:   {}".format(previous_worlds - len(self.valid_worlds)))
        print ("    Worlds remaining: {}".format(len(self.valid_worlds)))
        self.print_agent_valid_worlds()

    # Create agents and their respective observables
    def make_agents_observables(self, amount_agents, init_world, vocab):
        agents = list()
        for i in range(amount_agents):
            agent = dict()
            agent["name"] = "abcdefghijklmnopqrstuvwxyz"[i]
            agent["observations"] = [vocab.index(obs) for obs in self.get_observations_from_world(init_world, i)]
            agents.append(agent)
        return agents

    # Picks a random initial world
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
            if all([world[obs] for obs in self.observables[agent_idx]["observations"]]):
                worlds.append(world)
        return worlds

    def print_agent_valid_worlds(self):
        print (VALD + " Valid worlds:")
        for agent_idx in range(self.amount_agents):
            print ("    Agent {}: {}".format("abcdefghijklmnopqrstuvwxyz"[agent_idx], len(self.get_agent_valid_worlds(agent_idx))))

    def announcement_allowed(self, announcing_agent_idx, target_agent_idx, announcement_type):
        # Don't allow the same announcement about same agent's cards twice
        if (tuple((target_agent_idx, announcement_type)) in self.prev_announced):
            return False
        worlds = self.get_agent_valid_worlds(announcing_agent_idx)
        for world in worlds: 
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
        return True

    def allowed_announcements(self, agent_idx, target_agent_idx):
        announcements = []
        for announcement_type in [Announcements.BOTH_ODD, Announcements.BOTH_EVEN, Announcements.ONE_EVEN, Announcements.ONE_ODD, Announcements.ONE_LOW, Announcements.ONE_HIGH, Announcements.BOTH_HIGH, Announcements.BOTH_LOW, Announcements.ONE_MUL_THREE, Announcements.BOTH_MUL_THREE, Announcements.ONE_DIFF]:
            if self.announcement_allowed(agent_idx, target_agent_idx, announcement_type):
                announcements.append(announcement_type)
        return announcements
