## Arttu Kilpinen
## 014013070

# This file contains the methods needed by clients and the server

from __future__ import print_function
import sys

# Define eprint for printing to stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Methods for encoding and decoding bytes<->string
def encode(string):
    return bytes(string, 'utf-8')

def decode(data):
    return data.decode('utf-8')

# Return single player information for given coodrinates. False if its not occupied.
def getUserByCoordinates(state,x,y):
    for entry in state:
        reserved = (entry[1][0], entry[1][1])
        if reserved == (x,y):
            return entry

    return None


# Finds the user defined by its address
def getUserById(state, addr):
    for entry in state:
        if entry[0] == addr:
            return entry

    return None

# Returns True if given coordinate is wall. False otherwise.
def isWall(game_map, x, y):
    dimensions = game_map[0]

    if x == 0 or x == dimensions[0]-1 or y == 0 or y == dimensions[1]-1:
        return True

    if (x,y) in game_map:
        return True

    return False


# Turns user defined by addr to down
def turnDown(state, addr):
    user = getUserById(state, addr)
    modified_user = (user[0],(user[1][0],user[1][1],2))

    print(repr(user))
    print(repr(modified_user))
    
    state.remove(user)
    state.append(modified_user)

# Turns user defined by addr to up
def turnUp(state, addr):
    user = getUserById(state, addr)
    modified_user = (user[0],(user[1][0],user[1][1],1))

    print(repr(user))
    print(repr(modified_user))
    
    state.remove(user)
    state.append(modified_user)

# Turns user defined by addr to left
def turnLeft(state, addr):
    user = getUserById(state, addr)
    modified_user = (user[0],(user[1][0],user[1][1],3))

    print(repr(user))
    print(repr(modified_user))
    
    state.remove(user)
    state.append(modified_user)

# Turns user defined by addr to right
def turnRight(state, addr):
    user = getUserById(state, addr)
    modified_user = (user[0],(user[1][0],user[1][1],4))

    print(repr(user))
    print(repr(modified_user))
    
    state.remove(user)
    state.append(modified_user)

# Move the user identified by id to forward
# Ignore illegal movement
def moveForward(state, game_map, addr):
    
    user = getUserById(state, addr)
    modified_user = None
    direction = user[1][2]
    respawn_flag = False
    other_player = False

    print("moveForward")

    if direction == 1 and isWall(game_map, user[1][0]-1,user[1][1]) != True:     # Ignore movement to wall
        other_player = getUserByCoordinates(state, user[1][0]-1,user[1][1])
        if other_player == None or other_player[1][2] != 2:                      # Ignore movement to head of other
            modified_user = (user[0],(user[1][0]-1,user[1][1],direction))        # Calculate the movement
            if other_player != None:                                             # Set respawn flag in case the other
                respawn_flag = True                                              # player is defeated
            
    elif direction == 2 and isWall(game_map, user[1][0]+1,user[1][1]) != True:
        print("direction = 2")
        other_player = getUserByCoordinates(state, user[1][0]+1,user[1][1])
        if other_player == None or other_player[1][2] != 1:
            print("other player: none")
            modified_user = (user[0],(user[1][0]+1,user[1][1],direction))
            print(repr(user))
            print(repr(modified_user))
            if other_player != None:
                respawn_flag = True
                                   
    elif direction == 3 and isWall(game_map, user[1][0],user[1][1]-1) != True:
        other_player = getUserByCoordinates(state, user[1][0],user[1][1]-1)
        if other_player == None or other_player[1][2] != 4:
            modified_user = (user[0],(user[1][0],user[1][1]-1,direction))
            if other_player != None:
                respawn_flag = True
    elif direction == 4 and isWall(game_map, user[1][0],user[1][1]+1) != True:
        other_player = getUserByCoordinates(state, user[1][0],user[1][1]+1)
        if other_player == None or other_player[1][2] != 3:
            modified_user = (user[0],(user[1][0],user[1][1]+1,direction))
            if other_player != None:
                respawn_flag = True

    # Replace user state with its new state
    if modified_user != None:
        state.remove(user)
        state.append(modified_user)

    if respawn_flag == True:
        reSpawn(state, game_map, other_player)

# Return first empty position from upper left corner of the map        
def getEmptyPosition(state, game_map):
    dimensions = game_map[0]
    
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            if i == 0 or i == 9 or j == 0 or j == 9:
                continue
            if (i,j) in game_map:
                continue
            if getUserByCoordinates(state,i,j) != None:
                continue

            return (i,j, 1)
        
# Respawn defeated player        
def reSpawn(state, game_map, user):
    state.remove(user)
    addPlayer(state, game_map, user[0])

# Add player to the map
def addPlayer(state, game_map, addr):
    pos = getEmptyPosition(state, game_map)
    state.append((addr, pos))

