from model.agent import Agent
from model.knowledge import Fact, ReferedObject, Relation
from random import shuffle
from parameters import *

# Initialize deck of cards
deck = list(range(M_NUM_CARDS))

# Shuffle the deck
shuffle(deck)

# Create some agents
agents = [Agent(str(x)) for x in range (M_NUM_AGENTS)]

for agent in agents:
    agent.give_card(deck.pop())
    agent.give_card(deck.pop())

# Create the knowledge model
f = Fact(ReferedObject.ONE_CARD, Relation.IS_EVEN, agents[2])
agents[0].add_fact(f)

for agent in agents:
    print(agent)