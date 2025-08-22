'''

pe-fit-plot.py

Input parameters:
    -> System folders: The folder name where files are stored per system
    -> Indices: Per-system list of indices for each system trajectory
    -> Temperatures: Assumes that the same temperatures were tested for each system
    -> Runtimes: Per-system list of runtimes in ps

Input files:
    -> Potential Energy files are expected to have format "<index>_pe_<runtime>ps_<temperature>.txt"

Plots generated:
    -> Ensemble of potential energy plots for each trajectory (per runtime and per temperature)
    -> Plot the fits per runtime for a given temperature

'''

import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt

system_folders = ["Ni", "NiFe", "NiFeCr"]

temperatures = [700, 800, 900, 1000, 1100]

def getParameterFromFile(filename, n_atom_consituent):
    with open(filename, "r") as f:
        next(f) # skip header line
        parameter = []
        for line in f:
            line = line.strip()
            if line != '':
                pe = float(line)
                parameter.append(pe)

    return parameter

def getFitParams(x, y):
    x = sm.add_constant(x)
    fit = sm.OLS(y, x).fit()
    return fit.params

def getFitFromArray(arr):
    return getFitParams(np.arange(len(arr)), arr)

def plotPE(pe_slice, of):
    fig, ax = plt.subplots(figsize=(9,6))

    y = np.array(pe_slice)
    x = np.arange(len(y))

    ax.plot(x, y, 'b.')

    ax.set_xlabel("Time [ps]")
    ax.set_ylabel("Potential Energy [eV]")
    ax.grid()
    fig.savefig(of)
    plt.close()

    return

def plotPEEnsemble(system_name, pe, runtimes):
    for r, rtime in enumerate(runtimes):
        for t, temp in enumerate(temperatures):
            of = f"../Plots/{system_name}/1_pe_{rtime}ps_{temp}.png"
            plotPE(pe[1, r, t], of)

    return

def plotPEFits(pe_fit_avg_per_rtime_slice, of, runtimes):
    fig, ax = plt.subplots(figsize=(8,6))

    for r, rtime in enumerate(runtimes):
        b, m = pe_fit_avg_per_rtime_slice[r]
        x = np.arange(runtimes[r])
        y = m * x + b

        ax.plot(x, y, '-')
        ax.text(x[-1], y[-1], f"RT={rtime}", va='top', ha='left', fontsize=8)

    ax.set_xlabel("Runtime (RT) [ps]")
    ax.set_ylabel("Potential Energy [eV]")
    ax.grid()
    fig.savefig(of)
    plt.close()

def plotPEFitEnsemble(system_name, pe_fit_avg_per_rtime, runtimes):
    for t, temp in enumerate(temperatures):
        of = f"../Plots/{system_name}/pe_fit_{temp}.png"
        plotPEFits(pe_fit_avg_per_rtime[:, t], of, runtimes)

def main():

    plt.rcParams.update({'font.size': 14})

    for system_idx, system_name in enumerate(system_folders):
        if system_name == "Ni":
            indices = np.arange(1, 6)
            runtimes = [5000]
        elif system_name == "NiFe":
            indices = np.arange(1, 6)
            runtimes = [100000]
        elif system_name == "NiFeCr":
            indices = np.arange(1, 6)
            runtimes = [250000]

        pe                      = np.empty((len(indices), len(runtimes), len(temperatures))                    , dtype=object)
        pe_fit                  = np.empty((len(indices), len(runtimes), len(temperatures), 2)                 , dtype=float)
        pe_fit_avg_per_rtime    = np.empty((len(runtimes), len(temperatures), 2)                               , dtype=float)

        for i, idx in enumerate(indices):
            for r, rtime in enumerate(runtimes):
                for t, temp in enumerate(temperatures):

                    f = f"../{system_name}/{idx}_pe_{rtime}ps_{temp}.txt"
                    pe[i, r, t] = getParameterFromFile(f, None)

                    pe_fit[i, r, t] = getFitFromArray(pe[i, r, t])

        for r, rtime in enumerate(runtimes):
            for t, temp in enumerate(temperatures):
                pe_fit_avg_per_rtime[r, t] = np.mean(pe_fit[:, r, t, :], axis=0)

        print(f"Plotting {system_name} PE ensemble...")

        plotPEEnsemble(system_name, pe, runtimes)

        print(f"Plotting {system_name} PE fits per runtime...")

        plotPEFitEnsemble(system_name, pe_fit_avg_per_rtime, runtimes)

    return

main()

