'''

sd-contribution-plot.py

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
    -> Ensemble of SD plots vs. time for every trajecotry in the system
    -> Plot of individual element contributions to the final cumulative SD of each trajectory

Notes:
    -> Element contribution plots are only generated using the longest runtime
    -> (Aside) Plotting are on a log scale better shows elements that contribute very little to diffusion

'''

import numpy as np
import matplotlib.pyplot as plt

system_folders = ["Ni", "NiFe", "NiFeCr"]

temperatures = [700, 800, 900, 1000, 1100]

dim = 3

def getParameterFromFile(filename, n_atom_consituent):
    with open(filename, "r") as f:
        next(f) # skip header line
        next(f) # skip tiny first value
        initial_jump = float(f.readline())  # normalize each reading
        parameter = []
        for line in f:
            line = line.strip()
            if line != '':
                msd = float(line)
                sd = (msd - initial_jump) / (2 * dim) * n_atom_consituent
                parameter.append(sd)
    return parameter

def getPlotStyle(elem):
    if elem == "Ni":
        return 'g'
    elif elem == "Fe":
        return 'r'
    elif elem == "Cr":
        return 'b'
    else:
        return 'k'

def plotElementSD(sd_slice, of, elements):
    fig, ax = plt.subplots(figsize=(10,6))

    for e, elem in enumerate(elements):
        style = getPlotStyle(elem)

        y = np.array(sd_slice[e])
        x = np.arange(len(y))

        ax.plot(x, y, style, label=elem)

    ax.set_xlabel("Time [ps]")
    ax.set_ylabel("Squared Displacement $[Å^2]$")
    ax.legend()
    ax.grid()
    fig.savefig(of)
    plt.close()

    return

def plotSDEnsemble(system_name, sd, runtimes, elements):

    for r, rtime in enumerate(runtimes):
        for t, temp in enumerate(temperatures):
            of = f"../Plots/{system_name}/1_msd_{rtime}ps_{temp}.png"
            plotElementSD(sd[1, r, t], of, elements)

    return

def plotSDElementContribution(system_name, sd_percent_contributions_avg, elements):
    fig, ax = plt.subplots()

    x = temperatures

    for e, elem in enumerate(elements):
        style = getPlotStyle(elem)

        y = sd_percent_contributions_avg[:, e]

        ax.plot(x, y, style, label=elem)

    ax.set_xlabel("Temperature [K]")
    ax.set_xticks(temperatures)
    ax.set_ylabel("Displacement Percent Contribution [%]")
    ax.legend()
    ax.grid()

    of = f"../Plots/{system_name}/sd-element-contributions.png"
    fig.savefig(of)
    plt.close()

    return

def main():

    plt.rcParams.update({'font.size': 14})

    for system_idx, system_name in enumerate(system_folders):

        if system_name == "Ni":
            elements = ["Ni"]
            n_atom = {'Ni': 2049}
            indices = np.arange(1, 6)
            runtimes = [5000]
        elif system_name == "NiFe":
            elements = ["Ni", "Fe"]
            n_atom = {'Ni': 756, 'Fe': 1293}
            indices = np.arange(1, 6)
            runtimes = [100000]
        elif system_name == "NiFeCr":
            elements = ["Ni", "Fe", "Cr"]
            n_atom = {'Ni': 1511, 'Fe': 218, 'Cr': 320}
            indices = np.arange(1, 6)
            runtimes = [250000]

        sd                              = np.empty((len(indices), len(runtimes), len(temperatures), len(elements))     , dtype=object)
        sd_total                        = np.empty((len(indices), len(runtimes), len(temperatures))                    , dtype=object)
        sd_percent_contributions        = np.empty((len(indices), len(runtimes), len(temperatures), len(elements))     , dtype=object)
        sd_percent_contributions_avg    = np.empty((len(temperatures), len(elements))                                  , dtype=object)

        for i, idx in enumerate(indices):
            for r, rtime in enumerate(runtimes):
                for t, temp in enumerate(temperatures):
                    for e, elem in enumerate(elements):
                        f = f"../{system_name}/{idx}_msd_{elements[e]}_{rtime}ps_{temp}.txt"
                        sd[i, r, t, e] = getParameterFromFile(f, n_atom[elem])

                    sd_total[i, r, t] = np.sum(np.stack(sd[i, r, t, :]), axis=0)

                    for e, elem in enumerate(elements):
                        sd_slice = sd[i, r, t, e]
                        sd_slice_total = sd_total[i, r, t]

                        sd_percent_contributions[i, r, t, e] = sd_slice[-1] / sd_slice_total[-1] * 100

        for t, temp in enumerate(temperatures):
            sd_percent_contributions_avg[t] = np.mean(sd_percent_contributions[:, -1, t, :], axis=0)

        print(f"Plotting {system_name} SD ensemble...")

        plotSDEnsemble(system_name, sd, runtimes, elements)

        print(f"Plotting {system_name} element contributions...")

        plotSDElementContribution(system_name, sd_percent_contributions_avg, elements)

    return

main()
