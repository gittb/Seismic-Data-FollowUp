from tuning import Tuning
import usb.core
import usb.util
import time
import numpy as np
import socket
import sounddevice as sd

# now support python 3
# adding networking

#v0.21

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

TODO:
ground truth with HTC vive
Adjust tuning to get optimal performance

- would run with more iterations but looping (and prob just the averaging of large arrays) seems to take forever on the 
    pi's
"""

#config
addr = ("192.168.1.113", 12000)
device_id = "1"
buffer_size = 5


def sendmessage(device_id, doa_buff, val_buff=False):
    if len(doa_buff):
        doa_avg = np.mean(np.array(doa_buff))
        if val_buff:
            val_avg = np.mean(np.array(val_buff))
        else:
            val_avg = 'na'
        message = device_id + "," + str(int(doa_avg)) + "," + str(val_avg)
        message = message.encode('utf-8')
    else:
        message = device_id + "," + "ND"
        message = message.encode('utf-8')

    client_socket.sendto(message, addr)




#main

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)


Mic_tuning = Tuning(dev)
start = time.time()
with sd.InputStream(device=2, channels=6) as stream:
    for _ in range(10):
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
            print(stream.read_available)
            audio = stream.read(160)[0][:, 0]
            sendmessage(device_id, doa_buff)

        except KeyboardInterrupt:
            break
print(time.time() - start)
