'''

Check what expected diffusion of system should be for given Arrhenius parameters and temperature

August 2025
Jake Boudreau

'''

import numpy as np
import matplotlib.pyplot as plt

k = 8.6173e-5

def main():

    # Known input Arrhenius parameters
    d0 = 21.4066
    ea = 0.3031

    # Testing temperature [K]
    T = [100, 700, 800, 900, 1000, 1100]
    arrhenius_dependant = [1 / (k * t) for t in T]

    lnd0 = np.log(d0)
    lnd = np.empty((len(T)))
    for i in range(len(arrhenius_dependant)):
        lnd[i] = lnd0 - (ea * arrhenius_dependant[i])

    d = np.exp(lnd[0])

    plt.plot(arrhenius_dependant, lnd)

    plt.savefig("plot-check.png")

    print(f"Diffusion coefficient estimate is {d} Angst.^2 ps^-1")

    return

main()
