import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

path = r'C:\Users\lw390\OneDrive\Documents\物流自动化技术\货架vs叉车'

racks = [i for i in range(4, 11)]
forks = [i for i in range(2, 6)]
times = np.zeros((len(racks)+4, len(forks)+2))

for rack in racks:
    for fork in forks:
        with open(path + '\\' + '100_' + str(fork) + '_' + str(rack) + '.txt', 'r') as fh:
            times[rack, fork] = (np.mean(np.array([t.split(' ')[0] for t in fh.readlines()], dtype=int)))

fig = plt.figure()
ax = Axes3D(fig)
X, Y = np.meshgrid(racks, forks)
ax.plot_surface(X, Y, times[4:, 2:].T, rstride=1, cstride=1, cmap='rainbow')
ax.set_xlabel('rack')
ax.set_ylabel('fork')
ax.set_zlabel('time consumption (s)')
ax.set_title('Rack vs Fork with 100 pallet')

plt.show()
