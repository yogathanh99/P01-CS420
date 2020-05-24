#!/usr/local/bin/python3.7

from pacman import *
from monster import *
from game_map import*
from misc import *
from settings import *

import sys,getopt
import pygame
import copy

pygame.init()


symbol = Symbol()

def get_legal_actions(agent, Map, game_level):
    #Don't let the agent move out side the map or to go through wall
    x = agent.location[0]
    y = agent.location[1]

    #reset the legal actions before striping the illegal
    agent.legal_actions = ["up","left","down","right","still"]
    if (x > 0):
        if (symbol.wall in Map.data[y][x-1]):
            agent.remove_actions("left")

        if (game_level < 3):
            if (symbol.monster in Map.data[y][x-1]):
                agent.remove_actions("left")
    else:
        agent.remove_actions("left")

    if (x < Map.width -1):
        if (symbol.wall in Map.data[y][x+1]):
            agent.remove_actions("right")

        if (game_level < 3):
            if (symbol.monster in Map.data[y][x+1]):
                agent.remove_actions("right")

    else:
        agent.remove_actions("right")

    if (y > 0):
        if (symbol.wall in Map.data[y-1][x]):
            agent.remove_actions("up")

        if (game_level < 3):
            if (symbol.monster in Map.data[y-1][x]):
                agent.remove_actions("up")

    else:
        agent.remove_actions("up")

    if (y < Map.height - 1):
        if (symbol.wall in Map.data[y+1][x]):
            agent.remove_actions("down")

        if (game_level < 3):
            if (symbol.monster in Map.data[y+1][x]):
                agent.remove_actions("down")

    else:
            agent.remove_actions("down")

def text(words, screen, position, size, color, fontName):
    font = pygame.font.SysFont(fontName, size)
    text = font.render(words, False, color)
    text_size = text.get_size()
    screen.blit(text, position)
    pygame.display.update()
    pygame.time.delay(500)

# tell pacman to eat the food
# this also check if pacman has already ate all the food, therefore the game can end
def state_check(pacman, global_map,screen):
    x = pacman.location[0]
    y = pacman.location[1]

    # there is food at pacman's current location
    if symbol.food in global_map.data[y][x]:
        result = pacman.eat_food()
        global_map.remove_food([x,y])
        if result == "win":
            # text('WIN', screen, [WIDTH//2, 180], 52,
            #                        GREEN, FONT)
            # print ("Pacman win the game!")
            return "WIN"
    
    # there is a monster at pacman's current location
    if (symbol.monster in global_map.data[y][x]):
        print("Pacman die")
        return "DIE"

    return False

def set_level(level):
    game_level = level


def main(argv):
    # set map level
    game_level = 1
    wall = '1'

    try:
      opts, args = getopt.getopt(argv,"hm:l:",["ifile=","ofile="])
    except getopt.GetoptError:
      print ('test.py -m <Map> -l <Level>')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
        print ('test.py -m <Map> -l <Level>')
        sys.exit()
      elif opt in ("-m", "--ifile"):
         wall = arg
      elif opt in ("-l", "--ofile"):
         game_level = int(arg)

    #generate maps
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    mapSize=[]
    wallFile = "walls_" + wall + ".txt"

    agents=[]
    walls = []
    foods = []
    enemies = []

    wallsPos=[]
    foodsPos=[]
    playerPos = None
    enemyPos = []

    
    with open(wallFile, 'r',) as file:
            for y, line in enumerate(file):
                if y==0:
                    for index in range(0, len(line)-1):
                        if line[index]=="x":
                            mapSize.append(int(line[:index]))
                            mapSize.append(int(line[index+1:]))
                else:
                    for x, str in enumerate(line):
                        # WALLS
                        if str == "1":
                            wallsPos.append([x,y-1])
                        # COINS
                        elif str == ".":
                            foodsPos.append([x,y-1])
                        # PLAYER
                        elif str == "p":
                            playerPos = [x, y-1]

                        if game_level!=1:
                            # ENEMY
                            if str in "m":
                                enemyPos.append([x, y-1])
                        
    #generate agents location
    

    # define a 8 X 8 map
    global_map = Map(mapSize[0], mapSize[1]+abs(mapSize[0]-mapSize[1]))

    food_pos = foodsPos
    food_number = len(food_pos)

    wall_pos = wallsPos

    map_dimension = global_map.map_dimension()

    # initialize pacman and monster locations
    
    pman = Pacman(playerPos,5,map_dimension,food_number,game_level)
    agents.append(pman)
    for enemy in enemyPos:
        monster=Monster(enemy,5,map_dimension,game_level)
        agents.append(monster)

    
    # add agents into the map
    global_map.load_agents(agents)
    # add food into the map
    global_map.load_food(food_pos)
    
    # add wall into the map
    global_map.load_wall(wall_pos)
    global_map.map_print()

    state_check(pman, global_map,screen)

    i = 100000 # a variable just to make the loop stop, removing later

    finish = False

    while (True):
        for a in agents:
            get_legal_actions(a,global_map,game_level)
            # agent moves and global map update it's location
            a.move(global_map)
            
    
        finish = state_check(pman, global_map,screen)
        global_map.map_print()

        if finish=="WIN":
            text('WIN', screen, [WIDTH//2, 180], 52,
                                   GREEN, FONT)
            print ("Pacman win the game!")
            print ("The game finish in {} steps".format(100000 - i))
            break
        elif finish=="DIE":
            text('DIE', screen, [WIDTH//2, 180], 52,
                                   GREEN, FONT)
            print ("The game finish in {} steps".format(100000 - i))
            print("Pacman die")
            break


        i = i - 1
        if (i <= 0):
            print("Preemptive to end the game")
            break

    pygame.quit()
    sys.exit()
    print ("The game finish at level {}".format(game_level))
if __name__ == "__main__":
    main(sys.argv[1:]) 