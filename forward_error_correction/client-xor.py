#!/usr/bin/python2
# Arttu Kilpinen, 014013070

import fileinput, sys, random, time

from socket import socket, AF_INET, SOCK_DGRAM
from numpy import frombuffer,bitwise_xor,byte

MAX_SEQ_SIZE = 9
PACKET_SIZE  = 100
HEADER_SIZE  = MAX_SEQ_SIZE + 1
PORT         = 3333
iteration    = 0

if len(sys.argv) != 3:
    print("Usage: " + sys.argv[0] + " <inputFile> <lossRate>")
    exit(-1)

# Read command line parameters
input_file = sys.argv[1]
loss_rate  = float(sys.argv[2])

# Open socket and input file
socket     = socket(AF_INET, SOCK_DGRAM)
input_data = open(input_file, "rb")

# Define destination
dest = ('localhost', PORT)


###############################
# Helper function definitions #
###############################

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

# Truncate (enlarge) data to given length
# Pad with zeros, add packet index number
def truncate(data, length):
    global iteration

    data_size = len(data)
    data      = str(iteration) + data
    
    while len(data) < data_size + length:
        data  = '\0' + data
        
    return data

# Xor two data blocks and return the result
def sXor(aa, bb):
    a = frombuffer(aa, dtype = byte)
    b = frombuffer(bb, dtype = byte)

    return bitwise_xor(a, b).tostring()

# Create XOR checksum and send packet, inject loss
def xorSend(data1, data2, socket, destination, lossrate, is_last):

    global iteration
    header_size = 10

    if len(data1) > len(data2):
        for i in range(len(data1) - len(data2)):
            data2 = data2 + '\0'

    
    iteration = iteration + 1 #use as packet index number

    # Add packet index number and truncate
    data1 = '1' + truncate(data1, MAX_SEQ_SIZE)
    data2 = '2' + truncate(data2, MAX_SEQ_SIZE)

    if(is_last):
        data3 = "q"
    else:
        data3 = "x"
        
    data3 = data3 + truncate(sXor(data1, data2), MAX_SEQ_SIZE)

    # Inject loss, count sent packets and send
    if random.random() > lossrate:
        socket.sendto(data1, destination)

    if random.random() > lossrate:
        socket.sendto(data2, destination)

    if random.random() > lossrate or is_last:
        socket.sendto(data3, destination)


#################
# Program start #
#################

# Read from inputfile and send
while True:
    data1   = input_data.read(PACKET_SIZE)
    is_last = endOfFile(input_data)

    #Odd amount of data, send last packet of whitespaces
    if len(data1) < PACKET_SIZE:
        xorSend(data1, '\0' , socket, dest, loss_rate, is_last)
        break

    data2   = input_data.read(PACKET_SIZE)
    is_last = endOfFile(input_data)

    xorSend(data1, data2, socket, dest, loss_rate, is_last)

    if is_last:
        break

print("Data sent succesfully")

socket.close()
input_data.close()




