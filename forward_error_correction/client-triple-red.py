#!/bin/env python2.7
# Arttu Kilpinen, 014013070

import fileinput, sys, random
from socket import socket, AF_INET, SOCK_DGRAM

MAX_SEQ_SIZE = 9
PACKET_SIZE = 100
port = 3333

if len(sys.argv) != 3:
    print("Usage: " + sys.argv[0] + " <inputFile> <lossRate>")
    sys.exit(-1)

# Read command line arguments
input_file = sys.argv[1]
loss_rate = float(sys.argv[2])

# Open socket and input file
socket = socket(AF_INET, SOCK_DGRAM)
input_data = open(input_file, 'rb')

seq  = 0                   # Current sequence number to be added to the packet header
dest = ('localhost', port) # Destination to send


###############################
# Helper function definitions #
###############################

# Print error message and exit the program
def fatalError(message):
    print("FATAL ERROR: " + message)
    exit(-1)


# Sends given data three times, injects loss
def TripleRedundancySend(data, socket, destination, lossrate, is_last):
    
    for i in range(3):

        # The last packet is allways sent
        if i == 2 and is_last:
            socket.sendto('q' + data, destination)
            break

        # Inject loss and send
        if random.random() > lossrate:
            socket.sendto(str(i + 1) + data, destination)
        
# Returns true if the given file is is read to its end
# False otherwise
def endOfFile(file):

    # Save current position
    current = file.tell()

    # Seek to the end of file and save position
    file.seek(0,2)
    end = file.tell()

    # Seek back to the previous position
    file.seek(current)

    if current == end:
        return True

    return False

# Adds the current sequence number to the packet
def addSeq(data, seq):
    global MAX_SEQ_SIZE

    if seq >= pow(10, MAX_SEQ_SIZE) - 1:
        fatalError("Sequence number owerflow")
        
    data = str(seq) + data
    
    for i in range(MAX_SEQ_SIZE - len(str(seq))):
        data = '\0' + data

    return data


#################
# Program start #
#################

# Read from inputfile and send
while not endOfFile(input_data):
    
    data = input_data.read(PACKET_SIZE)

    TripleRedundancySend(addSeq(data, seq), socket, dest, loss_rate, endOfFile(input_data))
    seq = seq + 1        

# Close socket and input file
socket.close()
input_data.close()

print("Data sent succesfulle")




