from model.agent import Agent
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

for agent in agents:
    print(agent)

# Create the knowledge model