# Multi Agent Systems 2019 - RUG
## Number Pile in Python3
MAS Project 2019
In main.py at the bottom of the file the program parameters can be set.
By default it will loop over all available policies and try all combinations against each other.

The program can be run from the 'MAS/' directory with the command: python3 main.py

### Dependencies
1. itertools
2. numpy
3. networkx
4. matplotlib

### Parameters:
1. n

Amount of games to be played.

2. m

Amount of experiments run. Default set to 10. Will result in an average win count over 10 experiments.
A total of m*n games will be played.

3. do_save_figure

save the generated experiment to a figure

4. do_show_figure

Shows the figure at the end of the experiment.

5. show_menu_each_step

When set to 'True', at each step in the game the user can:
    1. Show possible announcements.
    2. Show Agent holdings.
    3. Show all made announcements.
    4. Show Kripke Model

###Choose a policy for each agent:    
#### RANDOM
Chooses a random possible move

#### CHOOSE_OTHER_PLAYER
Favors choosing an announcement about another players rather than himself

#### CHOOSE_THEMSELVES
Favors choosing an announcement about himself rather than about another player.

#### ARGMIN
Chooses the announcement that results in the lowest amount of possible worlds remaining after the announcement is made.

#### ARGMAX
Chooses the announcement that results in the highest amount of possible worlds remaining afther the announcement is made.
