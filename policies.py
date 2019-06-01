from enum import Enum


class Policies(Enum):
    RANDOM                  = 0     #Chooses a random possible move
    CHOOSE_OTHER_PLAYER     = 1     #Favors choosing an announcement about another players rather than himself
    CHOOSE_PLAYER_HIMSELF   = 2     #Favors choosing an announcement about himself rather than about another player.
    ARGMIN                  = 3     #Chooses the announcement that results in the lowest amount of possible worlds remaining after the announcement is made.
    ARGMAX                  = 4     #Chooses the announcement that results in the highest amount of possible worlds remaining afther the announcement is made.
    HUMAN                   = 5     #human player.