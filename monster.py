#!/usr/local/bin/python3.7
from misc import *
from random import seed
from random import randint
from game_map import *

import copy

class Monster:
    def __init__ (self, location, view, map_dimension, level):

        self.location = location # a list [x,y], pacman current location
        self.view = view # an interger 5

        self.legal_actions = ["up","down","left","right","still"]        

        self.symbol = Symbol()
        self.my_symbol = self.symbol.monster

        self.map = Map(map_dimension[0], map_dimension[1])

        self.level = level
        self.smart = False

    def remove_actions(self, direction):        
        try:
            self.legal_actions.remove(direction)
        except ValueError:
            print ("directions not in current legal actions")


    def move(self,global_map):
        optimal_moves = []
        move = []

        if (self.level < 3):
            global_map.update(self.location, self.location, self.my_symbol)
            return
        

        if (self.level == 4):
            optimal_moves = copy.deepcopy(self.hunt_pacman(global_map))

        #checking if optimal moves is in legal actions
        for i in optimal_moves:
            if i in self.legal_actions:
                    move.append(i)
            
            # if all optiomal moves is ilegal
        if (len(move) == 0):
            move = copy.deepcopy(self.legal_actions)

        direction = self.random_move(move)
        print("Monster moving ...")

        x = self.location[0]
        y = self.location[1]

        if ( direction == "still" ):
            global_map.update(self.location, self.location, self.my_symbol)
            return

        if ( direction == "left" ):
            new_x = x - 1
            new_location = [new_x, y]

            global_map.update(self.location, new_location, self.my_symbol)
            self.update(new_location)
            
            return

        if ( direction == "right" ):
            new_x = x + 1  
            new_location = [new_x, y]

            global_map.update(self.location, new_location, self.my_symbol)
            self.update(new_location)
            return 

        if ( direction == "up" ):
            new_y = y - 1  
            new_location = [x, new_y]

            global_map.update(self.location, new_location, self.my_symbol)
            self.update(new_location)
            return

        if ( direction == "down" ):
            new_y = y + 1  
            new_location = [x, new_y]

            global_map.update(self.location, new_location, self.my_symbol)
            self.update(new_location)
            return
        
     
    def random_move(self, move):
        #if there is just one possible move
        if (len(move) == 1):
            return move[0]

        #forcing to move instead of standing still while it's possible
        try:
            self.remove_actions("still")
        except:
            pass

        value = randint(0,len(move)-1)
        return move[value]

    def update(self, new_location):
        self.location = copy.deepcopy(new_location)

    #this function will let the monster chassing pacman 
    def hunt_pacman(self,global_map):
        pacman_location = copy.deepcopy(self.scan_pacman(global_map))

        # pacman is not currently in the view of the monster        
        if (len(pacman_location) == 0):
            return []

        x = pacman_location[0]
        y = pacman_location[1]

        optimal_moves = []

        if (self.location[0] > pacman_location[0]):
            optimal_moves.append("left")

        if (self.location[0] < pacman_location[0]):
            optimal_moves.append("right")

        if (self.location[1] > pacman_location[1]):
            optimal_moves.append("up")

        if (self.location[1] < pacman_location[1]):
            optimal_moves.append("down")

        return optimal_moves

    # this use to scan if pacman is near the monster
    # if so, monster will get the location of pacman and then try to move to wards pacman
    def scan_pacman(self,global_map):
        radius = int (self.view/2)
        
        #this contains the coordinate of all the titles that has manhattan distance <=2

        for y in range(self.location[1] - radius, self.location[1] + radius +1 ,1):
            if (y<0 or y >= self.map.height):
                continue
            
            for x in range(self.location[0]-radius, self.location[0] +radius + 1, 1):
                if (x<0 or x >= self.map.width) :
                    continue
                
                if (self.symbol.pacman in global_map.data[y][x]):
                    return [x,y]


        return []