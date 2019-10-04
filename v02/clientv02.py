from tuning import Tuning
import usb.core
import usb.util
import time
import sounddevice as sd
import numpy as np
import socket

# now support python 3
# adding networking

#v0.2

"""
requires

sudo apt-get install libportaudio2
sounddevice
numpy
pyusb
"""


"""
Notes:
- only operates in 180 mode
- uses voice detection instead of audio value
- numpy arrays from start

- would run with more iterations but looping (and prob just the averaging of large arrays) seems to take forever on the 
    pi's
"""

#config
addr = ("192.168.1.67", 12000)
average_val = .8
device_id = "1"


#main

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

with sd.InputStream(device=2, channels=6) as stream:
    Mic_tuning = Tuning(dev)
    start = time.time()
    while True:
        try:
            doa_buff = []
            count = 0
            for _ in range(16):

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
print(time.time() - start)
