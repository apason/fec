#!/usr/bin/python2
# Arttu Kilpinen, 014013070

import sys
from socket import socket, AF_INET, SOCK_DGRAM
from numpy import frombuffer, bitwise_xor, byte

# Packet size and header size must be the same as clients
MAX_SEQ_SIZE = 9
HEADER_SIZE  = MAX_SEQ_SIZE + 1
PACKET_SIZE  = 100 + HEADER_SIZE

complete     = 0    # Number of packets from complete three-set (excludes xor packet)
partial      = 0    # Number of packets and corrected packets from partial set
single       = 0    # Single packets (xor packets not included)

data         = []   # Array of UDP packets read

p            = 0    # Index of the first packet not yet analyzed ( p is for pointer)

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " <outputFile>")
    exit(-1)
    
output_file = open(sys.argv[1], "wb")

# Open socket and bind to port
socket = socket(AF_INET, SOCK_DGRAM)
socket.bind(('', 3333))


###############################
# Helper function definitions #
###############################

# Print error message and exit the program
def fatalError(message):
    print("FATAL ERROR: " + message)
    exit(-1)
    
# Returns sequence number of given packet
def getSeq(packet):
    seq_field = packet[1:HEADER_SIZE]
    
    for i in range(MAX_SEQ_SIZE):
        if seq_field[i] != '\0':
            return int(seq_field[i:])

    fatalError("No sequence number found")

# Returns the index number of the packet ('1', '2', 'x' or 'q')
def getIndex(packet):
    return packet[0]

# Returns the data part of the packet (packet without the header)
def getMessage(packet):
    return packet[HEADER_SIZE:]

#Xor two data blocks
def sXor(aa, bb):
    if len(aa) > len(bb):
        for i in range(len(aa) - len(bb)):
            bb = bb + '\0'

    a = frombuffer(aa, dtype = byte)
    b = frombuffer(bb, dtype = byte)
    
    return bitwise_xor(a, b).tostring()


#################
# Program start #
#################

# Read from socket until packet with end header is recieved
while True:
    data.append(socket.recv(PACKET_SIZE))

    if data[len(data) - 1][0] == 'q':
        break

# Analyze received data
while p < len(data):

    seq = getSeq(data[p])
    j   = 1                # amount of packets in the set (max 3)

    # Scan packets with same seq number (1-3 packets)
    while True:

        if p + j >= len(data):
            p = p + j
            break

        seq_comp = getSeq(data[p + j])
        
        if(seq_comp != seq):
            p = p + j
            break
        else:
            j = j + 1
            
    # create a list of packets with same seq
    packet = []
    for i in range(j):
        packet.append(data[p - j + i])

    # Complete set (a, b, a XOR b) found
    if len(packet) == 3:
        complete = complete + 2
        output_file.write(getMessage(packet[0]) + getMessage(packet[1]))

    # Incomplete set, correction may be needed
    if(len(packet)) == 2:
       partial = partial + 2

       seq1  = getIndex(packet[0])
       data1 = getMessage(packet[0])
       seq2  = getIndex(packet[1])
       data2 = getMessage(packet[1])

       if seq2 == 'x' or seq2 == 'q':
           if seq1 == '1':
               output_file.write(data1)
               output_file.write(sXor(data1,data2))
           else:
               output_file.write(sXor(data1, data2))
               output_file.write(data1)
       else:
           output_file.write(data1+data2)
           
    # Incomplete set, xorred packets are discarded
    if len(packet) == 1 and getIndex(packet[0]) != 'x' and getIndex(packet[0]) != 'q':
       single = single + 1
       output_file.write(packet[0])

# Print statistics
recieved = complete + single + partial
total    = getSeq(data[len(data)-1]) * 2
lost     = total - recieved

print("Data from complete packets: " + str(complete))
print("Data from Partial packets (possibly recovered): " + str(partial))
print("Data from single packets: " + str(single))
print("")
print("Total (possibly recovered) data packets recieved " + str(recieved))
print("Total data packets the client sent: " + str(total))
print("Data packets lost: " + str(lost))
print("")
print("Loss rate: " + str(float(lost)/total))

# Close socket and file
socket.close()
output_file.close()

    
