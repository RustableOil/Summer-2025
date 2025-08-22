'''

Generate a plot of SD from the displacement output of a pykmc run;
    adapted from Liam's MSD.py script

Input Files:

    -> Displacements file (specified in config option)
    -> pykmc.out (simulation output file) to read step times

Plots:

    -> SD plot vs. time with linear fit

August 2025
Jake Boudreau

'''

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from ase.io import read

n_step = 500
n_atom = 4001

def getSD(in_file, n_atom, n_step):
    sd = np.empty((n_step), dtype=float)
    dr = np.empty((n_atom), dtype=float)
    with open(in_file, 'r') as f:
        for i in range(3):
            next(f)
        for s in range(n_step):
            print(f"reading step {s}")
            for a in range(n_atom):
                dx, dy, dz = [float(x) for x in f.readline().strip().split()]
                dr[a] = dx**2 + dy**2 + dz**2
            if s != 0:
                sd[s] = np.sum(dr[:]) + sd[s-1]
    f.close()

    return sd

def getTimes(inFile):

    with open(inFile, 'r') as f:

        for line in f:
            if line.startswith('-'):
                break

        times = np.empty((n_step))
        t_diff = np.empty((n_step))
        ea = np.empty((n_step))
        for s in range(n_step):
            newline = f.readline().strip().split()
            t_diff[s] = float(newline[1])
            t = float(newline[2])  # only take the cumulative time
            times[s] = t * 1.0e+12 # convert to ps
            if s != 0:
                ea[s] = float(newline[4])

    t_diff_avg = np.mean(t_diff)
    ea_avg = np.mean(ea)

    print(f"Average time step was {t_diff_avg}")
    print(f"Average activation energy was {ea_avg}")

    return times

def getSDFit(times, sd):

    deg = 1 # fit polynomial degree
    m, b = np.polyfit(times, sd, deg)

    return m, b

def plotSDFit(times, sd, m, b, D, out_file):

    plt.figure()

    x = times
    y = sd

    plt.plot(x, y, 'b')

    y = m * x + b

    plt.plot(x, y, 'r', label=f"D = {D:.4f} $[Å^2/ps]$")

    plt.xlabel("time [ps]")
    plt.ylabel("Square Displacement $[Å^2]$")
    plt.legend()

    plt.savefig(out_file)

    return

def getDiffusion(m):

    dim = 3 # number of system dimensions
    D = m / (2 * dim)

    print(f"Diffusion coefficient is {D} Angst.^2 ps^-1")

    return D

def main():

    in_file = "displacements.txt"
    sd = getSD(in_file, n_atom, n_step)

    in_file = "pykmc.out"
    times = getTimes(in_file)

    m, b = getSDFit(times, sd)

    D = getDiffusion(m)

    out_file = "sd-out.png"
    plotSDFit(times, sd, m, b, D, out_file)

    return

main()
