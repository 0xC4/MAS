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
    ONE_ODD     = 0
    ONE_EVEN    = 1
    BOTH_ODD    = 2
    BOTH_EVEN   = 3
    ONE_HIGH    = 4
    ONE_LOW     = 5
    BOTH_HIGH   = 6
    BOTH_LOW    = 7

class KnowledgeStructure:
    def __init__ (self, amount_agents, amount_cards):
        self.amount_agents  = amount_agents
        self.amount_cards   = amount_cards
        self.vocab          = self.generate_vocab(self.amount_agents, self.amount_cards)
        self.valid_worlds   = self.get_valid_worlds()
        self.initial_world  = self.pick_initial_world(self.valid_worlds)
        self.observables    = self.make_agents_observables(self.amount_agents, self.initial_world, self.vocab)
        self.prev_announced = []

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
    def generate_all_world_possibilities(self):
        debug_old = False
        num_prop = self.amount_agents * self.amount_cards
        print('number of props:' + str(num_prop))
        num_worlds = 2**num_prop
        
        if debug_old: print(num_worlds)
        world_list = []
        for i in range(num_worlds):
            num = i
            single_world = []
            #make all possible worlds
            while(num>0):
                single_world.append(num%2)
                num = num//2
            #make worlds all same size
            while(len(single_world) < num_prop):
                single_world.append(0)
            #apply filters:
            if self.apply_state_laws(single_world):
                world_list.append(single_world)
                if debug_old: print(single_world)
        if debug_old:
            print(len(world_list))
            for i in range(6):
                count = 0
                for j in range(len(world_list)):
                    count += world_list[j][i]
                print(count)
        return world_list

    # Test whether a world is in accordance with the laws, returns false if world is invalid according to rules
    def apply_state_laws(self, world):
        return all([self.two_card_law(world), self.no_same_card_law(world)])

    # Returns only the worlds that are in accordance with the given laws
    def get_valid_worlds(self):
        return [world for world in self.generate_all_world_possibilities() if self.apply_state_laws(world)]

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
        oddagentworld = [w for idx, w in enumerate(agentworld) if idx%2 == 0] # ODD is even since index 0 corresponds with 1
        if sum(oddagentworld) > 0:
            return True
        return False

    # AT LEAST ONE even card
    def one_even_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        evenagentworld = [w for idx, w in enumerate(agentworld) if idx%2 == 1] # EVEN is odd since index 0 corresponds with 1
        if sum(evenagentworld) > 0:
            return True
        return False

    # BOTH ODD
    def both_odd_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        oddagentworld = [w for idx, w in enumerate(agentworld) if idx%2 == 0] # ODD is EVEN since index 0 corresponds with 1
        if sum(oddagentworld) == 2:
            return True
        return False

    # BOTH EVEN
    def both_even_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        oddagentworld = [w for idx, w in enumerate(agentworld) if idx%2 == 1] # EVEN is ODD since index 0 corresponds with 1
        if sum(oddagentworld) == 2:
            return True
        return False

    # AT LEAST ONE low card
    def one_low_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        oddagentworld = [w for idx, w in enumerate(agentworld) if idx <= 2] # LOW cards are 1 - 3
        if sum(oddagentworld) > 0:
            return True
        return False

    # AT LEAST ONE low card
    def one_high_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        oddagentworld = [w for idx, w in enumerate(agentworld) if idx >= 3] # HIGH cards are 1 - 3
        if sum(oddagentworld) > 0:
            return True
        return False

    # BOTH low cards
    def both_low_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        oddagentworld = [w for idx, w in enumerate(agentworld) if idx <= 2] # LOW cards are 1 - 3
        if sum(oddagentworld) == 2:
            return True
        return False

    # BOTH high cards
    def both_high_card_law(self, agent_idx, world):
        agentworld = world[agent_idx *self.amount_cards:agent_idx *self.amount_cards + self.amount_cards]
        oddagentworld = [w for idx, w in enumerate(agentworld) if idx >= 3] # HIGH cards are 1 - 3
        if sum(oddagentworld) == 2:
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

        if announcing_agent_idx == target_agent_idx:
            worlds = self.get_agent_valid_worlds(announcing_agent_idx)
        else: 
            worlds = self.valid_worlds
        
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
        return True

    def allowed_announcements(self, agent_idx, target_agent_idx):
        announcements = []
        for announcement_type in [Announcements.BOTH_ODD, Announcements.BOTH_EVEN, Announcements.ONE_EVEN, Announcements.ONE_ODD, Announcements.ONE_LOW, Announcements.ONE_HIGH, Announcements.BOTH_HIGH, Announcements.BOTH_LOW]:
            if self.announcement_allowed(agent_idx, target_agent_idx, announcement_type):
                announcements.append(announcement_type)
        return announcements