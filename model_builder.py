from mlsolver.mlsolver.kripke import World, KripkeStructure

# 1n 2n 3n 4n 5n 6n 1e 2e 3e 4e 5e 6e 1s 2s 3s 4s 5s 6s
num_prop = 18
num_worlds = 2**num_prop
debug_old = False
debug_new = True

def filter_world(world):
	#people have exactly 2 cards
	if not(sum(world[:6]) == 2 and sum(world[6:12]) == 2 and sum(world[12:]) == 2):
		return False
	# people can't have the same card
	for i in range(6):
		if not((world[i] + world[i+6] + world[i+12]) == 1):
			return False
	return True

def convert_worlds(worlds):
	worlds_new = []
	for idx, world in enumerate(worlds):
		world_new = World(str(idx), {'1a': bool(world[0]),
									 '2a': bool(world[1]),
									 '3a': bool(world[2]),
									 '4a': bool(world[3]),
									 '5a': bool(world[4]),
									 '6a': bool(world[5]),
									 '1b': bool(world[6]),
									 '2b': bool(world[7]),
									 '3b': bool(world[8]),
									 '4b': bool(world[9]),
									 '5b': bool(world[10]),
									 '6b': bool(world[11]),
									 '1c': bool(world[12]),
									 '2c': bool(world[13]),
									 '3c': bool(world[14]),
									 '4c': bool(world[15]),
									 '5c': bool(world[16]),
									 '6c': bool(world[17]),
									 })
		if debug_new: print(world_new)
		worlds_new.append(world_new)
	return worlds_new

def make_worlds():
	if debug_old: print(num_worlds)
	world_list = []
	for i in range(num_worlds):
		num = i
		single_world = []
		#make all possible worlds
		while(num>0):
			single_world.append(num%2)
			num = num//2
		#make worlds all same size
		while(len(single_world) < num_prop):
			single_world.append(0)
		#apply filters:
		if filter_world(single_world):
			world_list.append(single_world)
			if debug_old: print(single_world)
	if debug_old:
		print(len(world_list))
		for i in range(6):
			count = 0
			for j in range(len(world_list)):
				count += world_list[j][i]
			print(count)
	return world_list

def make_relations(world_list):
	r1 = []
	r2 = []
	r3 = []
	for idx1, world1 in enumerate(world_list):
		for idx2, world2 in enumerate(world_list):
			if world1[:6] == world2[:6]:
				r1.append((str(idx1),str(idx2)))
			if world1[6:12] == world2[6:12]:
				r2.append((str(idx1),str(idx2)))
			if world1[12:] == world2[12:]:
				r3.append((str(idx1),str(idx2)))
	if debug_old:
		for i in r1:
			print(i)
	return r1, r2, r3

def make_model():
	world_list = make_worlds()
	r1, r2, r3 = make_relations(world_list)
	world_list = convert_worlds(world_list)
	return (world_list, r1, r2, r3)


if __name__ == '__main__':
	world_list, r1, r2, r3 = make_model()
	if debug_new:
		print(len(world_list))
		print(len(r1))
