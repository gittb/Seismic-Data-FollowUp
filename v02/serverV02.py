import socket
import numpy as np
import matplotlib.pyplot as plt
import time
import select

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 12000))

"""
Notes:
- do not locate if either sensor is over 180
- maybe detect only if voice is detected and not by audio magnitude (more dynamic)
- UDP stream similar to sending audio over network maybe
"""


timeout = 0.001

sig_ttl = 1
distance_between = 4  # in feet
plt.axis([-8, 8, -2, 10])
plt.gca().invert_yaxis()

num_units = 2
units = {}
for n in range(num_units):
    units[n] = {
        "doa" : -1,
        "mag" : 'na',
        "ttl" : 0
    }

run = False

server_socket.setblocking(0)


while True:

    ready = select.select([server_socket], [], [], timeout)

    if ready[0]:
        message = server_socket.recv(150)

        vals = message.decode('utf-8').split(',')
        id = int(vals[0])
        if run:
            #populate dict
            if len(vals) == 2:
                #check if no detection
                if units[id]['ttl'] > 0:
                    units[id]['ttl'] = units[id]['ttl'] - 1
                else:
                    units[id]['doa'] = -1
                    units[id]['mag'] = 'na'
            else:
                #populate if detection
                units[id]['doa'] = int(vals[1])
                units[id]['mag'] = 'na'
                units[id]['ttl'] = sig_ttl

            #check if sync det within ttl
            if (units[0]['ttl'] > 0 and units[1]['ttl'] > 0):
                print("Unit 0:", units[0], "Unit 1:", units[1])
                #  triangle quick maths
                ang_a = np.deg2rad(units[0]['doa'])
                ang_b = np.deg2rad(units[1]['doa']) #taken care of client side
                ang_c = np.deg2rad(180 - (units[0]['doa'] + units[1]['doa']))
                side_a = ((np.sin(ang_a)/np.sin(ang_c)) * distance_between)
                side_b = ((np.sin(ang_b)/np.sin(ang_c)) * distance_between)

                # position based on unit 1
                x = side_a * np.cos(ang_b)
                y = side_a * np.sin(ang_b)

                #print("Unit 0:", units[0], "Unit 1:", units[1], (180 - (ang_a + ang_b)))
                #print("sides:", side_a, side_b)
                print("Voice | DOA live :", x, y)
                plt.scatter(x, y)
                plt.pause(0.005)
                units[0]['ttl'] = 0
                units[1]['ttl'] = 0
        else:
            print(vals)

print(time.time() - start)