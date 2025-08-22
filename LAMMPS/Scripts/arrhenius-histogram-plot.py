'''

arrhenius-histogram-plot.py

Input parameters:
    -> System folders: The folder name where files are stored per system
    -> Indices: Per-system list of indices for each system trajectory
    -> Temperatures: Assumes that the same temperatures were tested for each system
    -> Runtimes: Per-system list of runtimes in ps; should be ordered from shortest to longest
    -> Elements: The individual elements included in each system; do not have to reflect system folder names
    -> n_atoms: Number of atoms for each constituent element in a system; stored as a dictionary
    -> dim: The number of dimensions of the system

Input files:
    -> Mean Squared Displacement files are expected to have format "<index>_msd_<element>_<runtime>ps_<temperature>.txt"

Plots generated:
    -> Arrhenius histogram: Histogram plot of the activation energies obtained over every simulation index, along with the standard error
    -> Arrhenius average: the ln(D) vs. 1/kT per an entire system with a fit that shows the activation energy and rate constant

Other Output:
    -> the Ea and ln(D0) values are echoed to stdout

Notes:
    -> Two methods are used for getting Ea and D0 estimates, and are both echoed as output.
        Method 1: Per-trajectory arrhenius analysis; fits are averaged into single values
        Method 2: ln(D) values are averaged over every trajectory; single arrhenius fit is done

    -> Values are only estimated with the longest runtime

'''

import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

system_folders = ["Ni", "NiFe", "NiFeCr"]

k = 8.6173E-5
temperatures = [700, 800, 900, 1000, 1100]
arrhenius_dependant = [1 / (k * t) for t in temperatures]
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

def getFitFromParams(x, y):
    x = sm.add_constant(x)
    fit = sm.OLS(y, x).fit()
    return fit.params

def getFitFromArray(arr):
    return getFitFromParams(np.arange(len(arr)), arr)

def plotArrheniusHistogram(system_name, arrhenius, indices):
    fig, ax = plt.subplots(figsize=(8,6))

    se = np.std(arrhenius[:, 1], ddof=1) / np.sqrt(len(indices))

    N, bins, patches = ax.hist(arrhenius[:, 1], label=f"S.E. = {se:.4f}")

    fracs = N / N.max()
    norm = colors.Normalize(fracs.min(), fracs.max())

    for thisfrac, thispatch in zip(fracs, patches):
        color = plt.cm.viridis(norm(thisfrac))
        thispatch.set_facecolor(color)

    ax.set_xlabel("Activation Energy [eV]", fontsize=14)
    ax.set_ylabel("Count", fontsize=14)
    plt.legend()

    of = f"../Plots/{system_name}/arrhenius-histogram.png"
    fig.savefig(of)
    plt.close()

    return

def plotArrheniusAverage(system_name, lnd_total_avg, arrhenius, lnd_se):
    fig, ax1 = plt.subplots()

    x = np.array(arrhenius_dependant)
    y = np.array(lnd_total_avg)

    ax1.errorbar(x, y, yerr=lnd_se, fmt='bo', mec='k')

    b, m = arrhenius

    fit_y = -m * x + b
    ax1.plot(x, fit_y, 'k--', label=f'Ea={m:.3f} eV')

    ax1.set_xlabel("$1/k_bT$ $[eV^{-1}]$")
    ax1.set_ylabel("$ln(D)$ $[Å^2 ps^{-1}]$")
    ax1.grid()
    ax1.legend()

    def inv_kT_to_T(x):
        return 1 / (x * k)

    def T_to_inv_kT(T):
        return 1 / (T * k)

    ax2 = ax1.secondary_xaxis('top', functions=(inv_kT_to_T, T_to_inv_kT))
    ax2.set_xlabel("Temperature [K]")
    ax2.set_xticks(temperatures)

    of = f"../Plots/{system_name}/arrhenius.png"
    fig.savefig(of)
    plt.close()

    return

def plotArrheniusAverageGroup(lnd_total_avg, lnd_total_se, arrhenius_avg):
    fig, ax1 = plt.subplots(figsize=(8,6))

    colors = plt.cm.tab10.colors

    x = np.array(arrhenius_dependant)

    for s, system_name in enumerate(system_folders):
        b, m = arrhenius_avg[s]

        ax1.errorbar(x, lnd_total_avg[s], yerr=lnd_total_se[s], fmt='o', color=colors[s % len(colors)], mec='k', label=f"{system_name} (Ea={m:.3f} eV)")

        fit_y = -m * x + b
        ax1.plot(x, fit_y, '--', color=colors[s % len(colors)])

    ax1.set_xlabel("$1/k_bT$ $[eV^{-1}]$")
    ax1.set_ylabel("$ln(D)$ $[Å^2 ps^{-1}]$")
    ax1.grid()
    ax1.legend()

    def inv_kT_to_T(x):
        return 1 / (x * k)

    def T_to_inv_kT(T):
        return 1 / (T * k)

    ax2 = ax1.secondary_xaxis('top', functions=(inv_kT_to_T, T_to_inv_kT))
    ax2.set_xlabel("Temperature [K]")
    ax2.set_xticks(temperatures)

    of = f"../Plots/arrhenius-group.png"
    fig.savefig(of)
    plt.close()

    return

def main():

    plt.rcParams.update({'font.size': 14})

    lnd_total_se  = np.empty((len(system_folders), len(temperatures)), dtype=float)
    lnd_total_avg = np.empty((len(system_folders), len(temperatures)), dtype=float)
    arrhenius_avg = np.empty((len(system_folders), 2), dtype=float)

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

        sd          = np.empty((len(indices), len(runtimes), len(temperatures), len(elements))  , dtype=object)
        sd_total    = np.empty((len(indices), len(runtimes), len(temperatures))                 , dtype=object)
        d_total     = np.empty((len(indices), len(runtimes), len(temperatures), 2)              , dtype=float)
        lnd_total   = np.empty((len(indices), len(runtimes), len(temperatures))                 , dtype=float)
        arrhenius   = np.empty((len(indices), 2)                                                , dtype=float)
        d0          = np.empty((len(indices))                                                   , dtype=float)

        for i, idx in enumerate(indices):
            for r, rtime in enumerate(runtimes):
                for t, temp in enumerate(temperatures):
                    for e, elem in enumerate(elements):

                        f = f"../{system_name}/{idx}_msd_{elements[e]}_{rtime}ps_{temp}.txt"
                        sd[i, r, t, e] = getParameterFromFile(f, n_atom[elem])

                    sd_total[i, r, t] = np.sum(np.stack(sd[i, r, t, :]), axis=0)

                    d_total[i, r, t] = getFitFromArray(sd_total[i, r, t])
                    if d_total[i, r, t, 1] < 0:
                        d_total[i, r, t, 1] = 1e-6

                    lnd_total[i, r, t] = np.log(d_total[i, r, t, 1])

            arrhenius[i] = getFitFromParams(arrhenius_dependant, lnd_total[i, -1, :])

        arrhenius[:, 1] *= -1   # activation energy is always > 0
        d0 = np.mean(np.exp(arrhenius[:, 0]))
        se_d0 = np.std(arrhenius[:, 0], ddof=1) / np.sqrt(len(indices))
        var_d0 = np.var(arrhenius[:, 0], ddof=1)

        ea = np.mean(arrhenius[:, 1])
        se_ea = np.std(arrhenius[:, 1], ddof=1) / np.sqrt(len(indices))
        var_ea = np.var(arrhenius[:, 1], ddof=1)

        print(f"(Method 1) {system_name} mean Arrhenius parameters: Ea = {ea:.4f} eV, SE = {se_ea:.4f}, VAR = {var_ea:.4f}, D0 = {d0:.4f}, SE = {se_d0:.4f}, VAR = {var_d0:.4f}")

        for t, temp in enumerate(temperatures):
            lnd_mean = np.mean(lnd_total[:, -1, t])
            lnd_se   = np.std(lnd_total[:, -1, t], ddof=1) / np.sqrt(len(indices))

            lnd_total_avg[system_idx, t] = lnd_mean
            lnd_total_se[system_idx, t]  = lnd_se

        x = np.array(arrhenius_dependant)
        y = lnd_total_avg[system_idx]

        arrhenius_avg[system_idx] = getFitFromParams(x, y)
        arrhenius_avg[system_idx, 1] *= -1

        d0 = np.exp(arrhenius_avg[system_idx, 0])
        ea = arrhenius_avg[system_idx, 1]

        print(f"(Method 2) {system_name} mean Arrhenius parameters: Ea = {ea:.4f} eV, D0 = {d0:.4f}")

        print(f"Plotting {system_name} Arrhenius histogram...")
        plotArrheniusHistogram(system_name, arrhenius, indices)

        print(f"Generating {system_name} Arrhenius plots...")
        plotArrheniusAverage(system_name, lnd_total_avg[system_idx], arrhenius_avg[system_idx], lnd_total_se[system_idx])

    print(f"Generating group Arrhenius plot.")

    plotArrheniusAverageGroup(lnd_total_avg, lnd_total_se, arrhenius_avg)

    return

main()
