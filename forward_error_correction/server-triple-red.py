#!/bin/env python2.7
# Arttu Kilpinen, 014013070

import sys
from socket import socket, AF_INET, SOCK_DGRAM

                                     # End Of Transmission is set on if the first
EOT_SIZE    = 1                      # byte of the packet contains 'q' (ascii)
MAX_SEQ     = 9                      # Bytes for sequence field (ascii coded decimals)
HEADER_SIZE = EOT_SIZE + MAX_SEQ     # Contains EOT byte and the sequence field
PACKET_SIZE = 100 + HEADER_SIZE      # Packet contains header and user message

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " <outputFile>")
    exit(-1)
    
output_file = open(sys.argv[1], "wb")

# Open socket and bind to port
socket = socket(AF_INET, SOCK_DGRAM)
socket.bind(('', 3333))

# sets of 0/1/2/3 missing packets
triples = 0
doubles = 0
singles = 0

# print error message and exit the program
def fatalError(message):
    print("FATAL ERROR: " + message)
    exit(-1)


# Returns True if the EOT is set in the given packet
# False otherwise
def isLastPacket(data):
    return data[0] == 'q'

# Returns the data part of the packet (packet without the header)
def getMessage(packet):
    return packet[HEADER_SIZE:]

# Returns sequence number of given packet
def getSeq(data):
    seq_field = data[1:HEADER_SIZE]
    for i in range(MAX_SEQ):
        if seq_field[i] != '\0':
            return int(seq_field[i:])

    fatalError("No sequence number found")


# Print information of read data sets and lossrate
def printStatistics(last_seq):
    lost = last_seq - triples - doubles - singles + 1 # First seq is 0 thus we add +1
    
    print("Triplets: " + str(triples))
    print("Doubles:  " + str(doubles))
    print("Singles:  " + str(singles))
    print("Lost:     " + str(lost))
    print("")
    print("Total packets received: " + str(3 * triples + 2 * doubles + singles))
    print("Total different packets received: " + str(triples + doubles + singles))
    print("")
    print("Loss rate: " + str(float(lost)/(last_seq + 1)))


# Main function of the server
# Receives data and handles one set at a time
def TripleRedundancyReceive(socket):

    global triples
    global doubles
    global singles

    global data

    i = 1

    data_c = data
    while not isLastPacket(data_c):
        data_c = socket.recv(PACKET_SIZE)

        if getSeq(data) == getSeq(data_c):
            i = i + 1
        else:
            if isLastPacket(data_c):                   # If data_c here is the last packet +1 must be added 
                singles = singles + 1                  # to singles and file write must be done because there 
                output_file.write(getMessage(data))    # is no further calls to this function.
            break

    if   i == 3:
        triples = triples + 1
    elif i == 2:
        doubles = doubles + 1
    elif i == 1:
        singles = singles + 1


    output_file.write(getMessage(data))
    data = data_c

# Start receiving
data = socket.recv(PACKET_SIZE)

# Receive and handle data until the end of transmission
while not isLastPacket(data):
    TripleRedundancyReceive(socket)

# Close socket and output file
socket.close()
output_file.close()
    
# Print statistics of the transmission
printStatistics(getSeq(data))
