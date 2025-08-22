'''

diffusion-convergence-plot.py

Input parameters:
    -> System folders: The folder name where files are stored per system
    -> Indices: Per-system list of indices for each system trajectory
    -> Temperatures: Assumes that the same temperatures were tested for each system
    -> Runtimes: Per-system list of runtimes in ps
    -> Elements: The individual elements included in each system; do not have to reflect system folder names
    -> n_atoms: Number of atoms for each constituent element in a system; stored as a dictionary
    -> dim: The number of dimensions of the system

Input files:
    -> Mean Squared Displacement files are expected to have format "<index>_msd_<element>_<runtime>ps_<temperature>.txt"

Plots generated:
    -> Diffusion Convergence: Per-system diffusion coefficient vs. total simulation runtime
        individual fit for each temperature

'''

import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt

system_folders = ["Ni", "NiFe", "NiFeCr"]
temperatures = [700, 800, 900, 1000, 1100]

dim = 3

def getParameterFromFile(filename, n_atom_consituent):
    with open(filename, "r") as f:
        next(f) # skip header line
        next(f) # skip tiny first value
        initial_jump = float(f.readline())  # to normalize each reading
        parameter = []
        for line in f:
            line = line.strip()
            if line != '':
                msd = float(line)
                sd = (msd - initial_jump) / (2 * dim) * n_atom_consituent
                parameter.append(sd)
    return parameter

def getFitParams(x, y):
    x = sm.add_constant(x)
    fit = sm.OLS(y, x).fit()
    return fit.params

def getFitFromArray(arr):
    return getFitParams(np.arange(len(arr)), arr)

def plotDiffusionConvergence(system_name, runtimes, d_total_avg_per_rtime):
    fig, ax = plt.subplots(figsize=(8,6))

    x = runtimes

    for t, temp in enumerate(temperatures):
        y = d_total_avg_per_rtime[:, t, 1]

        ax.plot(x, y)
        ax.text(x[-1], y[-1], f"T={temp}", va='top', ha='center', fontsize=8)

    ax.set_xlabel("Runtime [ps]")
    ax.set_ylabel("Difusion Coefficient $[Å^2 ps^{-1}]$")
    ax.grid()

    of = f"../Plots/{system_name}/diffusion-convergence.png"
    fig.savefig(of)
    plt.close()

    return

def main():

    for system_idx, system_name in enumerate(system_folders):

        if system_name == "Ni":
            elements = ["Ni"]
            n_atom = {'Ni': 2049}
            indices = np.arange(1, 6)
            runtimes = [5000]
        elif system_name == "NiFe":
            elements = ["Ni", "Fe"]
            n_atom = {'Ni': 756, 'Fe': 1293}
            runtimes = [100000]
            indices = np.arange(1, 6)
        elif system_name == "NiFeCr":
            elements = ["Ni", "Fe", "Cr"]
            n_atom = {'Ni': 1511, 'Fe': 218, 'Cr': 320}
            runtimes = [250000]
            indices = np.arange(1, 6)

        sd                              = np.empty((len(indices), len(runtimes), len(temperatures), len(elements))     , dtype=object)
        sd_total                        = np.empty((len(indices), len(runtimes), len(temperatures))                    , dtype=object)
        d_total                         = np.empty((len(indices), len(runtimes), len(temperatures), 2)                 , dtype=float)
        d_total_avg_per_rtime           = np.empty((len(runtimes), len(temperatures), 2)                               , dtype=float)

        for i, idx in enumerate(indices):
            for r, rtime in enumerate(runtimes):
                for t, temp in enumerate(temperatures):
                    for e, elem in enumerate(elements):
                        f = f"../{system_name}/{idx}_msd_{elements[e]}_{rtime}ps_{temp}.txt"
                        sd[i, r, t, e] = getParameterFromFile(f, n_atom[elem])

                    sd_total[i, r, t] = np.sum(np.stack(sd[i, r, t, :]), axis=0)

                    d_total[i, r, t] = getFitFromArray(sd_total[i, r, t])

        for r, rtime in enumerate(runtimes):
            for t, temp in enumerate(temperatures):
                d_total_avg_per_rtime[r, t] =  np.mean(d_total[:, r, t, :], axis=0)

        print(f"Plotting {system_name} diffusion convergence...")

        plotDiffusionConvergence(system_name, runtimes, d_total_avg_per_rtime)

    return

main()
