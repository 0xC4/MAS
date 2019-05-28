class Agent:
    def __init__(self, name):
        self.name  = name
        self.cards = []

    def __repr__(self):
        return "Agent {}: (Cards: {})".format(str(self.name), self.cards)
    
    def give_card(self, card):
        self.cards.append(card)