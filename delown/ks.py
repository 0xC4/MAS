import itertools
import random
from enum import Enum

class Announcements(Enum):
    ONE_ODD     = 0
    ONE_EVEN    = 1
    BOTH_ODD    = 2
    BOTH_EVEN   = 3

class KnowledgeStructure:
    def __init__ (self, amount_agents, amount_cards):
        self.amount_agents  = amount_agents
        self.amount_cards   = amount_cards
        self.vocab          = self.generate_vocab(self.amount_agents, self.amount_cards)
        self.valid_worlds   = self.get_valid_worlds()
        self.initial_world  = self.pick_initial_world(self.valid_worlds)
        self.observables    = self.make_agents_observables(self.amount_agents, self.initial_world, self.vocab)

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
        return list(itertools.product([True, False], repeat=self.amount_agents * self.amount_cards))

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

    # Make announcement and apply the new law
    def announce(self, agent_idx, announcement_type):
        previous_worlds = len(self.valid_worlds)

        if announcement_type == Announcements.ONE_ODD:
            print ("> Agent {} announces he has one odd card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_odd_card_law(agent_idx, w)]

        if announcement_type == Announcements.ONE_EVEN:
            print ("> Agent {} announces he has one even card.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.one_even_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_ODD:
            print ("> Agent {} announces he has both odd cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_odd_card_law(agent_idx, w)]

        if announcement_type == Announcements.BOTH_EVEN:
            print ("> Agent {} announces he has both even cards.".format("abcdefghijklmnopqrstuvwxyz"[agent_idx]))
            self.valid_worlds = [w for w in self.valid_worlds if self.both_even_card_law(agent_idx, w)]

        print (">> Worlds removed:   {}".format(previous_worlds - len(self.valid_worlds)))
        print (">> Worlds remaining: {}".format(len(self.valid_worlds)))

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