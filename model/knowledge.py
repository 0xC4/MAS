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
    FIRST_CARD      = 3
    SECOND_CARD     = 4

class Relation (Enum):
    IS_EVEN         = 0
    IS_ODD          = 1
    IS_HIGH         = 2
    IS_LOW          = 3

class Fact:
    def __init__(self, target, relation, agent):
        self.target   = target
        self.relation = relation
        self.agent    = agent
    