
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

def get_announcement_string(a):
    from ks import Announcements
    if a == Announcements.ONE_ODD:
        return "Agent {} has at least one odd card"
    if a == Announcements.BOTH_ODD:
        return "Agent {} has two odd cards"
    if a == Announcements.ONE_HIGH:
        return "Agent {} has at least one high card"
    if a == Announcements.BOTH_HIGH:
        return "Agent {} has two high cards"
    if a == Announcements.ONE_LOW:
        return "Agent {} has at least one low card"
    if a == Announcements.BOTH_LOW:
        return "Agent {} has two low cards"
    if a == Announcements.ONE_EVEN:
        return "Agent {} has at least one even card"
    if a == Announcements.BOTH_EVEN:
        return "Agent {} has two even cards"
    if a == Announcements.ONE_DIFF:
        return "Agent {} has two cards that are 1 number apart"
    if a == Announcements.ONE_MUL_THREE:
        return "Agent {} has at least one card that is a multiple of three"
    if a == Announcements.BOTH_MUL_THREE:
        return "Agent {} has two cards that are a multiple of three"
    if a == Announcements.K_ONE_CARD_A:
        return "Agent {} knows one card of agent a"
    if a == Announcements.K_ONE_CARD_B:
        return "Agent {} knows one card of agent b"
    if a == Announcements.K_ONE_CARD_C:
        return "Agent {} knows one card of agent c"

class GUI:
    def __init__(self, ks):
        self.knowledgestructure = ks

    def show_menu (self):
        choice = -1
        while choice != 0:
            print ()
            print ("# MENU")
            print ("[4] Show current Kripke model")
            print ("[3] Show made announcements")
            print ("[2] Show agent holdings")
            print ("[1] Show possible announcements")
            print ("[ENTER] Next step")
            choice = input()
            print ()
            print ("----")
            print ()
            if choice == "":
                choice = 0
            else:
                choice = int (choice)
            if choice == 1:
                for agent in range(self.knowledgestructure.amount_agents):
                    print (bcolors.HEADER + "Possible announcements for agent {}".format("ABCD"[agent]) + bcolors.ENDC)
                    for target_agent in range(self.knowledgestructure.amount_agents):
                        for ann in self.knowledgestructure.allowed_announcements(agent, target_agent):
                            print (get_announcement_string(ann).format("abcd"[target_agent]))
                    print ()
            if choice == 2:
                for i in range(self.knowledgestructure.amount_agents):
                     print ("Agent {} has: {}".format("abcd"[i], [c+1 for c in self.knowledgestructure.get_agent_cards(self.knowledgestructure.initial_world, i)]))
            if choice == 3:
                idx = 0
                for agent, announcement in self.knowledgestructure.prev_announced:
                    print ("Agent {} announced: Agent {}, {}".format("abcd"[idx%3], "abcd"[agent], announcement))                        
                    idx += 1
            if choice == 4:
                self.knowledgestructure.make_graph()
            if choice != 0:
                print ()
                print ("----")
                print ()
