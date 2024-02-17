#!/usr/bin/env python3

# Arttu Kilpinen
# 014013070


import _thread, ast, os, socket, sys, time

# Import common functions
sys.path.append(os.path.realpath("../"))
from common import *
# Define the state 

STATE_SEND_INTERVAL = 3
files = "map.py\0textures123"
state = []

# Thread for handling a single file transmission
def file_thread(control_connection, filename):

    # Socket for single file transmission
    file_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    file_socket.bind(('', 0))
    port = file_socket.getsockname()[1]

    # Send port to client
    control_connection.sendall(encode(str(port)))

    file_socket.listen()
    file_connection, file_address = file_socket.accept()

    # Open and send the required file
    resource_file = open(filename, 'rb')
    file_connection.sendfile(resource_file)
    file_connection.shutdown(socket.SHUT_WR)
    file_connection.close()
    
# Returns the command part of the message
def getCommand(data):
    return decode(data).split(" ")[0]

# Return the param part of the message
def getParam(data):
    return decode(data).split(" ")[1]

# Sends the state of the game to the given ID
def sendState(socket, addr):

    # Copy the state
    state_copy = state.copy()

    # Create user entry as seen in the client
    user_state = (('',0),getUserById(state_copy, addr)[1])

    # Replace the user state (seen by server) by the state seen by client
    state_copy.remove(getUserById(state_copy, addr))
    state_copy.append(user_state)

    # Send the state
    socket.sendto((encode(repr(state_copy))), addr)

# Check if the (calling) player is already in the state
def containsPlayer(addr):
    for entry in state:
        if entry[0] == addr:
            return True
        
    return False

# Print the state of the game in human readable forman
def printState():
    dimensions = game_map[0]

    # Loop over the game map
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):

            # Get user from coordinates (May be None)
            entry = getUserByCoordinates(state,i, j)

            # Check for wall
            if isWall(game_map,i, j):
                sys.stdout.write("#")

            # Check for players
            elif entry != None:
                if entry[1][2] == 1:
                    sys.stdout.write("▴")
                elif entry[1][2] == 2:
                    sys.stdout.write("▾")
                elif entry[1][2] == 3:
                    sys.stdout.write("◂")
                elif entry[1][2] == 4:
                    sys.stdout.write("▸")
                else:
                    sys.stdout.write("o")
                    
            # Print whitespace if the spot is empty
            else:
                sys.stdout.write(" ")
        print("")

# Forward the action from one player to others
def forwardAction(control, issuer_address):

    # Create a list of other players except the issuer
    issuer = getUserById(state, issuer_address)
    others = state.copy()
    others.remove(issuer)

    # Open new socket to send data 
    forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Loop over the other players and send the action
    for user in others:
        print("Sending: (" + repr(issuer_address) + "," + control + ") to " + repr(user[0]))
        forward_socket.sendto(encode(repr((issuer_address, control))), user[0])

    forward_socket.close()

# Thread for a single player interact with
def gamePlay(control_connection):

    # Open a new UDP socket for a new player
    game_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_socket.bind(('', 0))

    # Send the port of the newly created socket to the player
    port = game_socket.getsockname()[1]
    control_connection.sendall(encode(str(port)))
    time.sleep(1)
    
    #control_socket.shutdown(socket.SHUT_WR)
    #control_socket.close()

    # Receive and decode data
    data, addr = game_socket.recvfrom(1)
    data = decode(data)

    print("message from client: " + repr(data))

    # Start a timer thread for state transmissions
    _thread.start_new_thread(timerThread, (game_socket,addr))

    # Game play main loop
    while True:

        # A new player requests the game state
        if data == "s":

            # Add player to the game if its not already joined
            if containsPlayer(addr) == False:
                addPlayer(state, game_map, addr)
                forwardAction("c", addr)
                sendState(game_socket, addr)
                
            # Only initial state request is supported
            else:
                print("player requests state")

        print("command from user: " + data)

        # handle possible commands
        if data == "d":
            turnDown(state, addr)
            forwardAction(data, addr)
        elif data == "u":
            turnUp(state, addr)
            forwardAction(data, addr)
        elif data == "l":
            turnLeft(state, addr)
            forwardAction(data, addr)
        elif data == "r":
            turnRight(state, addr)
            forwardAction(data, addr)
        elif data == "f":
            moveForward(state, game_map, addr)
            forwardAction(data, addr)

        # Print the (modified) game state and continue to listen
        printState()
        data, addr = game_socket.recvfrom(1)
        data = decode(data)

        
# Control connections is handled here
# One thread per client
def clientThread(conn):

    while True:

        # Receive data
        data = conn.recv(1024)
        if not data:
            break

        # Return the names of the resource files
        if getCommand(data) == "list":
            conn.sendall(encode(files))

        # Spawn a new thread for a single file transfer
        elif getCommand(data) == "gett":
            print(decode(data))
            _thread.start_new_thread(file_thread, (conn, getParam(data)))

        # Spawn a new thread for a game play
        elif getCommand(data) == "join":
            _thread.start_new_thread(gamePlay, (conn,))

        # Inform the client of an unsupported command
        else:
            conn.sendall(encode("Unsupported command: ") + data)

            
def timerThread(game_socket, addr):

    while True:
        time.sleep(STATE_SEND_INTERVAL)
        sendState(game_socket, addr)

###################
## Program start ##
###################        
            
# Read the game map from a file
with open('map.py', 'r') as f:
    game_map = ast.literal_eval(f.read())

# Open socket and listen for connections
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('', 3333))
    s.listen(1)

    while True:
        conn, addr = s.accept()

        # Start a control connection with a client
        _thread.start_new_thread(clientThread, (conn,))

    s.close()

