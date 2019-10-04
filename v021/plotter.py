import socket
import numpy as np
import matplotlib.pyplot as plt
import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 12000))

"""
Notes:
- slim main server rec
"""

plt.axis([-8, 8, -2, 10])
plt.gca().invert_yaxis()



"""

input = [12,4,5,2,6,12,56,235,6,76,36,254]

f(input) => [12,412,5,2]


"""


run = True

while True:

    message = server_socket.recv(2000)

    vals = message.decode('utf-8').split(',')
    print(message)
    if run:
        x = float(vals[1])
        y = float(vals[2])
        plt.scatter(x, y)
        plt.pause(0.005)
