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
                    for target_agent in range(self.knowledgestructure.amount_agents):
                        print ("[P{}->{}] ".format(agent, target_agent) + str(self.knowledgestructure.allowed_announcements(agent, target_agent)))
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
