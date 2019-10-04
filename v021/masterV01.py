from tuning import Tuning
import usb.core
import usb.util
import time
import sounddevice as sd
import numpy as np
import socket
from multiprocessing import Process
import select

"""
master

combination of client and server sending only X and Y to main collection server
- requires newer pi
"""

#v0.1


#client config
addr = ("", 12000)
device_id = "0"
buffer_size = 10

#serv config
server_addr = ("192.168.1.67", 12000)
team_id = 'bonksquad'




def loc_serv(addr, team_id, timeout=0.001):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('', 12000))

    """
    slim serv for inter-team processing
    """

    sig_ttl = 1
    distance_between = 4  # in feet
    num_units = 2
    units = {}

    for n in range(num_units):
        units[n] = {
            "doa": -1,
            "mag": 'na',
            "ttl": 0
        }

    server_socket.setblocking(0)

    while True:
        ready = select.select([server_socket], [], [], timeout)

        if ready[0]:
            message = server_socket.recv(2000)

            vals = message.decode('utf-8').split(',')
            id = int(vals[0])
            # populate dict
            if len(vals) == 2:
                # check if no detection
                if units[id]['ttl'] > 0:
                    units[id]['ttl'] = units[id]['ttl'] - 1
                else:
                    units[id]['doa'] = -1
                    units[id]['mag'] = 'na'
            else:
                # populate if detection
                units[id]['doa'] = int(vals[1])
                units[id]['mag'] = 'na'
                units[id]['ttl'] = sig_ttl

            # check if sync det within ttl
            if (units[0]['ttl'] > 0 and units[1]['ttl'] > 0):
                print("Source located:", "Unit 0:", units[0], "Unit 1:", units[1])
                #  triangle quick maths
                ang_a = np.deg2rad(units[0]['doa'])
                ang_b = np.deg2rad(units[1]['doa'])  # taken care of client side
                ang_c = np.deg2rad(180 - (units[0]['doa'] + units[1]['doa']))
                side_a = ((np.sin(ang_a) / np.sin(ang_c)) * distance_between)
                side_b = ((np.sin(ang_b) / np.sin(ang_c)) * distance_between)

                # position based on unit 1
                x = side_a * np.cos(ang_b)
                y = side_a * np.sin(ang_b)
                cords = (team_id + "," + str(x) + "," + str(y))
                cords = cords.encode('utf-8')
                server_socket.sendto(message, addr)
                units[0]['ttl'] = 0
                units[1]['ttl'] = 0


serv_process = Process(target=loc_serv, args=(server_addr, team_id))
serv_process.daemon = True
serv_process.start()


#main

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

Mic_tuning = Tuning(dev)

start = time.time()
while True:
    try:
        doa_buff = []
        count = 0
        for _ in range(buffer_size):

            if device_id == "0":
                doa = Mic_tuning.direction
            else:
                doa = (180 - Mic_tuning.direction) % 380
            v_det = Mic_tuning.is_voice()
            if v_det == 1 and 1 < doa < 179:
                doa_buff.append(doa)

        if len(doa_buff):
            doa_avg = np.mean(np.array(doa_buff))
            val_avg = 'na'
            message = device_id + "," + str(int(doa_avg)) + "," + str(val_avg)
            message = message.encode('utf-8')
        else:
            message = device_id + "," + "ND"
            message = message.encode('utf-8')

        client_socket.sendto(message, addr)

    except KeyboardInterrupt:
        break