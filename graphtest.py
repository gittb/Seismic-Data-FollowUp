import numpy as np
import matplotlib.pyplot as plt
import time

plt.axis([-10, 10, 0, 20])

for i in range(10):
    y = np.random.random()

    time.sleep(1)

plt.show()

