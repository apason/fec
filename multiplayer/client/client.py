#!/usr/bin/env python3

import socket, fileinput, time, sys, ast, _thread, os

sys.path.append(os.path.realpath("../"))
from common import *
                

HOST = '127.0.0.1'     # The server's hostname or IP address
PORT = 3333            # The port used by the server
MESSAGE_SIZE = 1024    # Maximum message size
local_player = ('',0)  # Identification of the local player

# Create and return a string list of the resources
def parseList(resources):
    return decode(resources).split("\0")

# Get one resource from the server
def getResource(control_connection, name):

    eprint("Request a file from server: " + name)
    
    # Send the gett command for given resource
    control_connection.sendall(encode("gett " + name))
    eprint("Sent: gett + name")
    
    # Save the connection information
    file_port = control_connection.recv(MESSAGE_SIZE)
    eprint("Recv: " + repr(decode(file_port))

    # Create a new connection and download the file
    #eprint("Creating a new TCP connection with " + repr((HOST, int(decode(file_port)))))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as fs:
        fs.connect((HOST, int(decode(file_port))))

        resource_file = open(name, 'wb')
        eprint("Receiving data from the socket...")
        while True:
            data = fs.recv(MESSAGE_SIZE)
            if not data:
                break
            resource_file.write(data)

        eprint("Done! Closing the connection")
        fs.close()

# Return the position of the local player
def getLocalPosition():
    return getUserById(state, local_player)[1]

# Print the state of the game in human readable format
def printState():
    dimensions = game_map[0]
    position = getLocalPosition()

    # Loop all coordinates of the game map
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):

            # Get user from coordinates (may be None)
            entry = getUserByCoordinates(state,i,j)

            # Check for walls
            if isWall(game_map,i, j):
                sys.stdout.write("#")

            # Check for current user
            elif (position[0],position[1]) == (i,j):
                if position[2] == 1:
                    sys.stdout.write("\033[92m▴\033[0m")
                elif position[2] == 2:
                    sys.stdout.write("\033[92m▾\033[0m")
                elif position[2] == 3:
                    sys.stdout.write("\033[92m◂\033[0m")
                elif position[2] == 4:
                    sys.stdout.write("\033[92m▸\033[0m")
                else:
                    sys.stdout.write("\033[92mo\033[0m")

            # Check for other players
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
                    
            # Print empty space if the spot is not occupied
            else:
                sys.stdout.write(" ")
        print("")

# Thread that listens the server and changes the game state accordingly
def listenServer(game_socket, state):

    eprint("Starting a new thread.")
    eprint("Listening the server")

    while True:

        data = ast.literal_eval(decode(game_socket.recv(MESSAGE_SIZE)))
        print("recv: " + repr(data))

        if isinstance(data, tuple):
            user = data[0]
            command = data[1]

            if command == "u":
                turnUp(state, user)
            elif command == "d":
                turnDown(state, user)
            elif command == "l":
                turnLeft(state, user)
            elif command == "r":
                turnRight(state, user)
            elif command == "f":
                moveForward(state, game_map, user)
            elif command == "c":
                addPlayer(state, game_map, user)

        # Server sends its state
        elif isinstance(data, list):
            print("data type: list")
            state.clear()
            state.extend(data)

        printState()



# Program starts by creating control connection with the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        query = input()
        if query == "quit":
            s.close()
            exit(0)

        # Send data and save the response
        s.sendall(encode(query))
        eprint("sent: " + repr(query))
        data = s.recv(MESSAGE_SIZE)
        eprint("recv: " + repr(decode(data)))

        # Resource files asked
        if query == "list":
            resources = parseList(data)
            eprint("needed resources: " + repr(resources))

            # Parse and get all needed resources
            for resource in resources:
            getResource(s, resource)
                
        elif query == "join":
            dest = (HOST, int(decode(data)))
            eprint("Creating a new UDP connection to " + repr(dest))
            game_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            game_socket.sendto(encode("s"), dest)
            eprint("sent: 's'")

            #initialize game state
            with open('map.py', 'r') as f:
                game_map = ast.literal_eval(f.read())

            recv = decode(game_socket.recv(MESSAGE_SIZE))
            eprint("Recv: " + repr(recv))
            state = ast.literal_eval(recv)

            _thread.start_new_thread(listenServer, (game_socket,state))

            while True:
                printState()
                command = input()
                game_socket.sendto(encode(command), dest)
                eprint("Sent: " + repr(command))
                
                if command == "d":
                    turnDown(state, local_player)
                elif command == "u":
                    turnUp(state, local_player)
                elif command == "l":
                    turnLeft(state, local_player)
                elif command == "r":
                    turnRight(state, local_player)
                elif command == "f":
                    moveForward(state, game_map, local_player)
                elif command == "q":
                    break

            game_socket.close()
                    
        else:
            print("Recv: ", repr(decode(data)))


            
