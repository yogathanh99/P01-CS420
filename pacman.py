#!/usr/local/bin/python3 
from misc import *
from game_map import *

from random import seed
from random import randint

class Pacman:
    def __init__ (self, location, view, map_dimension, food, level):
        self.location = location # a list [x,y], pacman current location
        self.food = food # an int, the total number of food, map provided, when it reach zero, the game ends
        self.food_count = food # this will keep track of how many food pacman has seen
        self.view = view # an interger 5
        self.level = level # game level
        #Pac man has it's own map to calculate and stores the manhattan distance
        self.manhattan_distance = Map(map_dimension[0], map_dimension[1])

        #Pacman personal map since it can't see the whole world
        self.map = Map(map_dimension[0], map_dimension[1])
        self.legal_actions = ["up","down","left","right","still"]        
        
        self.symbol = Symbol()
        self.my_symbol = self.symbol.pacman

        # this will be the goals that pacman will try to reach in order to scan the map
        self.goals_pos = self.generate_goal_possitions_for_map_scanning()
        self.map_scaned = False # this indicate wether if pacman has learn about the whole map

        self.food_pos = [] #this contains the list of food locations that pacman need to reach

        self.previous = [] #this contains pacman previous location, this will help it not to visit back the location when it's possible

        self.hak_map = False #this indicate if pacman has the full view of the map
    def update(self, new_location):
        self.location = copy.deepcopy(new_location)

    def remove_actions(self, direction):        
        try:
            self.legal_actions.remove(direction)
        except ValueError:
            print ("directions not in current legal actions")


    # sense if there is any monster near pacman (manhattan distance <= 2)
    def monster_sense(self, global_map):
        danger_zone = self.calculate_manhattan_distance(global_map)

        monster_location = []
        # now we check if there is any monster in the danger zone
        for i in danger_zone:
            x = i[0]
            y = i[1]

            if (self.symbol.monster in global_map.data[y][x]):
                monster_location.append(i)

        return monster_location


    # removing actions that may lead pacman to the monster 
    def escaping_monster(self, monster_list):
        for i in monster_list:
            if (i[0] < self.location[0]): # don't go left
                self.remove_actions("left")

            if (i[1] > self.location[1]): #don't go down
                try:                    
                    self.remove_actions("down")
                except ValueError:
                    pass

            if (i[1] < self.location[1]): #don't go up
                try:                    
                    self.remove_actions("up")
                except ValueError:
                    pass

            if (i[0] > self.location[0]): # don't go right
                try:                    
                    self.remove_actions("right")
                except ValueError:
                    pass
        
        
    
    # if there's any monster near, prioritize to escape the monster's reach first
    def move(self, global_map):
        # removing the current position form any goals
        self.current_possition_checked()    

        if (self.level < 3 and self.hak_map == False):
            self.hack_map(global_map)

        if (self.level >= 3):
            monster_in_danger_zone = self.monster_sense(global_map)
        
        optimal_moves = self.search_for_best_move()
        move = []
        
        if (len(self.goals_pos) == 0):
            self.generate_new_goals()
        
        # always keep the manhattan distance from the monster at least 2 or more
        # there is some monster near by
        # escaping first while trying to reach the goal
        if (self.level >= 3):
            if len(monster_in_danger_zone) != 0:
                self.escaping_monster(monster_in_danger_zone)
                # after limiting the legal actions, we can move in the most reasonable direction or standing still if there is no options left
            

        # check if the map is fully scaned or pacman has the all the location of the food
        if (self.map_scaned == False or self.food_count > 0):
            self.resolving_wall_goal()
            


        #checking if optimal moves is in legal actions
        for i in optimal_moves:
            if i in self.legal_actions:
                    move.append(i)
            
            # if all optiomal moves is ilegal
        if (len(move) == 0):
            move = copy.deepcopy(self.legal_actions)

            # if there is more than one possible move, random the moves
        
        direction = self.random_move(move)

        print("Pacman move {}".format(direction))
        self.previous = copy.deepcopy(self.location)

        x = self.location[0]
        y = self.location[1]

        if ( direction == "still" ):
            global_map.update(self.location, self.location, self.symbol.pacman)
            return

        if ( direction == "left" ):
            new_x = x - 1
            new_location = [new_x, y]

            global_map.update(self.location, new_location, self.symbol.pacman)
            self.update(new_location)
            
            return

        if ( direction == "right" ):
            new_x = x + 1  
            new_location = [new_x, y]

            global_map.update(self.location, new_location, self.symbol.pacman)
            self.update(new_location)
            return 

        if ( direction == "up" ):
            new_y = y - 1  
            new_location = [x, new_y]

            global_map.update(self.location, new_location, self.symbol.pacman)
            self.update(new_location)
            return

        if ( direction == "down" ):
            new_y = y + 1  
            new_location = [x, new_y]

            global_map.update(self.location, new_location, self.symbol.pacman)
            self.update(new_location)
            return
        

    # with the current view, calculate the manhattan distance of tiles that packman can currently see
    # also return the danger zone
    # this is tell pacman what's there in it's vicinity
    # including foods, wall, monsters
  
    def calculate_manhattan_distance(self,global_map):
        radius = int (self.view/2)
        
        #this contains the coordinate of all the titles that has manhattan distance <=2
        danger_zone = []

        for y in range(self.location[1] - radius, self.location[1] + radius +1 ,1):
            if (y<0 or y >= self.map.height):
                continue
            
            for x in range(self.location[0]-radius, self.location[0] +radius + 1, 1):
                if (x<0 or x >= self.map.width) :
                    continue
                self.manhattan_distance.data[y][x] = manhattandistance(self.location, [x,y])


                self.map.data[y][x] = copy.deepcopy(global_map.data[y][x])
                
                # pacman now remember that it has scan this coordinate                
                if (self.symbol.food in self.map.data[y][x]):
                    if ([x,y] not in self.food_pos):
                        self.food_count = self.food_count - 1
                        self.food_pos.append([x,y])

                    if (self.food_count == 0):
                        self.map_scaned = True


                

                if (manhattandistance(self.location, [x,y]) <= 2):
                    danger_zone.append([x,y])

        return danger_zone
    
    # this is tell pacman what's there in it's vicinity
    # including foods, wall, monsters
  
    def generate_goal_possitions_for_map_scanning(self):
        goals_pos = []
        radius = int(self.view/2)
        x = 0
        y = 0
        while (x < self.map.width):
            x = x + radius
            if (x >= self.map.width):
                break
            y = 0
            while (y < self.map.height):
                y = y + radius
                if ( y >= self.map.height):
                    break
                goals_pos.append([x,y])


        return goals_pos
        

    # Pacman will try to scan the whole map to know where all the food is
    # if there is a wall at pacman goal break every node suronding that and make it goals   
    def resolving_wall_goal(self):
        if (self.hak_map == True):
            return
        for i in self.goals_pos:
            px = i[0]
            py = i[1]

            if (self.symbol.wall in self.map.data[py][px]):
                self.goals_pos.remove(i)
                


    # we will callculate the manhattan distance from the goal node to every node within the view radius
    # pick 2 node that has the smallest distance while they're on the opposite side of each other
    # relatively to the goal node

    # the search function to find all the best move from the given successor
    def search_for_best_move(self):
        nearest = []

        # moving to the nearest food or the nearest goal possition
        if (self.hak_map == True):
            nearest, distance = self.closet_goal(self.food_pos)

        else:
            if (self.map_scaned == False or self.food_count > 0): # Map is not fully scanned
                # removing goals that pacman has already scan
                self.resolving_wall_goal()
                self.removing_goal_pos()
                nearest_goal_pos, distance = self.closet_goal(self.goals_pos)
            else:
                nearest_goal_pos = []

            nearest_food, distance = self.closet_goal(self.food_pos)



            if (len(nearest_food) == 0):
                nearest = copy.deepcopy(nearest_goal_pos)

            else:
                nearest = copy.deepcopy(nearest_food)


        # now looking for possible move to get to the goal
        optimal_moves = []
        if (self.location[0] > nearest[0]): #pacman is currently on the right of it's goal
            optimal_moves.append("left")

        if (self.location[0] < nearest[0]):
            optimal_moves.append("right")

        if (self.location[1] > nearest[1]):
            optimal_moves.append("up")

        if (self.location[1] < nearest[1]):
            optimal_moves.append("down")
        
        return optimal_moves


    # the current location has food
    def eat_food(self):
        self.food = self.food - 1
        # removing the food from the map and the goal


        if (self.food <=0) :
            return self.win_game()                  

        return "NomNom"

    # when pacman has gather all the foods
    def win_game(self):
        dub = "win"
        return dub

    # when the current location has a monster
    def lose_game(self):
        l = "lose"
        return l


    def closet_goal(self, goals): 
        # goals is the list of goals that pacman is trying to reach, either goals_pos or food_pos
        x = self.location[0]
        y = self.location[1]

        minimum = 99999999
        nearest = []
        for l in goals:
            goal_x = l[0]
            goal_y = l[1]
            tmp = manhattandistance([x,y],[goal_x,goal_y])
            if tmp < minimum:
                minimum = tmp
                nearest = copy.deepcopy(l)

        return nearest, minimum

    def random_move(self, move):

        #forcing pacman to move instead of standing still while it's possible
        if (len(move)>1):
            try:
                move.remove("still")
            except:
                pass

        # forcing pacman not to move to revisit the previous location if its possible
        for direction in move:
            x = self.location[0]
            y = self.location[1]
            
            new_location = []

            if ( direction == "left" ):
                new_x = x - 1
                new_location = [new_x, y]

            elif ( direction == "right" ):
                new_x = x + 1  
                new_location = [new_x, y]

            elif ( direction == "up" ):
                new_y = y - 1  
                new_location = [x, new_y]
        
            elif ( direction == "down" ):
                new_y = y + 1  
                new_location = [x, new_y]

            #this will remove the direction that lead pacman back where it just at
            #if pacman currently has only that move, we will try to run different move in the legal actions
            if (self.previous == new_location):
                if (len(move) > 1):
                    move.remove(direction)
                    break

                elif (len(move) == 1):
                    for i in self.legal_actions:
                        if (i == "still"):
                            continue
                        if (i == direction):
                            continue
                        move.append(i)
                        
                        #now check if we can remove the current direction
                    if (len(move) == 1): #this is the only direction that pacman can go eventhough it lead pacman back to the previous place
                        break
                        
                    
                    move.remove(direction) #we can remove the current direction
                    break
                
                    
        value = randint(0,len(move)-1)
        return move[value]


    # this will removing any goal that pacman has already seen 
    def removing_goal_pos(self):


        for i in self.goals_pos:
            x = i[0]
            y = i[1]

            if (self.map.checked[y][x] == 1):
                self.goals_pos.remove(i)

        

    def current_possition_checked(self):
        x = self.location[0]
        y = self.location[1]

        # mark that it has visited this place
        self.map.checked[y][x] = 1

        if (self.map_scaned == False):
            try:
                self.goals_pos.remove([x,y])
            except ValueError:
                pass
        # remove the food from the current goals
        try:
            self.food_pos.remove([x,y])
        except ValueError:
            pass

        # remove the food from the map
        try:
            self.map.remove_food([x,y])
        except:
            pass

    # this function will be called when both goal_pos and food_pos are empty
    def generate_new_goals(self):
        # we will add some goal that has not been checked by pacman
        # we could try adding 4 goal that is the left most, right most, highest, lowest that pacman hasn't visited
        leftmost = [self.map.width,0]
        righmost = [0,0]
        lowest = [0,self.map.height]
        highest = [0,0]

        for i in self.map.checked:
            if i == 0: #not checked yet
                x = i[1]
                y = i[0]

                if (x < leftmost[0]):
                    leftmost[0] = x
                    leftmost[1] = y 
                
                if (x > righmost[0]):
                    righmost[0] = x
                    righmost[1] = y 

                if (y < lowest[1]):
                    lowest[0] = x
                    lowest[1] = y

                if (y > highest[1]):
                    highest[0] = x
                    highest[1] = y

        l = [leftmost, righmost, lowest, highest]
        unique = unique_sort_list(l) # removing duplicated goals
        self.goals_pos = copy.deepcopy(unique)
        return                 

    # this function to tell pacman that it has the full view of the map
    def hack_map(self, global_map):
        self.hak_map = True
        #self.map = copy.deepcopy(global_map)
        self.map=global_map
        self.map_scaned = True

        for x in range(self.map.width):
            for y in range(self.map.height):
                if (self.symbol.food in self.map.data[y][x]):
                    self.food_pos.append([x,y]) 