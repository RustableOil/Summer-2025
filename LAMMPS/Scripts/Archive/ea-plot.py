"""

Open a column-based list of activation energy (Ea) and rate constant (D0)
values for certain systems, then plot the results using the Arrhenius
expressions. Export the plots as png files when finished.

"""

import numpy as np
import matplotlib.pyplot as plt

systems = ["Ni", "NiFe", "NiFeCr"]
nSys = len(systems)
nRun = 25

def importParams(sysId):

    inf = "./system_d0_ea_" + systems[sysId] + ".txt"  # input file

    with open(inf, 'r') as f:

        nRun = int(f.readline())

        d0_ea = []
        for line in range(nRun):
            newline = f.readline().split()
            d0 = newline[1]
            ea = newline[2]
            d0_ea.append([d0, ea])

    f.close()

    return d0_ea

def plot(d0_ea, sysId):

    plt.figure()

    plt.hist(d0_ea[:,1])    # Ea histogram

    plt.savefig('ea_hist-' + systems[sysId] + '.png')

    return

def exportIMG():
    return

system_params = np.empty((nSys, nRun, 2))

for sysId in range(nSys):

    system_params[sysId] = importParams(sysId)

    plot(system_params[sysId], sysId)
