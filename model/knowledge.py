from enum import Enum

class KnowledgeModel:
    def __init__(self):
        self.announcements = []
    
    def add_announcements(self, fact):
        self.announcements.append(fact)

class ReferedObject (Enum):
    ONE_CARD        = 0
    BOTH_CARDS      = 1
    NO_CARD         = 2

class Relation (Enum):
    IS_EVEN         = 0
    IS_ODD          = 1
    IS_HIGH         = 2
    IS_LOW          = 3

class Fact:
    def __init__(self, target, relation, dst_agent):
        self.target   = target
        self.relation = relation
        self.dst_agent= dst_agent
    
    def __repr__(self):
        return "agent{}-{}-{}".format(self.dst_agent.name, self.target, self.relation)

def AllPossibleFacts(self_agent, owncards):
    facts = []
    if(any([card % 2 == 1 for card in owncards])):
        facts.append(Fact(ReferedObject.ONE_CARD, Relation.IS_ODD, self_agent))
    if(any([card % 2 == 0 for card in owncards])):
        facts.append(Fact(ReferedObject.ONE_CARD, Relation.IS_EVEN, self_agent))
    if(all([card % 2 == 1 for card in owncards])):
        facts.append(Fact(ReferedObject.BOTH_CARDS, Relation.IS_ODD, self_agent))
        facts.append(Fact(ReferedObject.NO_CARD, Relation.IS_EVEN, self_agent))
    if(all([card % 2 == 0 for card in owncards])):
        facts.append(Fact(ReferedObject.BOTH_CARDS, Relation.IS_EVEN, self_agent))
        facts.append(Fact(ReferedObject.NO_CARD, Relation.IS_ODD, self_agent))
    return facts