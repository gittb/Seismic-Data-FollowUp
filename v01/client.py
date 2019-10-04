from tuning import Tuning
import usb.core
import usb.util
import time
import sounddevice as sd
import numpy as np
import socket

# now support python 3
# adding networking

#V0.1

"""
requires

sudo apt-get install libportaudio2
sounddevice
numpy
pyusb
"""



#config
addr = ("192.168.1.67", 12000)
average_val = .8


#main

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
doa_buff = []
val_buff = []
count = 0

# print dev

with sd.InputStream(device=2, channels=6) as stream:
    Mic_tuning = Tuning(dev)
    start = time.time()
    for i in range(10):
        try:
            doa_buff = []
            val_buff = []
            for i in range(20):
                val_buff.append(np.average(np.absolute(stream.read(160)[0][:, 0]) * 10))
                doa_buff.append(Mic_tuning.direction)

            if average_val < np.mean(np.array(val_buff)):
                doa_avg = np.mean(np.array(doa_buff))
                #doa_avg = (180 - doa_avg) % 380
                val_avg = np.mean(np.array(val_buff))
                message = "0" + "," + str(int(doa_avg)) + "," + str(val_avg)
                message = message.encode('utf-8')
            else:
                message = "0" + "," + "ND"
                message = message.encode('utf-8')

            client_socket.sendto(message, addr)

        except KeyboardInterrupt:
            break
print(time.time() - start)
