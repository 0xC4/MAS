class Agent:
    def __init__(self, name):
        self.name  = name
        self.cards = []
        self.facts = []

    def __repr__(self):
        return "Agent {}: (Cards: {}) \nKnows facts: {}".format(str(self.name), self.cards, self.facts)
    
    def give_card(self, card):
        self.cards.append(card)

    def add_fact(self, fact):
        self.facts.append(fact)