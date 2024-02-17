#!/usr/bin/env python3

import time

start_timer = input('Do you want to start the timer? Y / N: ')

if start_timer.lower() == 'y':
    print('Type N or n to break the loop')
    start = time.time()
    while start_timer.lower() != 'n':
        start_timer = input()

    end = time.time()
    print('Total loop time: {}'.format(end - start))
else:
    print('Ok, ending')
