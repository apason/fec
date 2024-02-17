#!/usr/bin/env python3

import sys, ast

# # x, y
#game_map = [(10,10),(4,5),(4,6),(5,5),(5,6)];

with open('map.py', 'r') as f:
    game_map = ast.literal_eval(f.read())

dimensions = game_map[0]

for i in range(dimensions[0]):
    for j in range(dimensions[1]):
        if i == 0 or i == 9 or j == 0 or j == 9:
            sys.stdout.write("#")
        elif (i,j) in game_map:
            sys.stdout.write("#")
        else:
            sys.stdout.write(" ")
    print("")

print(repr(game_map))

